from flask_cors import CORS
from .database import db, init_db

def init_extensions(app):
    """Inicializa todas as extensões da aplicação Flask."""
    # Inicializa o CORS com configurações mais específicas
    CORS(app, 
         supports_credentials=True,
         resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000", "*"]}},
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type", "Authorization"],
         max_age=600)
    
    # Inicializa o banco de dados
    init_db(app)
    
    # Cria pastas necessárias se não existirem
    import os
    for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATE_FOLDER']]:
        os.makedirs(folder, exist_ok=True)
        
    return app