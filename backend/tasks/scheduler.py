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

from flask import Flask
from services.price_service import update_price_cache_for_all_tickers, get_cached_dollar_rate
from services.dividend_service import update_dividends_cache_for_all_users
from utils.market_utils import is_market_open
from utils.cache_utils import is_rate_limited, handle_rate_limit, reset_rate_limit
from extensions.database import execute_with_retry, db
from models.price import PriceCache

# Flag para controlar se as threads já estão rodando
threads_started = False

# ID único desta instância para evitar inicializações duplicadas em reloads
instance_id = str(uuid.uuid4())

# Controle de última atualização para evitar atualizações muito frequentes
last_price_update_time = datetime.now() - timedelta(hours=1)

# Lista de tickers que foram marcados como "delisted" e devem ser ignorados
delisted_tickers = set()

# Função para atualizar preços com remoção de tickers "possibly delisted"
def update_prices_with_delisted_handling():
    """
    Atualiza preços e remove tickers marcados como "possibly delisted"
    """
    from models.portfolio import Portfolio
    import json
    
    global last_price_update_time
    
    # Verifica se já atualizou recentemente (menos de 25 minutos atrás)
    now = datetime.now()
    if (now - last_price_update_time).total_seconds() < 1500:  # 25 minutos em segundos
        print(f"[PRICECACHE] Última atualização foi há {(now - last_price_update_time).total_seconds() / 60:.1f} minutos. Pulando atualização.")
        return
    
    print(f"[PRICECACHE] Iniciando atualização de preços (última atualização: {(now - last_price_update_time).total_seconds() / 60:.1f} minutos atrás).")
    
    # Atualiza o tempo da última atualização ANTES de começar para evitar múltiplas atualizações simultâneas
    last_price_update_time = now
        
    # Se todos os tickers derem erro, pode ser rate limit
    all_tickers_failed = False
    
    try:
        # Primeira tentativa de atualização normal
        result = update_price_cache_for_all_tickers()
        
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

def schedule_dividends_update():
    """
    Thread para atualização diária de dividendos (10:30 da manhã).
    """
    tz = pytz.timezone('America/Sao_Paulo')
    
    # Captura a referência da aplicação Flask do módulo principal
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.app import app as flask_app
    
    # Adiciona jitter (atraso aleatório) para evitar colisão com outras threads
    time.sleep(random.uniform(3, 10))
    
    # Variável para controlar última atualização
    last_update_date = datetime.now(tz).date() - timedelta(days=1)
    
    while True:
        now = datetime.now(tz)
        
        # Verifica se já atualizou hoje
        if now.date() == last_update_date:
            # Já atualizou hoje, espera até amanhã
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))  # Dorme no máximo 1 hora para poder verificar novamente
            continue
        
        # Verifica se já passou do horário de hoje
        target_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= target_time:
            try:
                print('[DIVIDENDS] Atualização diária programada iniciada.')
                with flask_app.app_context():
                    # Usando o sistema de retry
                    execute_with_retry(update_dividends_cache_for_all_users)
                    # Marca que atualizou hoje
                    last_update_date = now.date()
            except Exception as e:
                print(f'[DIVIDENDS] Erro na atualização diária programada: {e}')
            
            # Aguarda até o próximo dia
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))  # Dorme no máximo 1 hora para poder verificar novamente
        else:
            # Ainda não chegou a hora hoje, espera até a hora
            sleep_seconds = (target_time - now).total_seconds()
            print(f"[DIVIDENDS] Próxima atualização em {sleep_seconds / 60:.1f} minutos")
            time.sleep(min(sleep_seconds, 1800))  # Dorme no máximo 30 minutos para poder verificar novamente

def schedule_prices_update():
    """
    Thread para atualização diária de preços (18:00 em dias úteis).
    """
    tz = pytz.timezone('America/Sao_Paulo')
    
    # Captura a referência da aplicação Flask do módulo principal
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.app import app as flask_app
    
    # Adiciona jitter (atraso aleatório) para evitar colisão com outras threads
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
                with flask_app.app_context():
                    # Usando o sistema de retry
                    execute_with_retry(update_price_cache_for_all_tickers)
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

def update_all_portfolios():
    """
    Thread para atualização automática de preços enquanto o mercado está aberto.
    """
    last_market_status = None
    dollar_counter = 0
    flask_app = None
    
    # Captura a referência da aplicação Flask do módulo principal
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.app import app as flask_app
    
    # Adiciona jitter (atraso aleatório) para evitar colisão com outras threads
    time.sleep(random.uniform(1, 8))
    
    print(f"[SCHEDULER] Thread de atualização iniciada com ID {instance_id}")
    
    while True:
        try:
            # Verifica rate limit
            if is_rate_limited():
                print(f"[RATE LIMIT] Pausando atualizações devido ao rate limit")
                time.sleep(60)
                continue
                
            # Verifica se o mercado está aberto
            market_is_open_flag = is_market_open()
            
            if market_is_open_flag:
                # Mercado aberto, atualiza preços
                if last_market_status is False:
                    print("Mercado abriu. Atualizando preços...")
                    
                last_market_status = True
                
                with flask_app.app_context():
                    try:
                        # Usando o sistema de retry com tratamento de delisted
                        execute_with_retry(update_prices_with_delisted_handling)
                    except Exception as e:
                        print(f"[ERROR] Erro ao atualizar preços: {e}")
                
                # Atualiza o dólar a cada 10 ciclos (30 minutos)
                dollar_counter += 1
                if dollar_counter >= 10:
                    with flask_app.app_context():
                        try:
                            def update_dollar():
                                get_cached_dollar_rate(force_update=True)
                                reset_rate_limit()
                                
                            execute_with_retry(update_dollar)
                        except Exception as e:
                            print(f"Erro ao atualizar dólar: {e}")
                            if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
                                handle_rate_limit()
                    dollar_counter = 0
                
                print(f"[SCHEDULER] Dormindo por 30 minutos antes da próxima atualização (mercado aberto)")
                time.sleep(1800)  # 30 minutos entre atualizações quando mercado aberto
            else:
                # Mercado fechado
                if last_market_status != False:
                    print("Mercado fechado, não atualizando preços.")
                    
                last_market_status = False
                print("[AGUARDANDO] Mercado fechado. Próxima atualização em 30 minutos.")
                time.sleep(1800)  # 30 minutos entre verificações quando mercado fechado
        except Exception as e:
            print(f"[ERROR] Erro no loop de atualização: {e}")
            time.sleep(60)  # Espera um pouco antes de tentar novamente

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
    
    # Evitar iniciar as threads mais de uma vez (em caso de reload do Flask)
    if threads_started:
        print("[SCHEDULER] Threads já iniciadas em uma instância anterior. Pulando...")
        return
        
    # Registra função de limpeza
    atexit.register(cleanup)
    
    with app.app_context():
        print(f"Inicializando tarefas agendadas (instância {instance_id})...")
        
        try:
            # Verifica se a última atualização de preços foi recente (menos de 10 minutos)
            now = datetime.now()
            if (now - last_price_update_time).total_seconds() > 600:  # 10 minutos
                # Executa a atualização de preços em uma thread separada para não bloquear a inicialização
                def async_price_update():
                    with app.app_context():
                        try:
                            print("[SCHEDULER] Iniciando atualização de preços em segundo plano...")
                            execute_with_retry(update_prices_with_delisted_handling)
                            print("[SCHEDULER] Atualização de preços em segundo plano concluída.")
                        except Exception as e:
                            print(f"[SCHEDULER] Erro na atualização de preços em segundo plano: {e}")
                
                price_thread = threading.Thread(target=async_price_update, daemon=True)
                price_thread.start()
            else:
                print(f"[SCHEDULER] Última atualização de preços foi há {(now - last_price_update_time).total_seconds() / 60:.1f} minutos. Pulando atualização inicial.")
            
            # Atualiza dividendos na inicialização (também em uma thread separada)
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
        
        # Thread para atualização automática durante o horário de mercado
        updater_thread = threading.Thread(target=update_all_portfolios, daemon=True)
        updater_thread.start()

        # Thread para atualizar dividendos todos os dias às 10:30
        dividends_thread = threading.Thread(target=schedule_dividends_update, daemon=True)
        dividends_thread.start()

        # Thread para atualizar preços todos os dias úteis às 18:00
        prices_thread = threading.Thread(target=schedule_prices_update, daemon=True)
        prices_thread.start()
        
        # Marca que as threads foram iniciadas
        threads_started = True
        
        print(f"Tarefas agendadas iniciadas com sucesso! (instância {instance_id})")