"""
Script para verificar e corrigir o estado do agendador do APScheduler.
"""
import os
import sys

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_scheduler_status():
    """
    Verifica o status atual do agendador e mostra informações úteis.
    """
    from backend.tasks.scheduler import scheduler, last_price_update_time
    from datetime import datetime
    import pytz
    
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    
    print("\n===== Status do Agendador =====")
    
    if scheduler:
        print(f"Scheduler está ativo: {scheduler.running}")
        
        # Listar todas as tarefas
        print("\nTarefas agendadas:")
        for job in scheduler.get_jobs():
            print(f"- ID: {job.id}")
            print(f"  Próxima execução: {job.next_run_time}")
            print(f"  Trigger: {job.trigger}")
            print(f"  Max instâncias: {job.max_instances}")
            
        # Verificar execuções atuais
        print("\nExecuções em andamento:")
        if hasattr(scheduler, '_executors'):
            for executor_name, executor in scheduler._executors.items():
                if hasattr(executor, '_threads') and executor._threads:
                    print(f"- Executor '{executor_name}': {len(executor._threads)} threads ativas")
                    for thread_id, thread_info in executor._threads.items():
                        print(f"  - Thread {thread_id}: {thread_info}")
                else:
                    print(f"- Executor '{executor_name}': Sem threads ativas")
    else:
        print("Scheduler não está inicializado!")
    
    # Verificar estado da última atualização
    time_diff = (now - last_price_update_time).total_seconds() / 60
    print(f"\nÚltima atualização: {last_price_update_time}")
    print(f"Tempo desde a última atualização: {time_diff:.1f} minutos")
    
    # Verificar se há problemas de rate limit
    from backend.utils.cache_utils import is_rate_limited, rate_limit_pause
    if is_rate_limited():
        print(f"\nSistema está em pause por rate limit até: {rate_limit_pause['until']}")
        print(f"Horas de espera configuradas: {rate_limit_pause['hours']}")
    else:
        print("\nSistema não está em pause por rate limit")
    
    print("\n=========================")

def fix_scheduler_issues():
    """
    Tenta corrigir problemas comuns do agendador.
    """
    from backend.tasks.scheduler import last_price_update_time
    from datetime import datetime, timedelta
    
    print("\n===== Tentando corrigir problemas =====")
    
    # Resetar o timestamp da última atualização
    old_timestamp = last_price_update_time
    global last_price_update_time
    last_price_update_time = datetime.now() - timedelta(minutes=35)
    print(f"Timestamp de última atualização resetado: {old_timestamp} -> {last_price_update_time}")
    
    # Resetar o estado de rate limit
    from backend.utils.cache_utils import reset_rate_limit
    reset_rate_limit()
    print("Estado de rate limit resetado")
    
    # Reiniciar o scheduler se necessário
    from backend.tasks.scheduler import scheduler
    if scheduler and scheduler.running:
        try:
            scheduler.shutdown()
            print("Scheduler desligado")
        except Exception as e:
            print(f"Erro ao desligar scheduler: {e}")
    
    # Iniciamos um novo scheduler
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        from backend.tasks.scheduler import start_scheduler
        start_scheduler(app)
        print("Novo scheduler iniciado")
    
    print("\nOperações de correção concluídas.")
    print("IMPORTANTE: Você deve reiniciar o servidor Flask para que as alterações façam efeito!")
    
if __name__ == "__main__":
    check_scheduler_status()
    
    response = input("\nDeseja tentar corrigir problemas? (s/n): ")
    if response.lower() == 's':
        fix_scheduler_issues()
    else:
        print("Nenhuma alteração foi feita.")
