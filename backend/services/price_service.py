import yfinance as yf
from datetime import datetime
from flask import current_app, Flask
import json
import types  # Para retornar objeto de resultado com atributos
import threading
import concurrent.futures
import sys  # Para flush do stdout
from models.price_history_cache import PriceHistoryCache
from datetime import date
import pytz

# Configuração global de timeouts (em segundos)
# Para ajustar o timeout, basta alterar o valor desta variável
# Valores recomendados: 
# - 15-30 segundos para uso normal
# - 45-60 segundos se estiver tendo muitos timeouts
# - 10 segundos se quiser respostas mais rápidas mas com mais falhas
YF_REQUEST_TIMEOUT = 30  # Timeout para requisições ao yfinance

# Lock global para operações de escrita no PriceCache
pricecache_write_lock = threading.Lock()

from extensions.database import db
from models.price import PriceCache
from utils.ticker_utils import format_ticker
from utils.cache_utils import is_rate_limited, handle_rate_limit, reset_rate_limit, dollar_cache, dollar_cache_lock

def test_yfinance_request():
    """
    Testa a conectividade com a API do yfinance.
    
    Returns:
        bool: True se a conexão estiver funcionando, False caso contrário
    """
    try:
        # Testa uma requisição simples ao yfinance com timeout
        yf.Ticker("AAPL").history(period="1d", timeout=YF_REQUEST_TIMEOUT)
        # Se a requisição passar, significa que a conexão está funcionando
        print("[YFINANCE] Teste de conexão com yfinance bem-sucedido.")
        return True
    except Exception as e:
        err_msg = str(e)
        print(f"[YFINANCE] Erro ao testar yfinance: {err_msg}")
        # Só aciona rate limit se for erro de Too Many Requests
        if 'too many requests' in err_msg.lower():
            from utils.cache_utils import handle_rate_limit
            handle_rate_limit()
        return False

def get_price(ticker, formatar=True, force_yfinance=False):
    """
    Busca o preço atual de um ticker do cache (PriceCache) ou do yfinance se solicitado.
    Se force_yfinance=True, faz download do yfinance, atualiza o cache e retorna o valor novo.
    Caso contrário, retorna apenas o valor do cache.
    
    Args:
        ticker (str): Código do ticker
        formatar (bool): Se True, formata o ticker antes de buscar
        force_yfinance (bool): Se True, força atualização via yfinance
        
    Returns:
        float: Preço do ticker ou None se não houver no cache nem no yfinance
    """
    ticker_formatted = format_ticker(ticker) if formatar else ticker
    ticker_stripped = ticker.strip().upper()
    obj = PriceCache.query.filter(
        (PriceCache.ticker == ticker_stripped) | 
        (PriceCache.ticker == ticker_formatted)
    ).first()
    if not force_yfinance:
        if obj and obj.price:
            return obj.price
        return None

    # Se force_yfinance=True, tenta buscar do yfinance
    tz = pytz.timezone('America/Sao_Paulo')
    try:
        ticker_yf = yf.Ticker(ticker_formatted)
        # Primeiro tenta buscar pelo histórico
        hist = ticker_yf.history(period="5d", timeout=YF_REQUEST_TIMEOUT)
        price = None
        if not hist.empty:
            try:
                price = float(hist['Close'].dropna().iloc[-1])
            except Exception as e:
                print(f"[get_price] Erro ao acessar preço de fechamento para {ticker}: {e}")
        # Se não conseguiu via history, tenta buscar pelo info
        if price is None:
            try:
                ticker_info = ticker_yf.info
                price = ticker_info.get('currentPrice') or ticker_info.get('regularMarketPrice')
            except Exception as e:
                print(f"[get_price] Erro ao acessar info do yfinance para {ticker}: {e}")
        if price is not None:
            with pricecache_write_lock:
                if obj:
                    obj.price = price
                    obj.last_updated = datetime.now(tz)
                else:
                    db.session.add(PriceCache(
                        user_id=None,
                        ticker=ticker_formatted,
                        price=price,
                        last_updated=datetime.now(tz)
                    ))
                db.session.commit()
            return price
    except Exception as e:
        print(f"[get_price] Erro ao buscar preço do yfinance para {ticker}: {e}")
    # Se falhar, retorna o valor do cache se houver
    if obj and obj.price:
        return obj.price
    return None

def get_cached_dollar_rate(force_update=False):
    """
    Obtém a taxa de câmbio USD/BRL do cache ou atualiza se necessário/solicitado.
    
    Args:
        force_update (bool): Se True, força atualização do cache
        
    Returns:
        float: Taxa de câmbio USD/BRL
    """
    # Verificar se está em pausa por rate limit
    if is_rate_limited():
        # Em pausa, retorna o último valor conhecido
        with dollar_cache_lock:
            return dollar_cache['rate']
            
    with dollar_cache_lock:
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        ts = dollar_cache['timestamp']
        if ts is not None and ts.tzinfo is None:
            ts = tz.localize(ts)
        if not force_update and ts is not None and (now - ts).total_seconds() < 1800:
            return dollar_cache['rate']
            
        last_rate = dollar_cache['rate']
        rate = get_price("USDBRL=X")
        
        # Proteção: só aceita se variar no máximo 100% para cima ou para baixo
        if rate and rate > 0 and 0.5 * last_rate <= rate <= 2 * last_rate:
            dollar_cache['rate'] = rate
            dollar_cache['timestamp'] = now
            save_dollar_to_db(rate)
            return rate
            
        print(f"[get_cached_dollar_rate] Valor de dólar ignorado por variação absurda: {rate} (anterior: {last_rate})")
        return dollar_cache['rate']

def load_dollar_from_db():
    """Carrega a taxa de câmbio do dólar do banco de dados."""
    obj = PriceCache.query.filter_by(user_id=None, ticker="USDBRL=X").order_by(PriceCache.last_updated.desc()).first()
    if obj:
        with dollar_cache_lock:
            dollar_cache['rate'] = obj.price
            dollar_cache['timestamp'] = obj.last_updated

def save_dollar_to_db(rate):
    """
    Salva a taxa de câmbio do dólar no banco de dados.
    
    Args:
        rate (float): Taxa de câmbio a ser salva
    """
    if rate is None:
        print("[PRICECACHE] Ignorando update/insert para USDBRL=X pois price=None")
        return
    
    tz = pytz.timezone('America/Sao_Paulo')
    obj = PriceCache.query.filter_by(user_id=None, ticker="USDBRL=X").first()
    now = datetime.now(tz)
    
    if obj:
        obj.price = rate
        obj.last_updated = now
    else:
        db.session.add(PriceCache(user_id=None, ticker="USDBRL=X", price=rate, last_updated=now))
        
    db.session.commit()

def update_price_cache_for_all_tickers(app=None, num_workers=6):
    """
    Atualiza o cache de preços para todos os tickers únicos no sistema.
    Busca tickers de todos os portfolios e do cache existente.
    Permite passar o app Flask explicitamente para contexto correto nas threads.
    Returns:
        Object: Objeto com informações sobre a operação, incluindo tickers que deram erro "possibly delisted"
    """
    from flask import has_app_context, current_app
    if app is None:
        if has_app_context():
            app = current_app._get_current_object()
        else:
            raise RuntimeError("update_price_cache_for_all_tickers must be called with a Flask app context or with app= argument!")
    # Garante que app é a instância real do Flask
    if hasattr(app, '_get_current_object'):
        app = app._get_current_object()
    assert isinstance(app, Flask), f"[ERROR] app não é instância de Flask: {type(app)}"
    print(f"[DEBUG] update_price_cache_for_all_tickers: app={{'provided' if app else 'not provided'}}, type={type(app)}, has_app_context={{has_app_context()}}")
    from models.portfolio import Portfolio
    
    # Objeto de resultado que será retornado
    result = types.SimpleNamespace()
    result.delisted_tickers = []
    result.total_tickers = 0
    
    # Verifica se está em rate limit
    if is_rate_limited():
        print(f"[RATE LIMIT] Pausando update_price_cache_for_all_tickers devido ao rate limit")
        return result
        
    # Testa a conectividade com o yfinance
    if not test_yfinance_request():
        # Não chama handle_rate_limit aqui, pois já foi tratado dentro de test_yfinance_request
        return result
        
    print('[PRICECACHE] Atualizando cache de preços dos ativos únicos...')
    
    # Coleta todos os tickers únicos dos portfolios, normalizando com format_ticker
    tickers = set()
    portfolios = Portfolio.query.all()
    for portfolio in portfolios:
        try:
            portfolio_data = json.loads(portfolio.data)
        except Exception:
            continue
        for asset in portfolio_data:
            ticker_str = asset['ticker'].strip().upper()
            final_ticker = format_ticker(ticker_str)
            tickers.add(final_ticker)
    # Adiciona também os já presentes no PriceCache, normalizando
    for p in PriceCache.query.with_entities(PriceCache.ticker).distinct():
        tickers.add(format_ticker(p.ticker))
    # Restaurar processamento normal: usar todos os tickers únicos
    tickers = list(tickers)
    result.total_tickers = len(tickers)
    
    if not tickers:
        print('[PRICECACHE] Nenhum ticker encontrado para atualizar.')
        return result

    print(f"[PRICECACHE] Iniciando download de preços para {len(tickers)} ativos únicos...")
    sys.stdout.flush()
    try:
        df = None
        try:
            print("[DEBUG] Antes do yf.download")
            sys.stdout.flush()
            # Período de 30 dias para evitar problemas de série vazia
            df = yf.download(tickers=tickers, period='30d', group_by='ticker', progress=False, threads=True, timeout=YF_REQUEST_TIMEOUT)
            print("[DEBUG] Depois do yf.download")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.flush()
            err_msg = str(e)
            if 'Too Many Requests' in err_msg.lower():
                from utils.cache_utils import handle_rate_limit
                handle_rate_limit()
                print(f"[PRICECACHE] Rate limit detectado: {err_msg}")
                return result
            if 'possibly delisted' in err_msg or 'no price data found' in err_msg:
                # Processa os tickers que falharam para identificar os "possibly delisted"
                error_msg = err_msg
                if 'Failed download:' in error_msg:
                    lines = error_msg.split('\n')
                    for line in lines:
                        if "possibly delisted" in line.lower():
                            # Extrai o ticker do formato ['TICKER']: YFPricesMissingError...
                            start_idx = line.find("['") + 2
                            end_idx = line.find("']")
                            if start_idx > 0 and end_idx > start_idx:
                                ticker_with_error = line[start_idx:end_idx]
                                print(f"[PRICECACHE] Ticker possivelmente delisted: {ticker_with_error}")
                                result.delisted_tickers.append(ticker_with_error)
                print(f"[PRICECACHE] YFPricesMissingError (simulado): {e}")
            elif 'HTTP Error' in err_msg:
                print(f"[PRICECACHE] HTTPError: {e}")
            elif 'timed out' in err_msg:
                print(f"[PRICECACHE] Timeout: {e}")
            else:
                print(f"[PRICECACHE] Erro inesperado no download do yfinance: {e}")
            sys.stdout.flush()
        # Reset pausa se sucesso
        reset_rate_limit()
        sys.stdout.flush()
        # Processa os resultados
        process_yfinance_results(df, tickers, result, app=app)
        sys.stdout.flush()
        # Atualiza o banco conforme as regras de delisted/rate limit
        update_price_cache_db(result.delisted_tickers, result.total_tickers)
        sys.stdout.flush()
        return result
        
    except Exception as e:
        print(f'[PRICECACHE] Erro ao atualizar preços dos ativos únicos: {e}')
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
            handle_rate_limit()
        return result

def process_yfinance_results(df, tickers, result=None, app=None):
    """
    Processa os resultados do yfinance e atualiza o banco de dados.
    Prioriza o uso do método info para obter preços em tempo real.
    Agora paraleliza em 6 batches para aproveitar múltiplos núcleos.
    Cada thread executa dentro de um contexto Flask passado explicitamente.
    
    Args:
        df (pandas.DataFrame): DataFrame com os preços
        tickers (list): Lista de tickers
        result (object): Objeto opcional para armazenar informações sobre tickers delisted
        app (Flask): Instância da aplicação Flask para contexto (obrigatório)
    """
    import math
    from itertools import islice
    from flask import Flask
    BATCH_SIZE = 10
    batch_count = 0
    NUM_WORKERS = 1  # Reduzido para evitar database locked no SQLite

    # Garante que app é a instância real do Flask
    if hasattr(app, '_get_current_object'):
        app = app._get_current_object()
    assert isinstance(app, Flask), f"[ERROR] app não é instância de Flask: {type(app)}"
    print(f"[DEBUG] process_yfinance_results: app type={type(app)}")

    if app is None:
        raise ValueError("Flask app instance must be provided to process_yfinance_results for proper DB context.")

    def chunked(iterable, n):
        # Divide a lista em n partes aproximadamente iguais
        k, m = divmod(len(iterable), n)
        return [iterable[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def process_ticker_batch(ticker_batch):
        import pytz
        tz = pytz.timezone('America/Sao_Paulo')
        with app.app_context():
            print(f"[BATCH] Iniciando batch com {len(ticker_batch)} tickers: {ticker_batch}")
            sys.stdout.flush()
            local_batch_count = 0
            local_delisted = []
            try:
                for ticker in ticker_batch:
                    if result and ticker in result.delisted_tickers:
                        continue
                    price = None
                    # Primeiro tenta buscar pelo histórico
                    try:
                        ticker_yf = yf.Ticker(ticker)
                        hist = ticker_yf.history(period="5d", timeout=YF_REQUEST_TIMEOUT)
                        if not hist.empty:
                            try:
                                price = float(hist['Close'].dropna().iloc[-1])
                                print(f"[PRICECACHE] Preço histórico usado para {ticker}: {price}")
                            except Exception as e:
                                print(f"[PRICECACHE] Erro ao acessar preço de fechamento para {ticker}: {e}")
                        # Se não conseguiu via history, tenta buscar pelo info
                        if price is None:
                            try:
                                ticker_info = ticker_yf.info
                                price = ticker_info.get('currentPrice') or ticker_info.get('regularMarketPrice')
                                if price:
                                    print(f"[PRICECACHE] Preço em tempo real obtido para {ticker}: {price}")
                            except Exception as e:
                                print(f"[PRICECACHE] Erro ao buscar preço em tempo real para {ticker}: {e}")
                                if 'possibly delisted' in str(e).lower() and result is not None:
                                    print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via info)")
                                    local_delisted.append(ticker)
                                    continue
                    except Exception as e:
                        print(f"[PRICECACHE] Erro ao buscar preço do yfinance para {ticker}: {e}")
                    if price is None and df is not None:
                        close_series = None
                        if len(tickers) == 1:
                            close_series = df['Close'] if 'Close' in df else None
                        else:
                            if (ticker, 'Close') in df:
                                close_series = df[(ticker, 'Close')]
                            elif ticker in df and 'Close' in df[ticker]:
                                close_series = df[ticker]['Close']
                        try:
                            if close_series is not None and not close_series.empty:
                                price = float(close_series.dropna().iloc[-1])
                                print(f"[PRICECACHE] Preço histórico usado para {ticker}: {price}")
                            else:
                                print(f"[PRICECACHE] Série de preços vazia para {ticker}, ignorando.")
                                if result is not None:
                                    local_delisted.append(ticker)
                                    print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via série vazia)")
                        except IndexError:
                            print(f"[PRICECACHE] IndexError: série vazia para {ticker}, ignorando.")
                            if result is not None:
                                local_delisted.append(ticker)
                                print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via IndexError)")
                        except Exception as e:
                            print(f"[PRICECACHE] Erro ao acessar preço para {ticker}: {e}")
                    if price is not None:
                        with pricecache_write_lock:
                            obj = PriceCache.query.filter_by(user_id=None, ticker=ticker).first()
                            if obj:
                                old_price = obj.price
                                obj.price = price
                                obj.last_updated = datetime.now(tz)
                                print(f"[PRICECACHE][UPDATE] {ticker}: {old_price} -> {price} (last_updated={obj.last_updated})")
                            else:
                                db.session.add(PriceCache(
                                    user_id=None,
                                    ticker=ticker,
                                    price=price,
                                    last_updated=datetime.now(tz)
                                ))
                                print(f"[PRICECACHE][INSERT] {ticker}: {price}")
                            # Atualiza também price_history_cache para o dia de hoje, sempre usando ticker normalizado
                            ticker_norm = format_ticker(ticker)
                            today = date.today()
                            phc = PriceHistoryCache.query.filter_by(ticker=ticker_norm, date=today).first()
                            now = datetime.now(tz)
                            if phc:
                                phc.close = price
                                phc.last_updated = now
                            else:
                                db.session.add(PriceHistoryCache(
                                    ticker=ticker_norm,
                                    date=today,
                                    close=price,
                                    last_updated=now
                                ))
                            local_batch_count += 1
                            if local_batch_count % BATCH_SIZE == 0:
                                db.session.commit()
                                print(f"[PRICECACHE][COMMIT] Batch commit realizado para {BATCH_SIZE} tickers.")
                    else:
                        print(f"[PRICECACHE] Ignorando update/insert para {ticker} pois price=None")
                        if result is not None and ticker not in local_delisted:
                            local_delisted.append(ticker)
                            print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via price=None)")
                with pricecache_write_lock:
                    db.session.commit()
                    print(f"[PRICECACHE][COMMIT] Batch commit realizado para {len(ticker_batch)} tickers.")
                    print("[PRICECACHE][DB] Valores finais salvos no banco:")
                    for ticker in ticker_batch:
                        obj = PriceCache.query.filter_by(user_id=None, ticker=ticker).first()
                        if obj:
                            print(f"[PRICECACHE][DB] {ticker}: {obj.price} (last_updated={obj.last_updated})")
                print(f"[BATCH] Fim do batch com {len(ticker_batch)} tickers")
                sys.stdout.flush()
                return local_delisted
            except Exception as e:
                print(f"[BATCH][ERROR] Exceção no batch: {e}")
                sys.stdout.flush()
                return []

    batches = chunked(tickers, NUM_WORKERS)
    all_delisted = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(process_ticker_batch, batch) for batch in batches if batch]
        for future in concurrent.futures.as_completed(futures):
            batch_delisted = future.result()
            if result is not None:
                result.delisted_tickers.extend(batch_delisted)
            all_delisted.extend(batch_delisted)
    print(f'[PRICECACHE] Preços atualizados para {len(tickers)} ativos únicos')
    if result and result.delisted_tickers:
        print(f'[PRICECACHE] {len(result.delisted_tickers)} tickers possivelmente delisted')

def remove_delisted_from_cache(delisted_tickers):
    """Remove tickers delisted do PriceCache e loga a ação."""
    if not delisted_tickers:
        return
    for ticker in delisted_tickers:
        with pricecache_write_lock:
            obj = PriceCache.query.filter_by(ticker=ticker).first()
            if obj:
                db.session.delete(obj)
                print(f"[PRICECACHE] Removido ticker delisted do cache: {ticker}")
    db.session.commit()

def update_price_cache_db(delisted_tickers, total_tickers):
    """
    Atualiza o banco de dados PriceCache conforme as regras:
    - Se todos os tickers deram erro, não remove nenhum (rate limit).
    - Se apenas alguns deram erro, remove apenas esses do banco.
    """
    if total_tickers > 0 and len(delisted_tickers) == total_tickers:
        print("[PRICECACHE] Todos os tickers falharam, possível rate limit. Não removendo tickers do banco.")
        return
    if delisted_tickers:
        for ticker in delisted_tickers:
            obj = PriceCache.query.filter_by(ticker=ticker).first()
            if obj:
                db.session.delete(obj)
                print(f"[PRICECACHE] Removido ticker delisted do cache: {ticker}")
        db.session.commit()
        print(f"[PRICECACHE] {len(delisted_tickers)} tickers removidos do cache.")