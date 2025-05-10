import yfinance as yf
from datetime import datetime
from flask import current_app
import json
import types  # Para retornar objeto de resultado com atributos
import threading

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
        # Testa uma requisição simples ao yfinance
        yf.Ticker("AAPL").info
        return True
    except Exception as e:
        print(f"[YFINANCE] Erro ao testar yfinance: {e}")
        return False

def get_price(ticker, formatar=True):
    """
    Busca o preço atual de um ticker via yfinance.
    Se for um ativo brasileiro (sem separadores), adiciona ".SA" ao final.
    Respeita o rate limit e usa cache se estiver em pausa.
    Prioriza o uso do método info para obter preços em tempo real.
    
    Args:
        ticker (str): Código do ticker
        formatar (bool): Se True, formata o ticker antes de buscar
        
    Returns:
        float: Preço do ticker ou None em caso de erro
    """
    # Verificar se está em pausa por rate limit
    if is_rate_limited():
        # Em pausa, busca apenas do cache
        ticker_formatted = format_ticker(ticker) if formatar else ticker
        ticker_stripped = ticker.strip().upper()
        
        # Procura no cache
        obj = PriceCache.query.filter(
            (PriceCache.ticker == ticker_stripped) | 
            (PriceCache.ticker == ticker_formatted)
        ).first()
        
        if obj and obj.price:
            return obj.price
        return None

    try:
        yf_ticker = format_ticker(ticker) if formatar else ticker
        
        # Primeiro tenta obter o preço direto da API info (preço em tempo real)
        try:
            ticker_info = yf.Ticker(yf_ticker).info
            # Tenta obter o preço atual ou preço de mercado regular
            price = ticker_info.get('currentPrice') or ticker_info.get('regularMarketPrice')
            if price:
                return float(price)
        except Exception as e:
            print(f"[get_price] Erro ao buscar info para {yf_ticker}: {e}")
        
        # Se não conseguiu via info, tenta usar o download histórico
        df = None
        try:
            df = yf.download(yf_ticker, period="5d", interval="1d", progress=False)
        except Exception as e:
            if 'possibly delisted' in str(e) or 'no price data found' in str(e):
                print(f"[get_price] YFPricesMissingError (simulado): {e}")
            elif 'HTTP Error' in str(e):
                print(f"[get_price] HTTPError: {e}")
            elif 'timed out' in str(e):
                print(f"[get_price] Timeout: {e}")
            else:
                print(f"[get_price] Erro inesperado no download do yfinance: {e}")
                
        if df is not None and not df.empty and 'Close' in df.columns:
            try:
                return float(df['Close'].dropna().iloc[-1])
            except IndexError:
                print(f"[get_price] IndexError: série vazia para {yf_ticker}, ignorando.")
            except Exception as e:
                print(f"[get_price] Erro ao acessar preço para {yf_ticker}: {e}")
            
        return None
    except Exception as e:
        print(f"[get_price] Erro ao buscar {ticker}: {e}")
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
            handle_rate_limit()
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
        now = datetime.now()
        if not force_update and (now - dollar_cache['timestamp']).total_seconds() < 300:
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
        
    obj = PriceCache.query.filter_by(user_id=None, ticker="USDBRL=X").first()
    now = datetime.now()
    
    if obj:
        obj.price = rate
        obj.last_updated = now
    else:
        db.session.add(PriceCache(user_id=None, ticker="USDBRL=X", price=rate, last_updated=now))
        
    db.session.commit()

def update_price_cache_for_all_tickers():
    """
    Atualiza o cache de preços para todos os tickers únicos no sistema.
    Busca tickers de todos os portfolios e do cache existente.
    
    Returns:
        Object: Objeto com informações sobre a operação, incluindo tickers que deram erro "possibly delisted"
    """
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
        handle_rate_limit()
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
    tickers = list(tickers)
    result.total_tickers = len(tickers)
    
    if not tickers:
        print('[PRICECACHE] Nenhum ticker encontrado para atualizar.')
        return result

    print(f"[PRICECACHE] Iniciando download de preços para {len(tickers)} ativos únicos...")
    try:
        df = None
        try:
            # Período de 30 dias para evitar problemas de série vazia
            df = yf.download(tickers=tickers, period='30d', group_by='ticker', progress=False, threads=True)
        except Exception as e:
            if 'possibly delisted' in str(e) or 'no price data found' in str(e):
                # Processa os tickers que falharam para identificar os "possibly delisted"
                error_msg = str(e)
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
            elif 'HTTP Error' in str(e):
                print(f"[PRICECACHE] HTTPError: {e}")
            elif 'timed out' in str(e):
                print(f"[PRICECACHE] Timeout: {e}")
            else:
                print(f"[PRICECACHE] Erro inesperado no download do yfinance: {e}")
        
        # Reset pausa se sucesso
        reset_rate_limit()
        
        # Processa os resultados
        process_yfinance_results(df, tickers, result)
        
        # Atualiza o banco conforme as regras de delisted/rate limit
        update_price_cache_db(result.delisted_tickers, result.total_tickers)
        
        return result
        
    except Exception as e:
        print(f'[PRICECACHE] Erro ao atualizar preços dos ativos únicos: {e}')
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
            handle_rate_limit()
        return result

def process_yfinance_results(df, tickers, result=None):
    """
    Processa os resultados do yfinance e atualiza o banco de dados.
    Prioriza o uso do método info para obter preços em tempo real.
    
    Args:
        df (pandas.DataFrame): DataFrame com os preços
        tickers (list): Lista de tickers
        result (object): Objeto opcional para armazenar informações sobre tickers delisted
    """
    BATCH_SIZE = 10
    batch_count = 0
    with pricecache_write_lock:
        for ticker in tickers:
            # Pula tickers que já sabemos que estão delisted
            if result and ticker in result.delisted_tickers:
                continue
                
            # Primeiro tenta obter o preço direto da API info (preço em tempo real)
            price = None
            try:
                ticker_info = yf.Ticker(ticker).info
                # Tenta obter o preço atual ou preço de mercado regular
                price = ticker_info.get('currentPrice') or ticker_info.get('regularMarketPrice')
                if price:
                    print(f"[PRICECACHE] Preço em tempo real obtido para {ticker}: {price}")
            except Exception as e:
                print(f"[PRICECACHE] Erro ao buscar preço em tempo real para {ticker}: {e}")
                # Verifica se é um erro de "possibly delisted"
                if 'possibly delisted' in str(e).lower() and result is not None:
                    print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via info)")
                    result.delisted_tickers.append(ticker)
                    continue
                
            # Se não conseguiu via info, tenta usar o DataFrame do histórico
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
                        # Ticker pode estar delisted se não tem preços históricos
                        if result is not None:
                            result.delisted_tickers.append(ticker)
                            print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via série vazia)")
                except IndexError:
                    print(f"[PRICECACHE] IndexError: série vazia para {ticker}, ignorando.")
                    # Ticker pode estar delisted se gera IndexError
                    if result is not None:
                        result.delisted_tickers.append(ticker)
                        print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via IndexError)")
                except Exception as e:
                    print(f"[PRICECACHE] Erro ao acessar preço para {ticker}: {e}")
                
            if price is not None:
                # Sempre salva o ticker normalizado
                obj = PriceCache.query.filter_by(user_id=None, ticker=ticker).first()
                if obj:
                    obj.price = price
                    obj.last_updated = datetime.now()
                else:
                    db.session.add(PriceCache(
                        user_id=None,
                        ticker=ticker,
                        price=price,
                        last_updated=datetime.now()
                     ))
                batch_count += 1
                if batch_count % BATCH_SIZE == 0:
                    db.session.commit()
            else:
                print(f"[PRICECACHE] Ignorando update/insert para {ticker} pois price=None")
                # Se não conseguimos nenhum preço, pode estar delisted
                if result is not None and ticker not in result.delisted_tickers:
                    result.delisted_tickers.append(ticker)
                    print(f"[PRICECACHE] Ticker {ticker} possivelmente delisted (via price=None)")
        
        db.session.commit()
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