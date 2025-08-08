import os
import sys
from datetime import datetime

from flask import Flask, jsonify, send_from_directory

# Configuração do projeto
from config import get_config
# Extensões
from extensions import init_extensions
from extensions.database import db
# Middleware
from middleware.cache_control import setup_cache_control
# Serviços
from services.price_service import load_dollar_from_db
from services.auth_service import create_test_user
# Rotas
from routes import register_blueprints
# Tarefas agendadas
from tasks.scheduler import start_scheduled_tasks

# Redireciona stdout e stderr para o arquivo de log (sobrescreve a cada execução)
log_path = os.path.join(os.path.dirname(__file__), 'logs', 'terminal_log.txt')
try:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    sys.stdout = open(log_path, 'w', encoding='utf-8', buffering=1)
    sys.stderr = sys.stdout
except Exception as e:
    print(f'[LOGGING] Falha ao redirecionar stdout/stderr para log: {e}')

def create_app(config_name='default'):
    """
    Factory para criar a aplicação Flask.
    
    Args:
        config_name (str): Nome da configuração a ser usada
        
    Returns:
        Flask: Instância da aplicação Flask configurada
    """
    # Evita que Flask registre rota estática na raiz (que causava 404 em /login, /dashboard etc.)
    app = Flask(__name__, static_folder=None)
    
    # Diretório do build do frontend
    app.config['FRONTEND_DIST_DIR'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend-react/dist'))
    
    # Carregar configuração
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar extensões
    init_extensions(app)
    
    # Configurar controle de cache
    setup_cache_control(app)
    
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

        # REMOVIDO: FORÇA ATUALIZAÇÃO DE TODOS OS PREÇOS NO INÍCIO
        # from services.price_service import update_price_cache_for_all_tickers
        # print('[STARTUP] Atualizando todos os preços do PriceCache...')
        # update_price_cache_for_all_tickers(app=app)
        # print('[STARTUP] Atualização de preços concluída.')        # Iniciar tarefas agendadas
        start_scheduled_tasks(app)
        # (Desativado: scheduler removido)
    return app

# Aplicação global
app = init_app()

# Servir arquivos estáticos do build do Vite (assets)
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    dist_dir = app.config.get('FRONTEND_DIST_DIR')
    assets_dir = os.path.join(dist_dir, 'assets')
    return send_from_directory(assets_dir, filename)

# Favicon (opcional)
@app.route('/favicon.ico')
def favicon():
    dist_dir = app.config.get('FRONTEND_DIST_DIR')
    try:
        return send_from_directory(dist_dir, 'favicon.ico')
    except Exception:
        # Se não existir, retorna 404 padrão
        from flask import abort
        abort(404)

# Rota para servir o frontend React
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    """Serve o frontend React para todas as rotas que não são API."""
    if path.startswith('api/'):
        # Se for uma rota de API que não existe, retorna 404
        from flask import abort
        abort(404)
    
    # Para todas as outras rotas, serve o index.html do React
    dist_dir = app.config.get('FRONTEND_DIST_DIR')
    return send_from_directory(dist_dir, 'index.html')

# Rota direta de backup para o template
@app.route('/api/template-download-direct', methods=['GET'])
def template_download_direct():
    """Endpoint direto para download do template via Google Drive."""
    from flask import redirect
      # Link direto para o arquivo template no Google Drive
    google_drive_url = 'https://drive.google.com/uc?export=download&id=1W3GI8bGTNxyMdgJ05qEhPUUE_MW1AJFU'
    return redirect(google_drive_url)

if __name__ == '__main__':
    # Rodando sem reloader para evitar duplicação de processos
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)