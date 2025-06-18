"""
Script de recuperação para reiniciar o estado de atualização de preços.
Execute este script quando o sistema ficar muito tempo sem atualização.
"""
import os
import sys
import datetime

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tasks.scheduler import last_price_update_time
from backend.utils.cache_utils import reset_rate_limit

def force_price_update_reset():
    """
    Reseta o estado da atualização de preços para forçar uma nova atualização.
    """
    global last_price_update_time
    
    # Recua o timestamp da última atualização em 2 horas
    print(f"Estado atual: última atualização em {last_price_update_time}")
    
    # Reinicia o estado de rate limit
    reset_rate_limit()
    print("Rate limit resetado.")
    
    # Força a próxima atualização
    from datetime import datetime, timedelta
    last_price_update_time = datetime.now() - timedelta(hours=2)
    print(f"Estado atualizado: última atualização em {last_price_update_time}")
    
    print("Reinicialização concluída. O sistema deve atualizar na próxima execução agendada.")

if __name__ == "__main__":
    print("Iniciando recuperação de emergência...")
    force_price_update_reset()
    print("Recuperação de emergência concluída.")
    print("Reinicie o servidor Flask para aplicar as alterações.")
