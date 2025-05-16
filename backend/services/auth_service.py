import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, jsonify

from extensions.database import db
from models.user import User
from models.portfolio import Portfolio

# Conjunto de IDs de usuários ativos
active_user_ids = set()

# Limite de sessão em minutos
SESSION_TIMEOUT_MINUTES = 30

def register_user(name, email, password):
    """
    Registra um novo usuário no sistema.
    
    Args:
        name (str): Nome do usuário
        email (str): Email do usuário (deve ser único)
        password (str): Senha do usuário
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    # Validação dos dados
    if not name or not email or not password:
        return {'error': 'Dados incompletos'}, 400
        
    email = email.strip().lower()
    
    # Verifica se o email já está cadastrado
    if User.query.filter_by(email=email).first():
        return {'error': 'Email já cadastrado'}, 400
    
    # Cria o novo usuário
    user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    # Salva no banco de dados
    db.session.add(user)
    db.session.commit()
    
    return {'message': 'Usuário cadastrado com sucesso', 'user_id': user.id}, 201

def login_user(email, password):
    """
    Realiza o login de um usuário.
    
    Args:
        email (str): Email do usuário
        password (str): Senha do usuário
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    # Validação dos dados
    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400
        
    email = email.strip().lower()
    
    # Busca o usuário pelo email
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {'error': 'Credenciais incorretas'}, 401
    
    # Inicia a sessão
    print(f"[AUTH] Iniciando sessão para usuário {email} (ID: {user.id})")
    session.clear()  # Limpa qualquer sessão existente primeiro
    session.permanent = True  # Torna a sessão permanente
    session['user_id'] = user.id
    session['last_activity'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    session['authenticated'] = True
    
    # Adiciona usuário à lista de ativos
    active_user_ids.add(user.id)
    
    # Verifica se o usuário tem portfólio
    has_portfolio = Portfolio.query.filter_by(user_id=user.id).first() is not None
    
    print(f"[AUTH] Sessão iniciada. Conteúdo: {session}")
    
    return {
        'message': 'Login realizado com sucesso',
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'has_portfolio': has_portfolio
    }, 200

def logout_user():
    """
    Realiza o logout do usuário atual.
    
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    user_id = session.pop('user_id', None)
    if user_id:
        active_user_ids.discard(user_id)
        
    return {'message': 'Logout realizado com sucesso'}, 200

def get_current_user():
    """
    Obtém as informações do usuário atualmente autenticado.
    
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Usuário não autenticado'}, 401
    
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404
    
    has_portfolio = Portfolio.query.filter_by(user_id=user_id).first() is not None
    
    return {'id': user.id, 'name': user.name, 'email': user.email, 'has_portfolio': has_portfolio}, 200

def check_session_timeout():
    """
    Verifica se a sessão do usuário expirou por inatividade.
    
    Returns:
        tuple or None: (dict, int) se a sessão expirou, None caso contrário
    """
    user_id = session.get('user_id')
    if user_id:
        now = datetime.utcnow()
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%dT%H:%M:%S')
            if (now - last_activity) > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                session.clear()
                return {'error': 'Sessão expirada. Faça login novamente.'}, 401
        
        # Atualiza o timestamp da última atividade
        session['last_activity'] = now.strftime('%Y-%m-%dT%H:%M:%S')
    
    return None

def create_test_user():
    """
    Cria um usuário de teste se não existir.
    """
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
    
    return test_user