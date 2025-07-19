from datetime import datetime
import json
import yfinance as yf

from extensions.database import db
from models.dividends import DividendsCache, DividendReceiptStatus
from models.portfolio import Portfolio
from utils.ticker_utils import format_ticker
from utils.cache_utils import is_rate_limited, reset_rate_limit, handle_rate_limit

def update_dividends_cache_for_all_users():
    """
    Atualiza o cache de dividendos para todos os usuários.
    Busca os dividendos desde 2023 utilizando o yfinance.
    """
    from models.user import User
    
    # Verifica se está em rate limit
    if is_rate_limited():
        print(f"[RATE LIMIT] Pausando update_dividends_cache_for_all_users devido ao rate limit")
        return
        
    print('[DIVIDENDS] Verificando necessidade de atualização do cache de dividendos...')
    
    users = User.query.all()
    for user in users:
        update_dividends_for_user(user)

def update_dividends_for_user(user):
    """
    Atualiza os dividendos para um usuário específico.
    Versão otimizada para evitar sobrecarga do sistema.
    
    Args:
        user (User): Usuário para atualizar os dividendos
    """
    # Busca o portfólio mais recente do usuário
    portfolio = Portfolio.query.filter_by(user_id=user.id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return
        
    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception:
        return
        
    # Verifica se já atualizou dividendos hoje para este usuário
    today = datetime.now().date()
    last_div = DividendsCache.query.filter_by(user_id=user.id).order_by(DividendsCache.last_updated.desc()).first()
    if last_div and last_div.last_updated.date() >= today:
        print(f"[DIVIDENDS] {user.email} já atualizado hoje, pulando...")
        return  # Já atualizado hoje
        
    # Verifica rate limiting antes de prosseguir
    if is_rate_limited():
        print(f"[DIVIDENDS] Rate limit ativo, pulando {user.email}")
        return
        
    # Prepara o mapa de tickers e quantidades
    # Com YTD, não é necessário limitar drasticamente o número de tickers
    ticker_qty_map = {}
    tickers = []
    
    for asset in portfolio_data:
        ticker_str = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker_str)
        qty = float(asset.get('quantidade', 0))
        ticker_qty_map[final_ticker] = {'ticker': ticker_str, 'quantity': int(qty)}
        tickers.append(final_ticker)
        
    tickers = list(set(tickers))
    dividends_to_insert = []
    
    try:
        # Verifica se está em rate limit antes de tentar
        if is_rate_limited():
            print(f"[DIVIDENDS] Rate limit ativo, pulando atualização para {user.email}")
            return
            
        # Download otimizado: YTD (Year-to-Date) para manter dados atualizados
        # Desde 1º de janeiro do ano atual até hoje
        current_year = datetime.now().year
        recent_start = datetime(current_year, 1, 1)  # 1º de janeiro do ano atual
        
        print(f"[DIVIDENDS] Baixando dividendos YTD para {len(tickers)} tickers desde {recent_start.strftime('%Y-%m-%d')} para {user.email}")
        
        # Download dos dividendos usando yfinance com timeout e sem threads paralelas
        df = yf.download(
            tickers=tickers, 
            start=recent_start.strftime('%Y-%m-%d'), 
            group_by='ticker', 
            actions=True, 
            progress=False, 
            threads=False,  # Desabilitado para evitar sobrecarga
            timeout=45      # Timeout de 45 segundos
        )
        
        # Reset pausa se sucesso
        reset_rate_limit()
        
        # Processa os dividendos de cada ticker com proteção contra dados inconsistentes
        for final_ticker in tickers:
            info = ticker_qty_map.get(final_ticker)
            if not info:
                continue
                
            ticker_str = info['ticker']
            qty = info['quantity']
            
            div_series = None
            
            # Extração mais robusta dos dados de dividendos
            try:
                if len(tickers) == 1:
                    div_series = df['Dividends'] if 'Dividends' in df else None
                else:
                    if (final_ticker, 'Dividends') in df:
                        div_series = df[(final_ticker, 'Dividends')]
                    elif final_ticker in df and 'Dividends' in df[final_ticker]:
                        div_series = df[final_ticker]['Dividends']
            except Exception as e:
                print(f"[DIVIDENDS] Erro ao extrair dividendos para {final_ticker}: {e}")
                continue
            
            if div_series is not None:
                for date, amount in div_series.items():
                    try:
                        # Filtros de qualidade dos dados (YTD - desde início do ano)
                        if amount > 0 and qty > 0 and date >= recent_start:
                            # Verifica se já existe no cache
                            date_obj = date.date() if hasattr(date, 'date') else date
                            exists = DividendsCache.query.filter_by(
                                user_id=user.id, 
                                ticker=ticker_str, 
                                date=date_obj
                            ).first()
                            
                            if not exists:
                                total_value = round(float(amount) * qty, 2)
                                # Valida se o valor é razoável (< R$ 100k por dividendo)
                                if total_value <= 100000:
                                    dividends_to_insert.append(DividendsCache(
                                        user_id=user.id,
                                        ticker=ticker_str,
                                        date=date_obj,
                                        value=total_value,
                                        quantity=qty,
                                        event_type='Dividendo',
                                        last_updated=datetime.now()
                                    ))
                    except Exception as e:
                        print(f"[DIVIDENDS] Erro ao processar dividendo {date}/{amount} para {ticker_str}: {e}")
                        continue
        
        # Salva os novos dividendos no banco com transação protegida
        if dividends_to_insert:
            try:
                # Usa transação explícita para evitar locks
                db.session.bulk_save_objects(dividends_to_insert)
                db.session.commit()
                print(f'[DIVIDENDS] {len(dividends_to_insert)} dividendos inseridos para {user.email}')
            except Exception as e:
                print(f'[DIVIDENDS] Erro ao salvar dividendos para {user.email}: {e}')
                db.session.rollback()
        else:
            print(f'[DIVIDENDS] Nenhum dividendo novo para {user.email}')
    
    except Exception as e:
        print(f'[DIVIDENDS] Erro ao atualizar dividendos para {user.email}: {e}')
        
        # Verifica se é erro de rate limit e ativa proteção
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower() or '429' in str(e):
            print(f'[DIVIDENDS] Rate limit detectado para {user.email}, ativando proteção')
            handle_rate_limit()
        
        # Rollback em caso de erro
        try:
            db.session.rollback()
        except:
            pass

def get_user_dividends(user_id, start_date=None):
    """
    Obtém os dividendos de um usuário.
    
    Args:
        user_id (str): ID do usuário
        start_date (datetime.date, optional): Data inicial para filtrar. Default é 2023-01-01.
        
    Returns:
        list: Lista de dividendos formatados com informação de recebimento
    """
    if start_date is None:
        start_date = datetime(2023, 1, 1).date()
        
    # Busca dividendos do cache
    cache_query = DividendsCache.query.filter(
        DividendsCache.user_id == user_id,
        DividendsCache.date >= start_date
    ).order_by(DividendsCache.date.asc())
    
    dividends = [d.to_dict() for d in cache_query]
    
    # Busca status de recebimento
    receipts = DividendReceiptStatus.query.filter_by(user_id=user_id).all()
    receipt_map = {(r.ticker, r.date): r.received for r in receipts}
    
    # Adiciona informação de recebimento aos dividendos
    for d in dividends:
        key = (d['ticker'], datetime.strptime(d['date'], '%Y-%m-%d').date())
        d['received'] = receipt_map.get(key, True)
    
    return dividends

def set_dividend_receipt_status(user_id, ticker, date, received):
    """
    Atualiza o status de recebimento de um dividendo.
    
    Args:
        user_id (str): ID do usuário
        ticker (str): Código do ticker
        date (str): Data no formato YYYY-MM-DD
        received (bool): Status de recebimento
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    try:
        # Converte a string de data para objeto date
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except Exception:
        return {'error': 'Data inválida'}, 400
        
    # Verifica se existe e atualiza, ou cria um novo registro
    status = DividendReceiptStatus.query.filter_by(
        user_id=user_id, 
        ticker=ticker, 
        date=date_obj
    ).first()
    
    if status:
        status.received = received
    else:
        status = DividendReceiptStatus(
            user_id=user_id, 
            ticker=ticker, 
            date=date_obj, 
            received=received
        )
        db.session.add(status)
        
    db.session.commit()
    return {'success': True}, 200

def get_dividend_receipt_status(user_id):
    """
    Obtém todos os status de recebimento de dividendos de um usuário.
    
    Args:
        user_id (str): ID do usuário
        
    Returns:
        list: Lista de status de recebimento formatados
    """
    receipts = DividendReceiptStatus.query.filter_by(user_id=user_id).all()
    
    result = [
        {'ticker': r.ticker, 'date': r.date.strftime('%Y-%m-%d'), 'received': r.received}
        for r in receipts
    ]
    
    return result