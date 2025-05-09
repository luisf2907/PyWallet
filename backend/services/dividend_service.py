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
        
    # Verifica se já atualizou dividendos hoje
    today = datetime.now().date()
    last_div = DividendsCache.query.filter_by(user_id=user.id).order_by(DividendsCache.last_updated.desc()).first()
    if last_div and last_div.last_updated.date() >= today:
        return  # Já atualizado hoje
        
    # Prepara o mapa de tickers e quantidades
    ticker_qty_map = {}
    tickers = []
    
    for asset in portfolio_data:
        ticker_str = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker_str)
        qty = float(asset.get('quantidade', 0))
        ticker_qty_map[final_ticker] = {'ticker': ticker_str, 'quantity': int(qty)}
        tickers.append(final_ticker)
        
    tickers = list(set(tickers))
    start_date = datetime(2023, 1, 1)
    dividends_to_insert = []
    
    try:
        # Download dos dividendos usando yfinance
        df = yf.download(
            tickers=tickers, 
            start=start_date.strftime('%Y-%m-%d'), 
            group_by='ticker', 
            actions=True, 
            progress=False, 
            threads=True
        )
        
        # Reset pausa se sucesso
        reset_rate_limit()
        
        # Processa os dividendos de cada ticker
        for final_ticker in tickers:
            info = ticker_qty_map.get(final_ticker)
            if not info:
                continue
                
            ticker_str = info['ticker']
            qty = info['quantity']
            
            div_series = None
            
            if len(tickers) == 1:
                div_series = df['Dividends'] if 'Dividends' in df else None
            else:
                if (final_ticker, 'Dividends') in df:
                    div_series = df[(final_ticker, 'Dividends')]
                elif final_ticker in df and 'Dividends' in df[final_ticker]:
                    div_series = df[final_ticker]['Dividends']
            
            if div_series is not None:
                for date, amount in div_series.items():
                    if amount > 0 and qty > 0 and date >= start_date:
                        # Verifica se já existe no cache
                        date_obj = date.date() if hasattr(date, 'date') else date
                        exists = DividendsCache.query.filter_by(
                            user_id=user.id, 
                            ticker=ticker_str, 
                            date=date_obj
                        ).first()
                        
                        if not exists:
                            dividends_to_insert.append(DividendsCache(
                                user_id=user.id,
                                ticker=ticker_str,
                                date=date_obj,
                                value=round(float(amount) * qty, 2),
                                quantity=qty,
                                event_type='Dividendo',
                                last_updated=datetime.now()
                            ))
        
        # Salva os novos dividendos no banco
        if dividends_to_insert:
            db.session.bulk_save_objects(dividends_to_insert)
            db.session.commit()
            print(f'[DIVIDENDS] {len(dividends_to_insert)} dividendos inseridos para {user.email}')
    
    except Exception as e:
        print(f'[DIVIDENDS] Erro ao atualizar dividendos para {user.email}: {e}')
        if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
            handle_rate_limit()

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