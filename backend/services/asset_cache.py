"""
Serviço para gerenciar o cache central de ativos
"""
import threading
import time
import json
from datetime import datetime, timedelta
from flask import current_app
import logging

from extensions.database import db
from models.portfolio import Portfolio
from models.price import PriceCache
from utils.ticker_utils import format_ticker
from services.price_service import get_price

# Dicionário de cache global de ativos
assets_cache = {}
assets_cache_lock = threading.Lock()

# Timestamp da última atualização completa
last_update_time = datetime.now() - timedelta(hours=1)

# Lock para a última atualização
last_update_time_lock = threading.Lock()

# Set para tickers marcados como delisted
delisted_tickers = set()

# Lock para o conjunto de tickers delisted
delisted_tickers_lock = threading.Lock()

# Dicionário para contar falhas consecutivas por ticker
ticker_failures = {}
ticker_failures_lock = threading.Lock()

# Configura logging específico para o cache de ativos
logger = logging.getLogger('asset_cache')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [ASSET_CACHE] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def initialize_assets_cache():
    """
    Inicializa o cache central de ativos, coletando todos os tickers únicos do sistema.
    """
    with assets_cache_lock:
        logger.info("Inicializando cache central de ativos...")
        
        # Coleta todos os tickers únicos dos portfolios
        all_tickers = set()
        
        # Dos portfolios
        portfolios = Portfolio.query.all()
        for portfolio in portfolios:
            try:
                portfolio_data = json.loads(portfolio.data)
                for asset in portfolio_data:
                    ticker = asset['ticker'].strip().upper()
                    all_tickers.add(ticker)
            except Exception as e:
                logger.error(f"Erro ao processar portfolio para o cache: {e}")
        
        # Do cache de preços existente
        for price in PriceCache.query.all():
            all_tickers.add(price.ticker)
        
        # Remove tickers conhecidos como delisted
        with delisted_tickers_lock:
            active_tickers = [t for t in all_tickers if t not in delisted_tickers]
        
        # Cria o cache inicial
        for ticker in active_tickers:
            # Verifica se já existe no cache
            price_obj = PriceCache.query.filter_by(ticker=ticker).first()
            if price_obj:
                assets_cache[ticker] = {
                    'price': price_obj.price,
                    'last_updated': price_obj.last_updated,
                }
        
        logger.info(f"Cache central inicializado com {len(assets_cache)} ativos")
        return assets_cache

def get_asset_price(ticker):
    """
    Obtém o preço de um ativo do cache central. Se o ativo não existir,
    adiciona ao cache e atualiza seu preço.
    
    Args:
        ticker (str): Código do ativo
        
    Returns:
        float: Preço do ativo ou None se não encontrado/erro
    """
    ticker = ticker.strip().upper()
    
    # Verifica se o ticker está no cache
    with assets_cache_lock:
        # Se o ticker estiver no cache, retorna o preço
        if ticker in assets_cache:
            # Reseta o contador de falhas quando um ticker é acessado com sucesso
            reset_ticker_failure_count(ticker)
            logger.debug(f"Preço para {ticker} encontrado no cache: {assets_cache[ticker]['price']}")
            return assets_cache[ticker]['price']
    
    # Se o ticker não estiver no cache, verifica se está marcado como delisted
    with delisted_tickers_lock:
        if ticker in delisted_tickers:
            logger.debug(f"Ticker {ticker} está marcado como delisted, retornando None")
            return None
    
    # Se não estiver no cache nem marcado como delisted, busca o preço e adiciona ao cache
    logger.info(f"Novo ativo detectado: {ticker}. Buscando preço...")
    price = get_price(ticker, force_yfinance=True)
    
    if price:
        with assets_cache_lock:
            assets_cache[ticker] = {
                'price': price,
                'last_updated': datetime.now()
            }
        logger.info(f"Novo ativo {ticker} adicionado ao cache com preço {price}")
        
        # Reseta qualquer contador de falhas
        reset_ticker_failure_count(ticker)
        
        # Salva no banco de dados para persistência
        save_to_price_cache(ticker, price)
        return price
    else:
        # Incrementa o contador de falhas
        increment_ticker_failure_count(ticker)
        failures = get_ticker_failure_count(ticker)
        
        # Se falhou muitas vezes consecutivas, marca como delisted
        if failures >= 3:
            with delisted_tickers_lock:
                delisted_tickers.add(ticker)
            logger.warning(f"Não foi possível obter preço para {ticker} após {failures} tentativas, marcado como possível delisted")
        else:
            logger.warning(f"Não foi possível obter preço para {ticker} (tentativa {failures})")
        
        return None

def save_to_price_cache(ticker, price):
    """
    Salva ou atualiza um registro no banco de dados PriceCache.
    Também atualiza price_history_cache para refletir o último preço do dia.
    
    Args:
        ticker (str): Código do ativo
        price (float): Preço do ativo
    """
    try:
        ticker = ticker.strip().upper()
        obj = PriceCache.query.filter_by(ticker=ticker).first()
        now = datetime.now()
        
        if obj:
            obj.price = price
            obj.last_updated = now
        else:
            db.session.add(PriceCache(
                user_id=None,
                ticker=ticker,
                price=price,
                last_updated=now
            ))
        # Atualiza também price_history_cache para o dia de hoje
        from models.price_history_cache import PriceHistoryCache
        from datetime import date
        today = date.today()
        phc = PriceHistoryCache.query.filter_by(ticker=ticker, date=today).first()
        if phc:
            phc.close = price
            phc.last_updated = now
        else:
            db.session.add(PriceHistoryCache(
                ticker=ticker,
                date=today,
                close=price,
                last_updated=now
            ))
        db.session.commit()
        logger.debug(f"Preço para {ticker} salvo no banco: {price}")
    except Exception as e:
        logger.error(f"Erro ao salvar preço para {ticker} no banco: {e}")
        db.session.rollback()
        
        # Tentar novamente com tratamento de exceção específico
        try:
            # Em caso de erro de concorrência, tenta novamente buscando o objeto atual
            obj = PriceCache.query.filter_by(ticker=ticker).first()
            if obj:
                obj.price = price
                obj.last_updated = now = datetime.now()
            else:
                db.session.add(PriceCache(
                    user_id=None,
                    ticker=ticker,
                    price=price,
                    last_updated=now
                ))
            db.session.commit()
            logger.debug(f"Preço para {ticker} salvo no banco na segunda tentativa: {price}")
        except Exception as e2:
            logger.error(f"Erro persistente ao salvar preço para {ticker} no banco: {e2}")
            db.session.rollback()

def update_assets_cache(specific_tickers=None, max_retries=3, retry_delay=5):
    """
    Atualiza os preços no cache central. Pode atualizar todos os ativos
    ou apenas uma lista específica de tickers.
    
    Args:
        specific_tickers (list): Lista opcional de tickers específicos para atualizar
        max_retries (int): Número máximo de tentativas para atualizar um ticker
        retry_delay (int): Tempo de espera entre tentativas (segundos)
        
    Returns:
        dict: Estatísticas da atualização
    """
    global last_update_time
    
    stats = {
        'total': 0,
        'updated': 0,
        'failed': 0,
        'delisted': 0,
        'retried': 0,
        'rate_limited': False
    }
    
    logger.info("[DEBUG] Iniciando update_assets_cache (forçando atualização do yfinance para todos os ativos)")
    # Se não houver tickers específicos, atualiza todos os tickers do cache
    if not specific_tickers:
        with assets_cache_lock:
            tickers_to_update = list(assets_cache.keys())
    else:
        tickers_to_update = [t.strip().upper() for t in specific_tickers]
    
    stats['total'] = len(tickers_to_update)
    logger.info(f"Iniciando atualização de {stats['total']} ativos...")
      # Atualiza em lotes para evitar sobrecarga da API
    BATCH_SIZE = 5
    failed_tickers = []
    
    for i in range(0, len(tickers_to_update), BATCH_SIZE):
        batch = tickers_to_update[i:i+BATCH_SIZE]
        logger.info(f"Atualizando lote {i//BATCH_SIZE + 1}/{(len(tickers_to_update) + BATCH_SIZE - 1)//BATCH_SIZE}")
        
        for ticker in batch:
            retry_count = 0
            success = False
            while retry_count < max_retries and not success:
                try:
                    # Verifica se está em rate limit antes de tentar
                    from utils.cache_utils import is_rate_limited
                    if is_rate_limited():
                        logger.warning(f"Rate limit ativo, pausando atualização do lote")
                        stats['rate_limited'] = True
                        break
                    
                    # Verifica formato correto para tickers BR
                    formatted_ticker = ticker
                    if '.' not in ticker and '=' not in ticker:
                        formatted_ticker = format_ticker(ticker)
                    
                    price = get_price(formatted_ticker, formatar=False, force_yfinance=True)
                    if price is not None:
                        logger.info(f"[DEBUG] Preço atualizado para {ticker}: {price}")
                        # Atualiza o cache
                        with assets_cache_lock:
                            assets_cache[ticker] = {
                                'price': price,
                                'last_updated': datetime.now()
                            }
                        
                        # Salva no banco de dados
                        save_to_price_cache(ticker, price)
                        stats['updated'] += 1
                        logger.debug(f"Preço atualizado para {ticker}: {price}")
                        success = True
                    else:
                        # Se falhar, incrementa contagem de tentativas
                        retry_count += 1
                        stats['retried'] += 1
                        logger.warning(f"Tentativa {retry_count}/{max_retries} falhou para {ticker}")
                        
                        if retry_count < max_retries:
                            logger.info(f"Aguardando {retry_delay}s antes da próxima tentativa para {ticker}")
                            time.sleep(retry_delay)
                        else:
                            failed_tickers.append(ticker)
                            stats['failed'] += 1
                            logger.warning(f"Falha ao obter preço para {ticker} após {max_retries} tentativas")
                
                except Exception as e:
                    retry_count += 1
                    stats['retried'] += 1
                    logger.error(f"Erro na tentativa {retry_count}/{max_retries} para {ticker}: {e}")
                    
                    if retry_count < max_retries:
                        logger.info(f"Aguardando {retry_delay}s antes da próxima tentativa para {ticker}")
                        time.sleep(retry_delay)
                    else:
                        failed_tickers.append(ticker)
                        stats['failed'] += 1
                        logger.error(f"Erro ao atualizar {ticker} após {max_retries} tentativas: {e}")
            
            # Se atingiu rate limit, interrompe o processamento do lote atual
            if stats['rate_limited']:
                break
        
        # Se atingiu rate limit, interrompe todo o processamento
        if stats['rate_limited']:
            logger.warning("Interrompendo atualização devido a rate limit")
            break
        
        # Pequeno delay entre lotes para evitar rate limit
        if i + BATCH_SIZE < len(tickers_to_update):
            time.sleep(2)
      # Processa tickers que falharam
    if len(failed_tickers) > 0:
        # Se mais de 60% dos tickers falharem, pode ser um problema de rate limit ou conectividade
        if len(failed_tickers) > 0.6 * stats['total']:
            logger.warning(f"Mais de 60% dos tickers falharam ({len(failed_tickers)}/{stats['total']}), possível rate limit ou problema de conexão.")
            # Marca o rate limit para evitar novas tentativas imediatas
            from utils.cache_utils import handle_rate_limit
            handle_rate_limit()
            stats['rate_limited'] = True
            logger.warning("Rate limit ativado por precaução. Tentativas serão pausadas por algum tempo.")
        else:
            # Alguns tickers falharam, podem ser delisted ou temporariamente indisponíveis
            logger.info(f"{len(failed_tickers)} tickers falharam, verificando status...")
            
            for ticker in failed_tickers:
                # Verifica quantas vezes o ticker falhou consecutivamente
                failures = get_ticker_failure_count(ticker)
                
                if failures >= 3:  # Se falhou 3 ou mais vezes consecutivas
                    with delisted_tickers_lock:
                        delisted_tickers.add(ticker)
                    
                    # Remove do cache
                    with assets_cache_lock:
                        if ticker in assets_cache:
                            del assets_cache[ticker]
                    
                    # Remove do banco de dados
                    try:
                        obj = PriceCache.query.filter_by(ticker=ticker).first()
                        if obj:
                            db.session.delete(obj)
                            stats['delisted'] += 1
                            logger.info(f"Ticker {ticker} removido como possível delisted após {failures} falhas consecutivas")
                    except Exception as e:
                        logger.error(f"Erro ao remover ticker delisted {ticker}: {e}")
                else:
                    # Incrementa o contador de falhas, mas mantém o ticker
                    increment_ticker_failure_count(ticker)
                    logger.info(f"Ticker {ticker} falhou {failures + 1} vezes, mantendo no sistema por enquanto")
            
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Erro ao persistir alterações de tickers delisted: {e}")
                db.session.rollback()
    
    # Atualiza o timestamp da última atualização completa
    if not specific_tickers and not stats['rate_limited']:  # Somente se for atualização completa e bem-sucedida
        with last_update_time_lock:
            last_update_time = datetime.now()
            logger.info(f"Timestamp de última atualização atualizado: {last_update_time}")
    
    logger.info(f"Atualização concluída: {stats['updated']} atualizados, {stats['failed']} falhas, {stats['retried']} retentativas, {stats['delisted']} removidos, rate_limited: {stats['rate_limited']}")
    return stats

def is_time_to_update():
    """
    Verifica se é hora de fazer uma atualização completa baseado nos intervalos fixos de 30 minutos.
    
    Returns:
        bool: True se for hora de atualizar, False caso contrário
    """
    now = datetime.now()
    
    # Intervalos de 30 minutos: 00:00, 00:30, 01:00, 01:30, etc.
    # Verificamos se estamos próximos de um desses intervalos (até 30 segundos)
    minutes = now.minute
    seconds = now.second
    
    # Verifica se o rate limit está ativo
    from utils.cache_utils import is_rate_limited
    if is_rate_limited():
        logger.warning("Rate limit ativo, adiando atualização")
        return False
    
    # Se estivermos próximos do início da hora ou da meia-hora
    is_near_interval = (minutes == 0 or minutes == 30) and seconds < 60
    
    if is_near_interval:
        with last_update_time_lock:
            # Evita atualizações repetidas no mesmo intervalo
            time_since_last_update = (now - last_update_time).total_seconds()
            
            # Se a última atualização foi há menos de 10 minutos, não atualiza novamente
            if time_since_last_update < 600:
                logger.debug(f"Última atualização foi há apenas {time_since_last_update/60:.1f} min, aguardando")
                return False
                
            logger.info(f"É hora de atualizar (intervalo fixo de 30 min): {now.strftime('%H:%M:%S')}")
            return True
    
    # Também atualizamos se passou muito tempo desde a última atualização (caso o servidor tenha ficado inativo)
    with last_update_time_lock:
        time_since_last_update = (now - last_update_time).total_seconds()
        if time_since_last_update > 1800:  # 30 minutos
            logger.info(f"Passou muito tempo desde a última atualização ({time_since_last_update/60:.1f} min)")
            return True
    
    return False

def get_dollar_rate():
    """
    Obtém a taxa de câmbio do dólar.
    
    Returns:
        float: Taxa de câmbio USD/BRL
    """
    return get_asset_price("USDBRL=X")

def get_ticker_failure_count(ticker):
    """
    Obtém o número de falhas consecutivas para um ticker.
    
    Args:
        ticker (str): Código do ticker
        
    Returns:
        int: Número de falhas consecutivas
    """
    ticker = ticker.strip().upper()
    with ticker_failures_lock:
        return ticker_failures.get(ticker, 0)

def increment_ticker_failure_count(ticker):
    """
    Incrementa o contador de falhas para um ticker.
    
    Args:
        ticker (str): Código do ticker
    """
    ticker = ticker.strip().upper()
    with ticker_failures_lock:
        ticker_failures[ticker] = ticker_failures.get(ticker, 0) + 1
        logger.debug(f"Incrementado contador de falhas para {ticker}: {ticker_failures[ticker]}")

def reset_ticker_failure_count(ticker):
    """
    Reseta o contador de falhas para um ticker.
    
    Args:
        ticker (str): Código do ticker
    """
    ticker = ticker.strip().upper()
    with ticker_failures_lock:
        if ticker in ticker_failures:
            del ticker_failures[ticker]
            logger.debug(f"Resetado contador de falhas para {ticker}")

def save_cache_to_database():
    """
    Salva todo o conteúdo do cache na base de dados para persistência.
    Esta função deve ser chamada periodicamente ou antes de encerrar o aplicativo.
    """
    start_time = time.time()
    saved_count = 0
    
    try:
        logger.info("Iniciando persistência do cache central no banco de dados...")
        
        with assets_cache_lock:
            for ticker, data in assets_cache.items():
                try:
                    save_to_price_cache(ticker, data['price'])
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Erro ao persistir {ticker}: {e}")
        
        logger.info(f"Persistência concluída: {saved_count} registros salvos em {time.time() - start_time:.3f}s")
    except Exception as e:
        logger.error(f"Erro geral durante persistência do cache: {e}")
