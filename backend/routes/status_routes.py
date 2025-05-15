import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, jsonify
from datetime import datetime

# Acesso ao scheduler para verificar status das atualizações
from tasks.scheduler import last_price_update_time

# Criação do Blueprint para status
status_bp = Blueprint('status', __name__, url_prefix='/api')

@status_bp.route('/system-status', methods=['GET'])
def system_status():
    """Endpoint para verificar status do sistema."""
    now = datetime.now()
    
    # Calcula o tempo desde a última atualização de preços
    last_price_update_minutes = (now - last_price_update_time).total_seconds() / 60
    
    # Verifica se uma atualização está em andamento (menos de 5 minutos)
    price_update_in_progress = last_price_update_minutes < 5
    
    return jsonify({
        'server_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'price_update': {
            'last_update_minutes_ago': round(last_price_update_minutes, 1),
            'update_in_progress': price_update_in_progress
        },
        'system_ready': True
    }), 200
