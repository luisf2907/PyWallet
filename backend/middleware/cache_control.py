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
        # Para arquivos estáticos (.js, .css, .html), não usar cache em desenvolvimento
        if response.headers.get('Content-Type', '').startswith(('text/html', 'application/javascript', 'text/css')):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    return app