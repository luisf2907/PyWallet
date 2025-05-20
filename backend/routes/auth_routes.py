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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

def generate_token(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def send_reset_email(to_email, token):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'app.prophit@gmail.com'
    smtp_pass = 'qkuu rcem gxmv yngp'  # Senha de app fixa
    subject = 'Recuperação de senha - Prophit!'
    body = f"""
Olá,

Recebemos uma solicitação para redefinir a senha da sua conta Prophit! associada a este e-mail.
Se você fez essa solicitação, utilize o token abaixo para redefinir sua senha. O token é válido por 5 minutos:

Token: {token}

Se você não solicitou a redefinição de senha, ignore este e-mail. Sua senha permanecerá inalterada e nenhuma ação será tomada.
Dúvidas? Fale conosco pelo e-mail suporte.prophit@gmail.com.

Atenciosamente,
Equipe Prophit!

---
Este é um e-mail automático enviado pelo sistema Prophit!
"""
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"E-mail de recuperação enviado para {to_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    from models.user import User
    from extensions.database import db
    from datetime import datetime, timedelta
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'E-mail é obrigatório.'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'E-mail não cadastrado.'}), 404
    token = generate_token(6)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()
    send_reset_email(user.email, token)
    return jsonify({'message': 'Se o e-mail existir, você receberá instruções para redefinir sua senha.'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    from models.user import User
    from extensions.database import db
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    if not token or not new_password:
        return jsonify({'message': 'Token e nova senha são obrigatórios.'}), 400
    # Token deve ser comparado em maiúsculo
    user = User.query.filter_by(reset_token=token.upper()).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({'message': 'Token inválido ou expirado.'}), 400
    user.password_hash = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    return jsonify({'message': 'Senha redefinida com sucesso!'}), 200