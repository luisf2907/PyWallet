import os
import sys
from datetime import datetime

from flask import Flask, jsonify, send_from_directory

# Configuração do projeto
from config import get_config
# Extensões
from extensions import init_extensions
from extensions.database import db
# Serviços
from services.price_service import load_dollar_from_db
from services.auth_service import create_test_user
# Rotas
from routes import register_blueprints
# Tarefas agendadas
from tasks.scheduler import start_scheduled_tasks

def create_app(config_name='default'):
    """
    Factory para criar a aplicação Flask.
    
    Args:
        config_name (str): Nome da configuração a ser usada
        
    Returns:
        Flask: Instância da aplicação Flask configurada
    """
    app = Flask(__name__, static_folder='static')
    
    # Carregar configuração
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar extensões
    init_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Adicionar hook para verificar atualização do código
    @app.before_request
    def check_code_update():
        try:
            current_file = os.path.abspath(__file__)
            last_modified = os.path.getmtime(current_file)
            print(f"[INFO] Código atualizado pela última vez em: {datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"[ERROR] Não foi possível verificar a atualização do código: {e}")
    
    return app

def init_app():
    """
    Inicializa a aplicação e configura tarefas de inicialização.
    
    Returns:
        Flask: Instância da aplicação Flask configurada
    """
    app = create_app()
    
    with app.app_context():
        # Criar tabelas do banco de dados
        db.create_all()
        
        # Criar usuário de teste
        create_test_user()
        
        # Carregar valor do dólar do banco
        load_dollar_from_db()
        
        # Iniciar tarefas agendadas
        start_scheduled_tasks(app)
    
    return app

# Aplicação global
app = init_app()

# Rota direta de backup para o template
@app.route('/api/template-download-direct', methods=['GET'])
def template_download_direct():
    """Endpoint direto para download do template via Google Drive."""
    from flask import redirect
      # Link direto para o arquivo template no Google Drive
    google_drive_url = 'https://drive.google.com/uc?export=download&id=1W3GI8bGTNxyMdgJ05qEhPUUE_MW1AJFU'
    return redirect(google_drive_url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)