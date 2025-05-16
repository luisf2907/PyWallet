"""
Rotas para gerenciamento de dividendos
"""
import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify, session

from services.dividend_service import (
    get_user_dividends, set_dividend_receipt_status,
    get_dividend_receipt_status
)

# Criação do Blueprint para dividendos
dividend_bp = Blueprint('dividends', __name__, url_prefix='/api')

@dividend_bp.route('/dividends', methods=['GET'])
def get_dividends():
    """Endpoint para obter os dividendos do usuário."""
    print(f"[DIVIDENDS] Sessão atual: {session}")
    user_id = session.get('user_id')
    if not user_id:
        print("[DIVIDENDS] Erro: Usuário não autenticado na sessão!")
        return jsonify({'error': 'Usuário não autenticado'}), 401

    print(f"[DIVIDENDS] Buscando dividendos para usuário {user_id}")
    dividends = get_user_dividends(user_id)
    return jsonify({'dividends': dividends})

@dividend_bp.route('/dividend-receipt', methods=['POST'])
def set_dividend_receipt():
    """Endpoint para atualizar o status de recebimento de um dividendo."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    ticker = data.get('ticker')
    date = data.get('date')
    received = data.get('received')
    
    if not ticker or not date or received is None:
        return jsonify({'error': 'Dados incompletos'}), 400
    
    response, status_code = set_dividend_receipt_status(user_id, ticker, date, received)
    return jsonify(response), status_code

@dividend_bp.route('/dividend-receipt', methods=['GET'])
def get_dividend_receipts():
    """Endpoint para obter o status de recebimento dos dividendos."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    receipts = get_dividend_receipt_status(user_id)
    return jsonify({'receipts': receipts})

@dividend_bp.route('/debug/dividends-raw', methods=['GET'])
def debug_dividends_raw():
    """Endpoint de debug para ver dividendos brutos do banco."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    all_divs = get_user_dividends(user_id)
    return jsonify({'raw_dividends': all_divs})