import os
import sys
import re
import uuid
import random
import json
import time
import threading
from datetime import datetime, timedelta, time as dt_time

import pandas as pd
import numpy as np
import yfinance as yf
import pytz

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Importar o módulo de evolução do portfólio
from portfolio_evolution import calculate_portfolio_evolution, generate_simulated_evolution

# =============================================================================
# Configurações do Flask e Banco de Dados
# =============================================================================
app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pywallet_secret_key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATE_FOLDER'] = 'templates'
app.config['SESSION_COOKIE_SECURE'] = False  # Permite cookie via HTTP no localhost

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pywallet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

# Cria pastas se não existirem
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATE_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# =============================================================================
# Locks Globais para Cache
# =============================================================================
portfolio_cache_lock = threading.Lock()
evolution_cache_lock = threading.Lock()
_evolution_cache = {}  # Cache global para evolução do portfólio

# =============================================================================
# Cache para cotação do dólar (USDBRL=X)
# =============================================================================
dollar_cache = {'rate': 5.8187, 'timestamp': datetime(2000, 1, 1)}
dollar_cache_lock = threading.Lock()

def get_cached_dollar_rate():
    with dollar_cache_lock:
        now = datetime.now()
        if (now - dollar_cache['timestamp']).total_seconds() < 600:
            return dollar_cache['rate']
        rate = get_price("USDBRL=X")
        if rate and rate > 0:
            dollar_cache['rate'] = rate
            dollar_cache['timestamp'] = now
            return rate
        return dollar_cache['rate']

# =============================================================================
# Modelos do Banco de Dados
# =============================================================================
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON string com os ativos (dados originais)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False)
    cached_prices = db.Column(db.Text, nullable=True)  # JSON string com preços atualizados
    cache_timestamp = db.Column(db.DateTime, nullable=True)

# =============================================================================
# Helpers para yfinance
# =============================================================================
def get_price(ticker, formatar=True):
    """
    Busca o preço atual de um ticker via yfinance.
    Se for um ativo brasileiro (sem separadores), adiciona ".SA" ao final.
    """
    def is_us_stock(t):
        return re.fullmatch(r"[A-Z]{1,5}", t.strip().upper()) is not None

    def format_ticker_local(t):
        if '=' in t:
            return t
        if '.' in t:
            return t
        if not is_us_stock(t):
            return t + '.SA'
        return t

    try:
        yf_ticker = format_ticker_local(ticker) if formatar else ticker
        df = yf.download(yf_ticker, period="5d", interval="1d", progress=False)
        if not df.empty and 'Close' in df.columns:
            return float(df['Close'].dropna().iloc[-1])
        tinfo = yf.Ticker(yf_ticker).info
        return float(tinfo.get('regularMarketPrice') or tinfo.get('currentPrice') or 0)
    except Exception as e:
        print(f"[get_price] Erro ao buscar {ticker}: {e}")
        return None

def format_ticker(ticker):
    """
    Adiciona '.SA' se for ticker BR (sem ponto ou '='); senão retorna o original.
    """
    ticker = ticker.strip().upper()
    if '=' in ticker:
        return ticker
    if '.' in ticker:
        return ticker
    if not re.fullmatch(r'[A-Z]{1,5}', ticker):
        return ticker + '.SA'
    return ticker

# =============================================================================
# Checar se o mercado está aberto
# =============================================================================
def is_market_open():
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    weekday = now.weekday()  # 0=Segunda,6=Domingo
    current_time = now.time()

    if weekday >= 5:
        return False

    # B3: 10:00 - 17:55
    b3_open_time = dt_time(10, 0)
    b3_close_time = dt_time(17, 55)
    # NYSE (aproximado, em horário de Brasília)
    ny_open_time_br = dt_time(10, 30)
    ny_close_time_br = dt_time(17, 0)

    is_b3_open = b3_open_time <= current_time <= b3_close_time
    is_nyse_open = ny_open_time_br <= current_time <= ny_close_time_br
    return is_b3_open or is_nyse_open

# =============================================================================
# Thread de atualização de preços
# =============================================================================
def update_all_portfolios():
    last_market_status = None  # None, True (aberto) ou False (fechado)
    while True:
        market_is_open_flag = is_market_open()
        if market_is_open_flag:
            if last_market_status is False:
                print("Mercado abriu. Atualizando preços...")
            last_market_status = True
            with app.app_context():
                portfolios = Portfolio.query.all()
                for portfolio in portfolios:
                    try:
                        portfolio_data = json.loads(portfolio.data)
                    except Exception as e:
                        print(f"Erro ao decodificar o portfólio ID {portfolio.id}: {e}")
                        continue
                    updated_prices = {}
                    for asset in list(portfolio_data):
                        ticker_orig = asset['ticker'].strip().upper()
                        final_ticker = format_ticker(ticker_orig)
                        price = get_price(final_ticker)
                        updated_prices[ticker_orig] = price
                    # Protege a escrita do cache com lock
                    with portfolio_cache_lock:
                        portfolio.cached_prices = json.dumps(updated_prices)
                        portfolio.cache_timestamp = datetime.now()
                        db.session.commit()
                        print(f"Portfólio (ID: {portfolio.id}) atualizado em {portfolio.cache_timestamp}")
            time.sleep(60)
        else:
            if last_market_status != False:
                print("Mercado fechado, não atualizando preços.")
                last_market_status = False
            time.sleep(600)  # 10 minutos

# =============================================================================
# Endpoints de Autenticação
# =============================================================================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Dados incompletos'}), 400

    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    user = User(
        id=str(uuid.uuid4()),
        name=data['name'],
        email=email,
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuário cadastrado com sucesso', 'user_id': user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    email = data['email'].strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Credenciais incorretas'}), 401

    session['user_id'] = user.id
    has_portfolio = Portfolio.query.filter_by(user_id=user.id).first() is not None
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'has_portfolio': has_portfolio
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@app.route('/api/user', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    has_portfolio = Portfolio.query.filter_by(user_id=user_id).first() is not None
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'has_portfolio': has_portfolio})

# =============================================================================
# Endpoint de Taxa de Câmbio
# =============================================================================
@app.route('/api/exchange-rate', methods=['GET'])
def exchange_rate():
    rate = get_cached_dollar_rate()
    return jsonify({'rate': rate}), 200

# =============================================================================
# Endpoint Upload
# =============================================================================
@app.route('/api/upload-portfolio', methods=['POST'])
def upload_portfolio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400

    if not file.filename.endswith(('.csv', '.xlsx')):
        return jsonify({'error': 'Formato de arquivo não suportado. Use CSV ou XLSX'}), 400

    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(file.filename)[1]}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Carregar arquivo CSV ou XLSX
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(filepath)
                if df.shape[1] >= 3:
                    cols = df.columns.str.lower()
                    if any(col in ['código', 'ticker', 'ativo'] for col in cols):
                        col_ticker = next((i for i, col in enumerate(cols) if col in ['código', 'ticker', 'ativo']), 0)
                        col_price = next((i for i, col in enumerate(cols) if col in ['preço', 'medio', 'médio']), 1)
                        col_qty = next((i for i, col in enumerate(cols) if col in ['qtd', 'quantidade', 'quant']), 2)
                        df = df.iloc[:, [col_ticker, col_price, col_qty]]
                        df.columns = ['ticker', 'preco_medio', 'quantidade']
                    else:
                        df = df.iloc[:, :3]
                        df.columns = ['ticker', 'preco_medio', 'quantidade']
                else:
                    df = pd.read_csv(filepath, sep=';')
                    df = df.iloc[:, :3]
                    df.columns = ['ticker', 'preco_medio', 'quantidade']
            except Exception:
                df = pd.read_csv(filepath, header=None)
                if df.shape[1] >= 3:
                    df = df.iloc[:, :3]
                    df.columns = ['ticker', 'preco_medio', 'quantidade']
                else:
                    raise ValueError("CSV não tem pelo menos 3 colunas")
        else:
            try:
                df = pd.read_excel(filepath)
                if df.shape[1] >= 3:
                    cols = [str(col).lower() for col in df.columns]
                    if any('código' in col or 'ticker' in col or 'ativo' in col for col in cols):
                        col_ticker = next((i for i, col in enumerate(cols) if 'código' in col or 'ticker' in col or 'ativo' in col), 0)
                        col_price = next((i for i, col in enumerate(cols) if 'preço' in col or 'medio' in col or 'médio' in col), 1)
                        col_qty = next((i for i, col in enumerate(cols) if 'qtd' in col or 'quantidade' in col or 'quant' in col), 2)
                        df = df.iloc[:, [col_ticker, col_price, col_qty]]
                        df.columns = ['ticker', 'preco_medio', 'quantidade']
                    else:
                        df = df.iloc[:, :3]
                        df.columns = ['ticker', 'preco_medio', 'quantidade']
            except Exception:
                df = pd.read_excel(filepath, header=None)
                if df.shape[1] >= 3:
                    df = df.iloc[:, :3]
                    df.columns = ['ticker', 'preco_medio', 'quantidade']
                else:
                    raise ValueError("XLSX não tem pelo menos 3 colunas")

        if isinstance(df['ticker'].iloc[0], str) and df['ticker'].iloc[0].lower() in ['código', 'ticker', 'ativo']:
            df = df.iloc[1:].reset_index(drop=True)

        df['ticker'] = df['ticker'].astype(str).str.strip().str.upper()
        df['preco_medio'] = pd.to_numeric(df['preco_medio'], errors='coerce')
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
        if df['preco_medio'].isna().all():
            df['preco_medio'] = df['preco_medio'].astype(str).str.replace(',', '.').astype(float)
        df = df.dropna()
        df = df[df['quantidade'] > 0]
        df['valor_total'] = df['preco_medio'] * df['quantidade']

        portfolio_data = df.to_dict('records')
        portfolio = Portfolio(
            user_id=user_id,
            data=json.dumps(portfolio_data),
            filename=filename
        )
        db.session.add(portfolio)
        db.session.commit()

        return jsonify({
            'message': 'Portfólio carregado com sucesso',
            'portfolio_summary': {
                'total_assets': len(df),
                'total_value': df['valor_total'].sum()
            }
        }), 200

    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500

# =============================================================================
# Endpoint para Distribuição do Portfólio
# =============================================================================
@app.route('/api/portfolio-distribution', methods=['GET'])
def portfolio_distribution():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return jsonify({'error': 'Portfólio não encontrado'}), 404

    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception as e:
        return jsonify({'distribution': []}), 200

    # Otimização: use cache de preços se disponível e recente (até 10 minutos)
    cached = None
    with portfolio_cache_lock:
        if portfolio.cache_timestamp and (datetime.now() - portfolio.cache_timestamp).total_seconds() < 600:
            try:
                cached = json.loads(portfolio.cached_prices)
            except Exception:
                cached = None

    # Se não houver cache, use preço médio do usuário (não chama yfinance em request)
    exch_rate = get_cached_dollar_rate()
    total_invested = 0.0
    dist_map = {}
    for asset in portfolio_data:
        ticker = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker)
        quantity = float(asset.get('quantidade', 0))
        avg_price = float(asset.get('preco_medio', 0))

        if cached and ticker in cached and cached[ticker] is not None:
            current_price = cached[ticker]
        else:
            # Não chama get_price aqui! Usa preço médio como fallback
            current_price = avg_price

        is_us = not final_ticker.endswith('.SA')
        invest = current_price * exch_rate * quantity if is_us else current_price * quantity
        if invest <= 0:
            continue
        total_invested += invest
        if ticker not in dist_map:
            dist_map[ticker] = 0
        dist_map[ticker] += invest

    distribution_list = []
    for tck, val in dist_map.items():
        pct = (val / total_invested) * 100 if total_invested else 0
        distribution_list.append({'ticker': tck, 'percentage': pct})
    distribution_list.sort(key=lambda x: x['percentage'], reverse=True)

    return jsonify({'distribution': distribution_list}), 200

# =============================================================================
# Endpoint para Resumo do Portfólio (inclui evolução)
# =============================================================================
@app.route('/api/portfolio-summary', methods=['GET'])
def portfolio_summary():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return jsonify({'error': 'Portfólio não encontrado'}), 404

    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    max_period = timedelta(days=3 * 365)
    if end_date_obj - start_date_obj > max_period:
        start_date_obj = end_date_obj - max_period
        start_date = start_date_obj.strftime('%Y-%m-%d')
    
    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception as e:
        print(f"Erro ao decodificar os dados do portfólio: {e}")
        return jsonify({'summary': {}, 'assets': [], 'evolution': []}), 200

    if not portfolio_data:
        return jsonify({'summary': {}, 'assets': [], 'evolution': []}), 200

    # Lê o cache protegido pelo lock
    cached = None
    with portfolio_cache_lock:
        if portfolio.cache_timestamp and (datetime.now() - portfolio.cache_timestamp).total_seconds() < 60:
            try:
                cached = json.loads(portfolio.cached_prices)
            except Exception:
                pass

    exch_rate = get_cached_dollar_rate()

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

        if cached and ticker_orig in cached and cached[ticker_orig] is not None:
            current_price_original = cached[ticker_orig]
        else:
            current_price_original = get_price(final_ticker) or 0

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

    total_return = total_current_value - total_invested
    total_return_pct = ((total_current_value / total_invested) - 1) * 100 if total_invested > 0 else 0

    cdi_return = 0.1135
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

    summary = {
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'cdi_return_pct': cdi_return * 100,
        'percentage_of_cdi': (total_return_pct / (cdi_return * 100)) * 100 if cdi_return and cdi_return > 0 else 0,
        'best_asset': best_ticker,
        'best_asset_return_pct': best_return_pct,
        'worst_asset': worst_ticker,
        'worst_asset_return_pct': worst_return_pct,
        'updated_at': datetime.now().isoformat()
    }

    cache_key = f"{user_id}:{start_date}:{end_date}"
    with evolution_cache_lock:
        if cache_key in _evolution_cache:
            cached_entry = _evolution_cache[cache_key]
            if (datetime.now() - cached_entry['timestamp']).total_seconds() < 120:
                return jsonify(cached_entry['data']), 200

    evolution_list = []
    try:
        evolution_list = calculate_portfolio_evolution(
            portfolio_data=portfolio_data,
            start_date=start_date,
            end_date=end_date,
            exchange_rate=exch_rate,
            format_ticker_func=format_ticker
        )
        if len(evolution_list) < 2:
            raise Exception("Dados insuficientes para evolução do portfólio")
    except Exception as e:
        print(f"Erro ao calcular evolução real: {e}")
        print("Gerando dados simulados para evolução do portfólio...")
        evolution_list = generate_simulated_evolution(
            start_date=start_date,
            end_date=end_date,
            start_value=total_invested * 0.95,
            end_value=total_current_value,
            num_points=30
        )

    response_data = {
        'summary': summary,
        'assets': assets_performance,
        'evolution': evolution_list
    }
    
    with evolution_cache_lock:
        _evolution_cache[cache_key] = {
            'timestamp': datetime.now(),
            'data': response_data
        }

    return jsonify(response_data), 200

# =============================================================================
# Endpoint para Proventos
# =============================================================================
@app.route('/api/dividends', methods=['GET'])
def get_dividends():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return jsonify({'error': 'Portfólio não encontrado'}), 404

    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception as e:
        return jsonify({'error': f'Erro ao ler dados do portfólio: {e}'}), 500

    dividends = []
    for asset in portfolio_data:
        ticker_str = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker_str)
        try:
            qty = float(asset.get('quantidade', 0))
            yf_ticker = yf.Ticker(final_ticker)
            df_div = yf_ticker.dividends
            for date, amount in df_div.items():
                if amount > 0 and qty > 0:
                    dividends.append({
                        'ticker': ticker_str,
                        'date': date.strftime('%Y-%m-%d'),
                        'value': round(float(amount) * qty, 2),
                        'quantity': int(qty)
                    })
        except Exception as e:
            print(f"[DIVIDENDS] Falha ao buscar {final_ticker}: {e}")
    dividends.sort(key=lambda x: x['date'])
    return jsonify({'dividends': dividends})

# =============================================================================
# Hook para verificar atualização do código (apenas no startup)
# =============================================================================
def print_code_update_info_once():
    try:
        current_file = os.path.abspath(__file__)
        last_modified = os.path.getmtime(current_file)
        print(f"[INFO] Código atualizado pela última vez em: {datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"[ERROR] Não foi possível verificar a atualização do código: {e}")

# Proteção adicional para evitar modificações durante iteração
@app.before_request
def protect_cache():
    global _evolution_cache
    with evolution_cache_lock:
        _evolution_cache = dict(_evolution_cache)

# =============================================================================
# Inicialização
# =============================================================================
if __name__ == '__main__':
    print_code_update_info_once()
    with app.app_context():
        db.create_all()
        test_email = 'root@example.com'
        test_user = User.query.filter_by(email=test_email).first()
        if not test_user:
            test_user = User(
                id=str(uuid.uuid4()),
                name='Root User',
                email=test_email,
                password_hash=generate_password_hash('password123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("Usuário de teste criado: root@example.com / password123")

    updater_thread = threading.Thread(target=update_all_portfolios, daemon=True)
    updater_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5000)
