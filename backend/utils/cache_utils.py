import threading
from datetime import datetime, timedelta

# Cache global para evolução do portfólio
_evolution_cache = {}
evolution_cache_lock = threading.Lock()

# Cache para cotação do dólar
dollar_cache = {'rate': 5.8187, 'timestamp': datetime(2000, 1, 1)}
dollar_cache_lock = threading.Lock()

# Cache para controle de rate limit
rate_limit_pause = {'until': None, 'hours': 1}
rate_limit_lock = threading.Lock()

# Lock para cache de portfólio
portfolio_cache_lock = threading.Lock()

def get_from_evolution_cache(key):
    """
    Obtém um valor do cache de evolução de portfólio.
    
    Args:
        key (str): Chave para busca no cache
        
    Returns:
        dict: Dados do cache ou None se não encontrado ou expirado
    """
    with evolution_cache_lock:
        if key in _evolution_cache:
            cached = _evolution_cache[key]
            if (datetime.now() - cached['timestamp']).total_seconds() < 120:
                return cached['data']
    return None

def set_evolution_cache(key, data):
    """
    Armazena um valor no cache de evolução de portfólio.
    
    Args:
        key (str): Chave para o armazenamento
        data (dict): Dados a serem armazenados
    """
    with evolution_cache_lock:
        _evolution_cache[key] = {
            'timestamp': datetime.now(),
            'data': data
        }

def clear_evolution_cache_for_user(user_id):
    """
    Limpa o cache de evolução para um usuário específico.
    
    Args:
        user_id (str): ID do usuário
    """
    with evolution_cache_lock:
        keys_to_delete = [k for k in _evolution_cache if k.startswith(f"{user_id}:")]
        for k in keys_to_delete:
            del _evolution_cache[k]
            
def handle_rate_limit(hours=None):
    """
    Configura uma pausa por rate limit.
    
    Args:
        hours (int, optional): Número de horas para pausa. Se None, usa o valor atual incrementado.
    """
    with rate_limit_lock:
        now = datetime.now()
        if hours is not None:
            rate_limit_pause['hours'] = hours
        rate_limit_pause['until'] = now + timedelta(hours=rate_limit_pause['hours'])
        print(f"[RATE LIMIT] yfinance bloqueado. Pausando atualizações por {rate_limit_pause['hours']}h até {rate_limit_pause['until']}")
        # Incrementa o tempo de espera exponencialmente para a próxima pausa
        rate_limit_pause['hours'] *= 2

def is_rate_limited():
    """
    Verifica se o sistema está em pausa por rate limit.
    
    Returns:
        bool: True se estiver em pausa, False caso contrário
    """
    with rate_limit_lock:
        return rate_limit_pause['until'] is not None and datetime.now() < rate_limit_pause['until']

def reset_rate_limit():
    """
    Reseta a pausa por rate limit.
    """
    with rate_limit_lock:
        rate_limit_pause['until'] = None
        rate_limit_pause['hours'] = 1