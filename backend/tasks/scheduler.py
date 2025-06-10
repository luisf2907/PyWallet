"""
Agendador de tarefas para o backend do PyWallet
"""
import time
import threading
from datetime import datetime, timedelta
import pytz
import os
import random
import atexit
import uuid
import sys
import logging

from flask import Flask
from services.price_service import update_price_cache_for_all_tickers, get_cached_dollar_rate
from services.dividend_service import update_dividends_cache_for_all_users
from utils.market_utils import is_market_open
from utils.cache_utils import is_rate_limited, handle_rate_limit, reset_rate_limit
from extensions.database import execute_with_retry, db
from models.price import PriceCache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pywallet.scheduler")

# Detectar se está rodando no reloader do Flask
# WERKZEUG_RUN_MAIN == 'true' indica processo principal do Flask
# Se for None ou diferente de 'true', é o processo reloader
is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'

# Flag para controlar se as threads já estão rodando
threads_started = False

# ID único desta instância para evitar inicializações duplicadas em reloads
instance_id = str(uuid.uuid4())

# Controle de última atualização para evitar atualizações muito frequentes
last_price_update_time = datetime.now() - timedelta(hours=1)

# Lista de tickers que foram marcados como "delisted" e devem ser ignorados
delisted_tickers = set()

# Número de workers configurável via env ou padrão 6
NUM_WORKERS = int(os.getenv("PYWALLET_PRICE_THREADS", 6))
# Intervalo de atualização em minutos (padrão: 10)
UPDATE_INTERVAL_MINUTES = int(os.getenv("PYWALLET_PRICE_UPDATE_MINUTES", 10))

scheduler = None

# Função para atualizar preços com remoção de tickers "possibly delisted"
def update_prices_with_delisted_handling(app=None):
    """
    Atualiza preços e remove tickers marcados como "possibly delisted"
    """
    from models.portfolio import Portfolio
    import json
    import traceback
    
    global last_price_update_time
    
    # Verifica se já atualizou recentemente (menos de 25 minutos atrás)
    now = datetime.now()
    if (now - last_price_update_time).total_seconds() < 30:  # 30 segundos para evitar requests duplicados
        print(f"[PRICECACHE] Última atualização foi há {(now - last_price_update_time).total_seconds() / 60:.1f} minutos. Pulando atualização.")
        return
    
    print(f"[PRICECACHE] Iniciando atualização de preços (última atualização: {(now - last_price_update_time).total_seconds() / 60:.1f} minutos atrás).")
    
    # Atualizaremos o timestamp somente após sucesso na atualização
    # Isso permite uma nova tentativa caso a anterior falhe
    
    # Se todos os tickers derem erro, pode ser rate limit
    all_tickers_failed = False
    
    try:
        # Passa o app explicitamente para garantir contexto nas threads
        from flask import current_app
        result = update_price_cache_for_all_tickers(app=app or current_app)
        
        # Somente atualiza o timestamp se recebemos um resultado válido
        if result is not None:
            last_price_update_time = now
            print(f"[PRICECACHE] Atualização concluída com sucesso às {now.strftime('%H:%M:%S')}")
        
        # Verificar se temos tickers com erro "possibly delisted"
        if hasattr(result, 'delisted_tickers') and result.delisted_tickers:
            # Se todos os tickers falharam, provavelmente é rate limit
            if result.total_tickers > 0 and len(result.delisted_tickers) == result.total_tickers:
                print("[RATE LIMIT] Todos os tickers falharam, possível rate limit. Não removendo tickers.")
                all_tickers_failed = True
                return
                
            # Caso contrário, podemos remover os tickers delisted
            if not all_tickers_failed and result.delisted_tickers:
                # Adiciona à lista global de delisted
                for ticker in result.delisted_tickers:
                    delisted_tickers.add(ticker)
                    
                # Remove do banco de dados
                for ticker in result.delisted_tickers:
                    print(f"[DELISTED] Removendo ticker {ticker} marcado como 'possibly delisted'")
                    try:
                        PriceCache.query.filter_by(ticker=ticker).delete()
                    except Exception as e:
                        print(f"[ERROR] Erro ao remover ticker {ticker}: {e}")
                
                # Commit das alterações
                db.session.commit()
                print(f"[DELISTED] {len(result.delisted_tickers)} tickers removidos do cache")
    except Exception as e:
        print(f"[ERROR] Erro ao atualizar preços com tratamento de delisted: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        # Não atualiza o timestamp em caso de erro

def schedule_dividends_update(app):
    """
    Thread para atualização diária de dividendos (10:30 da manhã).
    """
    tz = pytz.timezone('America/Sao_Paulo')
    time.sleep(random.uniform(3, 10))
    last_update_date = datetime.now(tz).date() - timedelta(days=1)
    while True:
        now = datetime.now(tz)
        if now.date() == last_update_date:
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))
            continue
        target_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= target_time:
            try:
                print('[DIVIDENDS] Atualização diária programada iniciada.')
                with app.app_context():
                    execute_with_retry(update_dividends_cache_for_all_users)
                    last_update_date = now.date()
            except Exception as e:
                print(f'[DIVIDENDS] Erro na atualização diária programada: {e}')
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))
        else:
            sleep_seconds = (target_time - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 60:.1f} minutos")
            time.sleep(min(sleep_seconds, 1800))

def schedule_prices_update(app):
    """
    Thread para atualização diária de preços (18:00 em dias úteis).
    """
    tz = pytz.timezone('America/Sao_Paulo')
    time.sleep(random.uniform(5, 15))
    while True:
        now = datetime.now(tz)
        # Só roda em dias úteis (segunda a sexta)
        if now.weekday() < 5:
            next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)
                
            # Pular finais de semana
            while next_run.weekday() >= 5:
                next_run += timedelta(days=1)
                
            sleep_seconds = (next_run - now).total_seconds()
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
                
            try:
                print('[PRICECACHE] Atualização diária programada iniciada.')
                with app.app_context():
                    execute_with_retry(lambda: update_price_cache_for_all_tickers(app=app))
            except Exception as e:
                print(f'[PRICECACHE] Erro na atualização diária programada: {e}')
                
            # Garante que só rode uma vez por dia
            time.sleep(60)
        else:
            # Se for final de semana, dorme até segunda
            next_weekday = now + timedelta(days=(7 - now.weekday()))
            next_run = next_weekday.replace(hour=18, minute=0, second=0, microsecond=0)
            sleep_seconds = (next_run - now).total_seconds()
            time.sleep(sleep_seconds)

def update_all_portfolios(app):
    """
    Configura e inicia o scheduler para atualização de preços a cada 30 minutos em horários fixos.
    Esta versão usa APScheduler em vez de threads para maior resiliência.
    """
    logger.info("Configurando APScheduler para atualização periódica de preços")
    
    # Cria um scheduler dedicado para as atualizações a cada 30 minutos
    executors = {
        'default': ThreadPoolExecutor(1),  # Só 1 job de atualização por vez
    }
    portfolio_scheduler = BackgroundScheduler(executors=executors, timezone="America/Sao_Paulo")
    
    # Função que será executada a cada 30 minutos
    def portfolio_update_job():
        try:
            current_time = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
            logger.info(f"[SCHEDULER] Atualização periódica de preços iniciada às {current_time}")
            print(f"[SCHEDULER] Atualização periódica de preços iniciada às {current_time}")
            
            with app.app_context():
                update_prices_with_delisted_handling(app=app)
        except Exception as e:
            logger.error(f"[ERROR] Erro na atualização periódica de preços: {e}")
            print(f"[ERROR] Erro na atualização periódica de preços: {e}")
    
    # Configura o job para executar a cada 30 minutos (nos minutos 0 e 30 de cada hora)
    portfolio_scheduler.add_job(
        portfolio_update_job,
        trigger='cron',
        minute='0,30',  # Executa em XX:00 e XX:30
        id="portfolio_price_update_job",
        max_instances=1,
        replace_existing=True,
        coalesce=True,
    )
    
    # Inicia o scheduler
    portfolio_scheduler.start()
    
    # Registra no atexit para desligar corretamente
    atexit.register(lambda: portfolio_scheduler.shutdown() if portfolio_scheduler.running else None)
    
    # Calcula e imprime próxima execução
    next_run = portfolio_scheduler.get_jobs()[0].next_run_time
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    logger.info(f"[SCHEDULER] Próxima atualização de preços em {(next_run - now).total_seconds()/60:.1f} minutos (às {next_run.strftime('%H:%M')})")
    print(f"[SCHEDULER] Próxima atualização de preços em {(next_run - now).total_seconds()/60:.1f} minutos (às {next_run.strftime('%H:%M')})")
      # Executa uma vez na inicialização se a última atualização for muito antiga (mais de 25 minutos)
    # Certifica-se que last_price_update_time tenha timezone
    last_update_with_tz = last_price_update_time
    if last_update_with_tz.tzinfo is None:
        last_update_with_tz = pytz.timezone('America/Sao_Paulo').localize(last_update_with_tz)
        
    time_diff_seconds = (now - last_update_with_tz).total_seconds()
    
    if time_diff_seconds > (25 * 60):  # 25 minutos
        logger.info(f"[SCHEDULER] Executando atualização imediata (última foi há {time_diff_seconds / 60:.1f} minutos)")
        print(f"[SCHEDULER] Executando atualização imediata (última foi há {time_diff_seconds / 60:.1f} minutos)")
        portfolio_update_job()

def cleanup():
    """Função de limpeza chamada quando o processo termina"""
    print(f"[SCHEDULER] Limpando recursos da instância {instance_id}")

def start_scheduled_tasks(app):
    """
    Inicia todas as tarefas agendadas em threads separadas.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    global threads_started, last_price_update_time

    # Removida checagem de threads_started e is_reloader para sempre iniciar as threads
    # Registra função de limpeza
    atexit.register(cleanup)

    with app.app_context():
        print(f"Inicializando tarefas agendadas (instância {instance_id})...")
        try:
            now = datetime.now()
            if (now - last_price_update_time).total_seconds() > 600:
                def async_price_update():
                    with app.app_context():
                        try:
                            print("[SCHEDULER] Iniciando atualização de preços em segundo plano...")
                            execute_with_retry(lambda: update_prices_with_delisted_handling(app=app))
                            print("[SCHEDULER] Atualização de preços em segundo plano concluída.")
                        except Exception as e:
                            print(f"[SCHEDULER] Erro na atualização de preços em segundo plano: {e}")
                price_thread = threading.Thread(target=async_price_update, daemon=True)
                price_thread.start()
            else:
                print(f"[SCHEDULER] Última atualização de preços foi há {(now - last_price_update_time).total_seconds() / 60:.1f} minutos. Pulando atualização inicial.")
            def async_dividend_update():
                with app.app_context():
                    try:
                        print("[SCHEDULER] Iniciando atualização de dividendos em segundo plano...")
                        execute_with_retry(update_dividends_cache_for_all_users)
                        print("[SCHEDULER] Atualização de dividendos em segundo plano concluída.")
                    except Exception as e:
                        print(f"[SCHEDULER] Erro na atualização de dividendos em segundo plano: {e}")
            dividend_thread = threading.Thread(target=async_dividend_update, daemon=True)
            dividend_thread.start()
        except Exception as e:
            print(f"[SCHEDULER] Erro durante inicialização das tarefas: {e}")
        updater_thread = threading.Thread(target=lambda: update_all_portfolios(app), daemon=True)
        updater_thread.start()
        dividends_thread = threading.Thread(target=lambda: schedule_dividends_update(app), daemon=True)
        dividends_thread.start()
        prices_thread = threading.Thread(target=lambda: schedule_prices_update(app), daemon=True)
        prices_thread.start()
        threads_started = True
        print(f"Tarefas agendadas iniciadas com sucesso! (instância {instance_id})")

def start_scheduler(app):
    global scheduler
    if scheduler is not None:
        logger.info("Scheduler já está rodando.")
        return

    logger.info(f"Iniciando scheduler com {NUM_WORKERS} threads e intervalo de {UPDATE_INTERVAL_MINUTES} minutos.")
    executors = {
        'default': ThreadPoolExecutor(1),  # Só 1 job de atualização por vez
    }
    scheduler = BackgroundScheduler(executors=executors, timezone="UTC")

    def job_wrapper():
        logger.info(f"[SCHEDULER] Iniciando atualização de preços: {datetime.now()}")
        start = datetime.now()
        try:
            with app.app_context():
                # Passa o número de workers para a função de atualização
                update_price_cache_for_all_tickers(app=app, num_workers=NUM_WORKERS)
            logger.info(f"[SCHEDULER] Atualização de preços concluída em {datetime.now() - start}.")
        except Exception as e:
            logger.error(f"[SCHEDULER] Erro na atualização de preços: {e}")

    scheduler.add_job(
        job_wrapper,
        trigger=IntervalTrigger(minutes=UPDATE_INTERVAL_MINUTES),
        id="price_update_job",
        max_instances=1,
        replace_existing=True,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado.")

def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler finalizado.")
        scheduler = None
