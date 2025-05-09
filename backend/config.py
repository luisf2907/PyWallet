import os

class Config:
    """Configuração base para a aplicação PyWallet."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pywallet_secret_key')
    UPLOAD_FOLDER = 'uploads'
    TEMPLATE_FOLDER = 'templates'
    SESSION_COOKIE_SECURE = False  # Permite cookie via HTTP no localhost
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pywallet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_TIMEOUT_MINUTES = 30

class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dicionário com as configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name='default'):
    """Retorna a configuração baseada no ambiente."""
    return config.get(config_name, config['default'])