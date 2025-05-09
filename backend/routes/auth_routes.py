"""
Rotas para autenticação de usuários
"""
import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify, session

from services.auth_service import (
    register_user, login_user, logout_user, 
    get_current_user, check_session_timeout
)

# Criação do Blueprint para autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.before_request
def before_request():
    """Middleware para verificar timeout da sessão."""
    result = check_session_timeout()
    if result:
        return jsonify(result[0]), result[1]

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novos usuários."""
    data = request.get_json()
    response, status_code = register_user(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password')
    )
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários."""
    data = request.get_json()
    response, status_code = login_user(
        email=data.get('email'),
        password=data.get('password')
    )
    return jsonify(response), status_code

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para logout de usuários."""
    response, status_code = logout_user()
    return jsonify(response), status_code

@auth_bp.route('/user', methods=['GET'])
def get_user():
    """Endpoint para obter informações do usuário atual."""
    response, status_code = get_current_user()
    return jsonify(response), status_code