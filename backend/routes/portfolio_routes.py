import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify, session, send_from_directory, current_app

from services.portfolio_service import (
    upload_portfolio, get_portfolio_distribution,
    register_transaction
)
from services.price_service import get_cached_dollar_rate

# Criação do Blueprint para portfólio
portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api')

@portfolio_bp.route('/upload-portfolio', methods=['POST'])
def upload_portfolio_route():
    """Endpoint para fazer upload de arquivo de portfólio."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
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

@portfolio_bp.route('/exchange-rate', methods=['GET'])
def exchange_rate():
    """Endpoint para obter a taxa de câmbio USD/BRL."""
    rate = get_cached_dollar_rate()
    return jsonify({'rate': rate}), 200

@portfolio_bp.route('/download-template', methods=['GET'])
def download_template():
    """Endpoint para baixar o template de portfólio."""
    template_path = os.path.join(current_app.root_path, 'templates')
    return send_from_directory(template_path, 'template.xlsx', as_attachment=True)