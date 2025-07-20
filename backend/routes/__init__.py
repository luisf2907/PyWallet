from flask import Blueprint

# Importação dos blueprints
from .auth_routes import auth_bp
from .portfolio_routes import portfolio_bp
from .dividend_routes import dividend_bp
from .analysis_routes import analysis_bp
from .status_routes import status_bp
from .crypto_routes import crypto_routes

# Lista de todos os blueprints da aplicação
all_blueprints = [
    auth_bp,
    portfolio_bp,
    dividend_bp,
    analysis_bp,
    status_bp,
    crypto_routes
]

def register_blueprints(app):
    """
    Registra todos os blueprints na aplicação Flask.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)
    
    return app