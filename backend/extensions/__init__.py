from flask_cors import CORS
from .database import db, init_db

def init_extensions(app):
    """Inicializa todas as extensões da aplicação Flask."""
    # Inicializa o CORS
    CORS(app, supports_credentials=True)
    
    # Inicializa o banco de dados
    init_db(app)
    
    # Cria pastas necessárias se não existirem
    import os
    for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATE_FOLDER']]:
        os.makedirs(folder, exist_ok=True)
        
    return app