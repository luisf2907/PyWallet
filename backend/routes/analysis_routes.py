import os
import sys
from datetime import datetime, timedelta
import json

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify, session

from extensions.database import db
from models.portfolio import Portfolio, PortfolioEvolutionCache
from models.price import PriceCache
from services.price_service import get_cached_dollar_rate
from utils.ticker_utils import format_ticker
from utils.cache_utils import get_from_evolution_cache, set_evolution_cache, is_rate_limited

# Importar o módulo de evolução do portfólio
try:
    from portfolio_evolution import calculate_portfolio_evolution, generate_simulated_evolution
except ImportError:
    from backend.portfolio_evolution import calculate_portfolio_evolution, generate_simulated_evolution

# Criação do Blueprint para análise
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')

@analysis_bp.route('/portfolio-summary', methods=['GET'])
def portfolio_summary():
    """Endpoint para obter o resumo e evolução do portfólio."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    # Busca o portfólio mais recente do usuário
    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return jsonify({'error': 'Portfólio não encontrado'}), 404

    # Parâmetros de período
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Valida o formato das datas
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Limita o período a 3 anos
    max_period = timedelta(days=3 * 365)
    if end_date_obj - start_date_obj > max_period:
        start_date_obj = end_date_obj - max_period
        start_date = start_date_obj.strftime('%Y-%m-%d')
    
    # Carrega os dados do portfólio
    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception as e:
        print(f"Erro ao decodificar os dados do portfólio: {e}")
        return jsonify({'summary': {}, 'assets': [], 'evolution': []}), 200

    # Verificar cache
    cache_key = f"{user_id}:{start_date}:{end_date}"
    cached_data = get_from_evolution_cache(cache_key)
    if cached_data:
        return jsonify(cached_data), 200

    # Verificar rate limit
    is_rate_limited_flag = is_rate_limited()

    # Busca preços do cache
    price_cache = {p.ticker: p.price for p in PriceCache.query.all()}
    exch_rate = get_cached_dollar_rate()

    # Busca preços faltantes
    if not is_rate_limited_flag:
        update_missing_prices(portfolio_data, price_cache)

    # Calcula performance dos ativos
    assets_performance, summary = calculate_assets_performance(portfolio_data, price_cache, exch_rate)

    # Calcula evolução do portfólio
    evolution_list = []
    try:
        if is_rate_limited_flag:
            # Usa cache persistente se estiver em rate limit
            cached = PortfolioEvolutionCache.query.filter_by(user_id=user_id).order_by(PortfolioEvolutionCache.date.asc()).all()
            if cached:
                print("[FALLBACK] Usando cache persistente de evolução devido ao rate limit")
                evolution_list = [c.to_dict() for c in cached]
            else:
                print("[INFO] Sem cache de evolução disponível durante rate limit")
                evolution_list = None
        else:
            # Calcula normalmente
            evolution_list = calculate_portfolio_evolution(
                portfolio_data=portfolio_data,
                start_date=start_date,
                end_date=end_date,
                exchange_rate=exch_rate,
                format_ticker_func=format_ticker
            )
            
        if not evolution_list or len(evolution_list) < 2:
            print("[INFO] Sem dados suficientes para evolução do portfólio.")
            evolution_list = None
    except Exception as e:
        print(f"[ERRO] Erro ao calcular evolução do portfólio: {e}")
        evolution_list = None

    # Monta resposta final
    response_data = {
        'summary': summary,
        'assets': assets_performance,
        'evolution': evolution_list
    }
    
    # Salva no cache
    set_evolution_cache(cache_key, response_data)
    
    return jsonify(response_data), 200

def update_missing_prices(portfolio_data, price_cache):
    """Atualiza preços faltantes do cache."""
    from services.price_service import get_price
    
    missing_tickers = []
    for asset in portfolio_data:
        ticker_orig = asset['ticker'].strip().upper()
        if ticker_orig not in price_cache:
            missing_tickers.append(ticker_orig)
            
    if missing_tickers:
        print(f"Buscando preços para ativos não presentes no cache: {missing_tickers}")
        for ticker in missing_tickers:
            price = get_price(ticker)
            if price is not None:
                price_cache[ticker] = price
                # Atualiza no banco
                obj = PriceCache.query.filter_by(ticker=ticker).first()
                if obj:
                    obj.price = price
                    obj.last_updated = datetime.now()
                    db.session.commit()
                else:
                    db.session.add(PriceCache(
                        user_id=None,
                        ticker=ticker,
                        price=price,
                        last_updated=datetime.now()
                    ))
                    db.session.commit()

def calculate_assets_performance(portfolio_data, price_cache, exch_rate):
    """Calcula a performance dos ativos e retorna resumo."""
    from services.price_service import get_price
    total_invested = 0.0
    total_current_value = 0.0
    assets_performance = []
    
    for asset in portfolio_data:
        ticker_orig = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker_orig)
        try:
            avg_price = float(asset.get('preco_medio', 0))
            quantity = float(asset.get('quantidade', 0))
        except:
            continue

        is_bdr = False
        is_us = False
        if final_ticker.endswith('.SA'):
            if final_ticker.endswith('34.SA') or final_ticker.endswith('35.SA') or final_ticker.endswith('32.SA'):
                is_bdr = True
        else:
            is_us = True

        # Busca preço mais recente do yfinance (ou cache se falhar)
        current_price_original = get_price(ticker_orig) or price_cache.get(ticker_orig) or price_cache.get(final_ticker) or avg_price
        price_cache[ticker_orig] = current_price_original  # Atualiza cache local

        # Atualiza o banco de dados PriceCache sempre que buscar um preço novo
        obj = PriceCache.query.filter_by(ticker=ticker_orig).first()
        if obj:
            if obj.price != current_price_original:
                obj.price = current_price_original
                obj.last_updated = datetime.now()
                db.session.commit()
        else:
            db.session.add(PriceCache(
                user_id=None,
                ticker=ticker_orig,
                price=current_price_original,
                last_updated=datetime.now()
            ))
            db.session.commit()

        if is_us:
            invested_value = avg_price * quantity * exch_rate
            current_value = current_price_original * quantity * exch_rate
        else:
            invested_value = avg_price * quantity
            current_value = current_price_original * quantity

        total_invested += invested_value
        total_current_value += current_value

        return_pct = ((current_value / invested_value) - 1) * 100 if invested_value > 0 else 0

        assets_performance.append({
            'ticker': ticker_orig,
            'final_ticker': final_ticker,
            'avg_price': avg_price,
            'current_price': current_price_original,
            'quantity': quantity,
            'invested_value': invested_value,
            'current_value': current_value,
            'return_pct': return_pct,
            'is_us_ticker': is_us,
            'is_bdr': is_bdr
        })

    # Calcula indicadores gerais
    total_return = total_current_value - total_invested
    total_return_pct = ((total_current_value / total_invested) - 1) * 100 if total_invested > 0 else 0
    cdi_return = 0.1135  # ~11.35% ao ano

    # Identifica melhor e pior ativo
    if assets_performance:
        best = max(assets_performance, key=lambda x: x['return_pct'])
        worst = min(assets_performance, key=lambda x: x['return_pct'])
        best_ticker = best['ticker']
        worst_ticker = worst['ticker']
        best_return_pct = best['return_pct']
        worst_return_pct = worst['return_pct']
    else:
        best_ticker = None
        worst_ticker = None
        best_return_pct = None
        worst_return_pct = None

    # Monta resumo
    summary = {
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'cdi_return_pct': cdi_return * 100,
        'percentage_of_cdi': (total_return_pct / (cdi_return * 100)) * 100 if cdi_return > 0 else 0,
        'best_asset': best_ticker,
        'best_asset_return_pct': best_return_pct,
        'worst_asset': worst_ticker,
        'worst_asset_return_pct': worst_return_pct,
        'updated_at': datetime.now().isoformat()
    }
    
    return assets_performance, summary