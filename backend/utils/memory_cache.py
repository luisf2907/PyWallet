"""
Módulo para implementar cache em memória para melhorar a performance
"""
import time
import threading
import functools
from datetime import datetime, timedelta

# Cache global em memória
_MEMORY_CACHE = {}
_CACHE_LOCK = threading.RLock()

def memory_cache(ttl_seconds=300):
    """
    Decorator para cache em memória com TTL (time-to-live)
    
    Args:
        ttl_seconds (int): Tempo de vida do cache em segundos (padrão: 5 minutos)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gera uma chave única para esta função e seus argumentos
            cache_key = f"{func.__module__}.{func.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
            
            with _CACHE_LOCK:
                # Verifica se o valor está em cache e não expirou
                if cache_key in _MEMORY_CACHE:
                    entry = _MEMORY_CACHE[cache_key]
                    if datetime.now() < entry['expires']:
                        return entry['value']
            
            # Se não estiver em cache ou expirou, executa a função
            result = func(*args, **kwargs)
            
            # Armazena o resultado no cache
            with _CACHE_LOCK:
                _MEMORY_CACHE[cache_key] = {
                    'value': result,
                    'expires': datetime.now() + timedelta(seconds=ttl_seconds)
                }
            
            return result
        return wrapper
    return decorator

def clear_memory_cache():
    """Limpa todo o cache em memória"""
    with _CACHE_LOCK:
        _MEMORY_CACHE.clear()

def clear_memory_cache_pattern(pattern):
    """
    Limpa entradas do cache que correspondem a um padrão
    
    Args:
        pattern (str): Padrão para corresponder às chaves do cache
    """
    with _CACHE_LOCK:
        keys_to_remove = [k for k in _MEMORY_CACHE.keys() if pattern in k]
        for k in keys_to_remove:
            del _MEMORY_CACHE[k]

def clear_expired_cache():
    """Remove entradas expiradas do cache"""
    now = datetime.now()
    with _CACHE_LOCK:
        expired_keys = [k for k, v in _MEMORY_CACHE.items() if v['expires'] < now]
        for k in expired_keys:
            del _MEMORY_CACHE[k]

# Inicia um thread para limpar o cache expirado periodicamente
def _start_cache_cleanup():
    def cleanup_task():
        while True:
            time.sleep(60)  # Verifica a cada minuto
            clear_expired_cache()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

# Inicia a limpeza automática
_start_cache_cleanup()
