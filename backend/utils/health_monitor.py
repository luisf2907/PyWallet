"""
Monitor de saúde do backend PyWallet
Detecta problemas de performance e crashes do sistema
"""
import psutil
import time
import threading
from datetime import datetime
import logging

# Configuração do logging
logging.basicConfig(
    filename='logs/health_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HealthMonitor:
    """Monitor de saúde do sistema"""
    
    def __init__(self, app=None):
        self.app = app
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Inicia o monitoramento em thread separada"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[HEALTH] Monitor de saúde iniciado")
        
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[HEALTH] Monitor de saúde parado")
        
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring:
            try:
                self._check_system_health()
                time.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logging.error(f"Erro no monitor de saúde: {e}")
                time.sleep(60)
                
    def _check_system_health(self):
        """Verifica a saúde do sistema"""
        try:
            # Verifica uso de memória
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Log se uso de memória > 80%
            if memory.percent > 80:
                msg = f"ALERTA: Uso de memória alto: {memory.percent:.1f}%"
                print(f"[HEALTH] {msg}")
                logging.warning(msg)
                
            # Log se CPU > 90%
            if cpu_percent > 90:
                msg = f"ALERTA: Uso de CPU alto: {cpu_percent:.1f}%"
                print(f"[HEALTH] {msg}")
                logging.warning(msg)
                
            # Verifica conexões de rede (yfinance)
            connections = psutil.net_connections()
            external_connections = [c for c in connections if c.raddr and c.raddr.ip not in ['127.0.0.1', '::1']]
            
            if len(external_connections) > 50:
                msg = f"ALERTA: Muitas conexões externas: {len(external_connections)}"
                print(f"[HEALTH] {msg}")
                logging.warning(msg)
                
            # Log estatísticas normais (a cada 10 minutos)
            current_minute = datetime.now().minute
            if current_minute % 10 == 0:
                msg = f"Status: CPU {cpu_percent:.1f}%, RAM {memory.percent:.1f}%, Conexões {len(external_connections)}"
                print(f"[HEALTH] {msg}")
                logging.info(msg)
                
        except Exception as e:
            logging.error(f"Erro ao verificar saúde do sistema: {e}")
            
    def log_operation_start(self, operation_name):
        """Log do início de uma operação crítica"""
        msg = f"OPERAÇÃO INICIADA: {operation_name}"
        print(f"[HEALTH] {msg}")
        logging.info(msg)
        return time.time()
        
    def log_operation_end(self, operation_name, start_time):
        """Log do fim de uma operação crítica"""
        duration = time.time() - start_time
        msg = f"OPERAÇÃO CONCLUÍDA: {operation_name} em {duration:.2f}s"
        print(f"[HEALTH] {msg}")
        logging.info(msg)
        
        # Alerta se operação demorou muito
        if duration > 300:  # 5 minutos
            alert = f"ALERTA: Operação {operation_name} demorou {duration:.1f}s (>5min)"
            print(f"[HEALTH] {alert}")
            logging.warning(alert)

# Instância global
health_monitor = HealthMonitor()

def start_health_monitoring(app):
    """Inicia o monitoramento de saúde"""
    health_monitor.app = app
    health_monitor.start_monitoring()
    
def stop_health_monitoring():
    """Para o monitoramento de saúde"""
    health_monitor.stop_monitoring()
