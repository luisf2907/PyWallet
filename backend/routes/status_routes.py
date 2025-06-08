import os
import sys

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, jsonify
from datetime import datetime, timezone
import pytz

# --- NOVA LÓGICA: busca o último update do banco de dados (price_history_cache) ---
from backend.models.price_history_cache import PriceHistoryCache
from backend.extensions.database import db

def get_last_price_update_time():
    cache = PriceHistoryCache.query.order_by(PriceHistoryCache.last_updated.desc()).first()
    if cache and cache.last_updated:
        return cache.last_updated
    return None

# Criação do Blueprint para status
status_bp = Blueprint('status', __name__, url_prefix='/api')

@status_bp.route('/system-status', methods=['GET'])
def system_status():
    """Endpoint para verificar status do sistema."""
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    last_update = get_last_price_update_time()
    if last_update:
        # Garante que last_update também está em America/Sao_Paulo
        if last_update.tzinfo is None:
            last_update = tz.localize(last_update)
        else:
            last_update = last_update.astimezone(tz)
        last_price_update_minutes = (now - last_update).total_seconds() / 60
    else:
        last_price_update_minutes = None
    price_update_in_progress = last_price_update_minutes is not None and last_price_update_minutes < 5
    return jsonify({
        'server_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'price_update': {
            'last_update_minutes_ago': round(last_price_update_minutes, 1) if last_price_update_minutes is not None else None,
            'update_in_progress': price_update_in_progress
        },
        'system_ready': True
    }), 200

@status_bp.route('/status', methods=['GET'])
def status():
    """Endpoint simples para verificar se a API está online."""
    return jsonify({
        'status': 'online',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 200
