import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, request, jsonify, session, send_from_directory, current_app

from services.portfolio_service import (
    upload_portfolio, get_portfolio_distribution,
    register_transaction, overwrite_portfolio_manual
)
from services.price_service import get_cached_dollar_rate
# Criação do Blueprint para portfólio
portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api')

@portfolio_bp.route('/upload-portfolio', methods=['POST'])
def upload_portfolio_route():
    """Endpoint para fazer upload de arquivo de portfólio ou sobrescrever com dados manuais."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verifica se é uma requisição de upload de arquivo ou dados JSON
    if request.is_json:
        # Importação manual via tabela
        data = request.get_json()
        ativos = data.get('ativos', [])
        
        response, status_code = overwrite_portfolio_manual(user_id, ativos)
    else:
        # Upload de arquivo
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
            
        file = request.files['file']
        response, status_code = upload_portfolio(user_id, file)
    
    return jsonify(response), status_code

@portfolio_bp.route('/portfolio-distribution', methods=['GET'])
def portfolio_distribution():
    """Endpoint para obter a distribuição do portfólio."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    response, status_code = get_portfolio_distribution(user_id)
    return jsonify(response), status_code

@portfolio_bp.route('/register-aporte', methods=['POST'])
def register_aporte():
    """Endpoint para registrar um aporte (compra/venda)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    data = request.get_json()
    tipo = data.get('tipo')
    ticker = data.get('ticker', '').strip().upper()
    preco = float(data.get('preco', 0))
    quantidade = int(data.get('quantidade', 0))
    
    response, status_code = register_transaction(
        user_id=user_id,
        tipo=tipo,
        ticker=ticker,
        preco=preco,
        quantidade=quantidade
    )
    
    return jsonify(response), status_code

@portfolio_bp.route('/register-aporte-batch', methods=['POST'])
def register_aporte_batch():
    """Endpoint para registrar múltiplos aportes/retiradas de uma vez."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    ativos = data.get('ativos', [])
    
    if not ativos:
        return jsonify({'error': 'Nenhum ativo informado'}), 400
    
    try:
        # Usar o serviço de batch para maior consistência
        from services.batch_portfolio_service import batch_update_portfolio
        print(f"Redirecionando para serviço batch_update_portfolio com {len(ativos)} ativos")
        response, status_code = batch_update_portfolio(user_id, ativos)
        return jsonify(response), status_code
    except Exception as e:
        import traceback
        print(f"Erro ao processar register-aporte-batch: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Erro ao processar: {str(e)}'}), 500

@portfolio_bp.route('/exchange-rate', methods=['GET'])
def exchange_rate():
    """Endpoint para obter a taxa de câmbio USD/BRL."""
    rate = get_cached_dollar_rate()
    return jsonify({'rate': rate}), 200

@portfolio_bp.route('/batch-update', methods=['POST'])
def batch_update():
    """Endpoint para registrar múltiplos aportes/retiradas de uma vez sem sobrescrever o portfólio."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    data = request.get_json()
    ativos = data.get('ativos', [])
    
    # Log para depurar
    print(f"Requisição de batch-update recebida: {len(ativos)} ativos")
    for i, ativo in enumerate(ativos):
        print(f"Ativo {i+1}: {ativo}")
    
    try:
        # Importar aqui para evitar problemas de importação circular
        from services.batch_portfolio_service import batch_update_portfolio
        response, status_code = batch_update_portfolio(user_id, ativos)
        return jsonify(response), status_code
    except Exception as e:
        import traceback
        print(f"Erro ao processar batch-update: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Erro ao processar: {str(e)}'}), 500

# Endpoint para download de template foi removido, agora o download é feito diretamente do Google Drive

@portfolio_bp.route('/validate-ticker', methods=['POST'])
def validate_ticker():
    """Endpoint para validar se um ticker existe sem modificar o portfólio."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    data = request.get_json()
    ticker = data.get('ticker', '').strip().upper()
    
    if not ticker:
        return jsonify({'error': 'Ticker não informado'}), 400
    
    # Importa yfinance para verificar se o ticker existe
    try:
        import yfinance as yf
        from utils.ticker_utils import format_ticker, normalize_fractional_ticker
        
        # Normaliza o ticker se for fracionado
        ticker = normalize_fractional_ticker(ticker)
        
        yf_ticker = format_ticker(ticker)
        ticker_info = yf.Ticker(yf_ticker).info
        
        # Verifica se o ticker é válido (tem preço de mercado)
        if ticker_info.get('regularMarketPrice') or ticker_info.get('currentPrice'):
            return jsonify({'isValid': True}), 200
        else:
            return jsonify({'error': 'Ticker não encontrado'}), 404
    except Exception as e:
        current_app.logger.error(f"Erro ao validar ticker {ticker}: {str(e)}")
        return jsonify({'error': 'Ticker não encontrado'}), 404

@portfolio_bp.route('/empresa-update', methods=['POST'])
def empresa_update():
    """Endpoint para alterar posição de uma empresa (compra/venda manual)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    codigo_original = data.get('codigo')
    preco = data.get('preco')
    quantidade = data.get('quantidade')
    tipo_operacao = data.get('tipo_operacao', 'compra')  # Valor padrão é 'compra'
    
    if not codigo_original or preco is None or quantidade is None:
        return jsonify({'error': 'Dados incompletos.'}), 400
    
    # Normaliza o ticker se for fracionado
    from utils.ticker_utils import normalize_fractional_ticker
    codigo = normalize_fractional_ticker(codigo_original)
    
    # Log para debug se houve normalização
    if codigo != codigo_original:
        print(f"Ticker normalizado de {codigo_original} para {codigo} no endpoint empresa-update")
    
    from services.portfolio_service import update_empresa_manual
    result, status = update_empresa_manual(user_id, codigo, preco, quantidade, tipo_operacao)
    
    return jsonify(result), status