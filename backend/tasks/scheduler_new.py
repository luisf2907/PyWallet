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
from services.dividend_service import update_dividends_cache_for_all_users
from services.asset_cache import initialize_assets_cache, update_assets_cache, is_time_to_update, save_cache_to_database
from utils.cache_utils import is_rate_limited, handle_rate_limit, reset_rate_limit
from extensions.database import execute_with_retry, db

# Configura logging específico para o scheduler
logger = logging.getLogger('scheduler')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [SCHEDULER] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Detectar se está rodando no reloader do Flask
# WERKZEUG_RUN_MAIN == 'true' indica processo principal do Flask
# Se for None ou diferente de 'true', é o processo reloader
is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'

# Flag para controlar se as threads já estão rodando
threads_started = False

# ID único desta instância para evitar inicializações duplicadas em reloads
instance_id = str(uuid.uuid4())

def run_price_update():
    """Executa a atualização de preços com mecanismo de retry e tratamento de erros"""
    try:
        stats = update_assets_cache()
        logger.info(f"Atualização de preços concluída: {stats['updated']} de {stats['total']} atualizados")
        
        # Verifica se houve muitos erros ou se detectou rate limit
        if stats.get('rate_limited', False):
            logger.warning("Rate limit detectado durante a atualização")
            handle_rate_limit()
            return False
        
        # Se a atualização foi bem-sucedida, persistir o cache
        save_cache_to_database()
        
        # Reseta o contador de rate limit se tudo correr bem e não houve muitos erros
        if stats['failed'] < 0.3 * stats['total']:
            reset_rate_limit()
        
        return True
    except Exception as e:
        logger.error(f"Erro na atualização de preços: {e}")
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
            handle_rate_limit()
        return False

def schedule_fixed_updates():
    """
    Thread para atualização de preços em intervalos fixos de 30 minutos (00:00, 00:30, etc.)
    """
    # Captura a referência da aplicação Flask do módulo principal
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.app import app as flask_app
    
    # Adiciona jitter (atraso aleatório) para evitar colisão com outras threads
    time.sleep(random.uniform(1, 5))
    
    logger.info(f"Thread de atualização em intervalos fixos iniciada com ID {instance_id}")
    
    # Inicializa o cache central
    with flask_app.app_context():
        initialize_assets_cache()
    
    # Inicialização: faz uma primeira atualização ao iniciar o servidor
    logger.info("Realizando atualização inicial ao iniciar o servidor...")
    with flask_app.app_context():
        execute_with_retry(run_price_update)
    
    while True:
        try:
            # Verifica rate limit
            if is_rate_limited():
                logger.warning("Pausando atualizações devido ao rate limit")
                time.sleep(60)  # Espera 1 minuto antes de tentar novamente
                continue
            
            now = datetime.now()
            
            # Verifica se é hora de fazer uma atualização (intervalos fixos)
            if is_time_to_update():
                logger.info(f"Iniciando atualização programada: {now.strftime('%H:%M:%S')}")
                
                # Executa a atualização com app_context
                with flask_app.app_context():
                    success = execute_with_retry(run_price_update)
                    
                    if success:
                        logger.info("Atualização de preços concluída com sucesso")
                    else:
                        logger.error("Falha na atualização de preços")
                
                # Pequeno delay após a atualização para evitar duplicações 
                # (caso estejamos muito próximos do limite do intervalo)
                time.sleep(35)
            
            # Espera um curto período antes de verificar novamente
            # (curto o suficiente para não perder o início de um intervalo)
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Erro no loop de atualização: {e}")
            time.sleep(60)  # Espera um pouco antes de tentar novamente

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
    
    logger.info(f"Thread de atualização de dividendos iniciada com ID {instance_id}")
    
    while True:
        now = datetime.now(tz)
        
        # Verifica se já atualizou hoje
        if now.date() == last_update_date:
            # Já atualizou hoje, espera até amanhã
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            logger.info(f"Próxima atualização de dividendos em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))  # Dorme no máximo 1 hora para poder verificar novamente
            continue
        
        # Verifica se já passou do horário de hoje
        target_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= target_time:
            try:
                logger.info('Atualização diária de dividendos iniciada')
                with flask_app.app_context():
                    # Usando o sistema de retry
                    execute_with_retry(update_dividends_cache_for_all_users)
                    # Marca que atualizou hoje
                    last_update_date = now.date()
                    logger.info('Atualização diária de dividendos concluída com sucesso')
            except Exception as e:
                logger.error(f'Erro na atualização diária de dividendos: {e}')
            
            # Aguarda até o próximo dia
            next_run = now.replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            logger.info(f"Próxima atualização de dividendos em {sleep_seconds / 3600:.1f} horas")
            time.sleep(min(sleep_seconds, 3600))  # Dorme no máximo 1 hora para poder verificar novamente
        else:
            # Ainda não chegou a hora hoje, espera até a hora
            sleep_seconds = (target_time - now).total_seconds()
            logger.info(f"Próxima atualização de dividendos em {sleep_seconds / 60:.1f} minutos")
            time.sleep(min(sleep_seconds, 1800))  # Dorme no máximo 30 minutos para poder verificar novamente

def schedule_cache_persistence():
    """
    Thread para persistência periódica do cache (a cada 15 minutos).
    """
    # Captura a referência da aplicação Flask do módulo principal
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.app import app as flask_app
    
    # Adiciona jitter (atraso aleatório) para evitar colisão com outras threads
    time.sleep(random.uniform(5, 15))
    
    logger.info(f"Thread de persistência de cache iniciada com ID {instance_id}")
    
    while True:
        try:
            # Persiste o cache a cada 15 minutos
            with flask_app.app_context():
                logger.info("Executando persistência programada do cache")
                save_cache_to_database()
                logger.info("Persistência do cache concluída")
            
            # Aguarda 15 minutos antes da próxima persistência
            time.sleep(900)  # 15 minutos
            
        except Exception as e:
            logger.error(f"Erro na persistência do cache: {e}")
            time.sleep(300)  # Aguarda 5 minutos antes de tentar novamente

def cleanup():
    """Função de limpeza chamada quando o processo termina"""
    logger.info(f"Limpando recursos da instância {instance_id}")

def save_cache_before_exit():
    """Salva o cache em disco antes de encerrar a aplicação"""
    logger.info("Aplicação encerrando, salvando cache em disco...")
    try:
        save_cache_to_database()
        logger.info("Cache salvo com sucesso")
    except Exception as e:
        logger.error(f"Erro ao salvar cache antes de encerrar: {e}")

def start_scheduled_tasks(app):
    """
    Inicia todas as tarefas agendadas em threads separadas.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    global threads_started
    
    # Evitar iniciar as threads mais de uma vez (em caso de reload do Flask)
    # ou se estiver rodando no processo reloader do Flask
    if threads_started or is_reloader:
        logger.info("Threads já iniciadas ou rodando no reloader do Flask. Pulando...")
        return
        
    # Registra função de limpeza
    atexit.register(cleanup)
    atexit.register(save_cache_before_exit)
    
    with app.app_context():
        logger.info(f"Inicializando tarefas agendadas (instância {instance_id})...")
        
        try:
            # Thread para atualizações em intervalos fixos de 30 minutos
            fixed_updates_thread = threading.Thread(target=schedule_fixed_updates, daemon=True)
            fixed_updates_thread.start()
            
            # Thread para atualizar dividendos todos os dias às 10:30
            dividends_thread = threading.Thread(target=schedule_dividends_update, daemon=True)
            dividends_thread.start()
            
            # Thread para persistência periódica do cache
            cache_persistence_thread = threading.Thread(target=schedule_cache_persistence, daemon=True)
            cache_persistence_thread.start()
            
            # Marca que as threads foram iniciadas
            threads_started = True
            
            logger.info(f"Tarefas agendadas iniciadas com sucesso! (instância {instance_id})")
            
        except Exception as e:
            logger.error(f"Erro durante inicialização das tarefas: {e}")
