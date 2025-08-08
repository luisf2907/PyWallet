"""
Middleware para controle de cache
"""
from flask import make_response
from functools import wraps

def no_cache(f):
    """
    Decorator para desabilitar cache em rotas específicas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

def setup_cache_control(app):
    """
    Configura headers de cache para toda a aplicação
    """
    @app.after_request
    def after_request(response):
        # Cache inteligente baseado no tipo de conteúdo e ambiente
        content_type = response.headers.get('Content-Type', '')
        
        # Arquivos estáticos (JS, CSS, imagens) - cache longo
        if content_type.startswith(('application/javascript', 'text/css', 'image/', 'font/')):
            response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 ano
        # HTML - cache curto para permitir atualizações
        elif content_type.startswith('text/html'):
            response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutos
        # APIs JSON - cache muito curto
        elif content_type.startswith('application/json'):
            response.headers['Cache-Control'] = 'public, max-age=60'  # 1 minuto
        # Outros arquivos - sem cache apenas se for desenvolvimento
        else:
            if app.debug:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hora
        
        # CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    return app