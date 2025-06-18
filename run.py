import os
import webbrowser
import threading
import time
import subprocess
import sys
import platform
import shutil
import signal  # Importado para manipulação de sinais no Linux

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Limpa a tela do terminal, funciona em Windows e Linux."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════╗")
    print("║                 Prophit!                  ║")
    print("║      Analisador de Investimentos          ║")
    print("╚═══════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

def serve_frontend():
    """Inicia o servidor frontend, compatível com Windows e Linux."""
    print(f"{Colors.BLUE}Iniciando o servidor frontend...{Colors.ENDC}")

    venv_dir = os.path.abspath('venv')
    if platform.system().lower() == 'windows':
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        if not os.path.exists(python_exe):
            python_exe = os.path.join(venv_dir, 'Scripts', 'python')
    else:
        python_exe = os.path.join(venv_dir, 'bin', 'python')

    original_dir = os.getcwd()
    os.chdir('frontend')
    try:
        # Usa subprocess com shell=False para maior compatibilidade entre sistemas
        process = subprocess.Popen([python_exe, '-m', 'http.server', '8000'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
        print(f"{Colors.GREEN}Servidor frontend iniciado em http://localhost:8000{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Erro ao iniciar o servidor frontend: {e}{Colors.ENDC}")
    finally:
        os.chdir(original_dir)
    
    return process  # Retorna o processo para gerenciamento posterior

def start_backend():
    """Inicia o servidor backend, compatível com Windows e Linux."""
    print(f"{Colors.BLUE}Iniciando o servidor backend...{Colors.ENDC}")
    venv_dir = os.path.abspath('venv')
    if platform.system().lower() == 'windows':
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        if not os.path.exists(python_exe):
            python_exe = os.path.join(venv_dir, 'Scripts', 'python')
    else:
        python_exe = os.path.join(venv_dir, 'bin', 'python')

    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'app.py')
    process = subprocess.Popen(
        [python_exe, backend_path], 
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    print(f"{Colors.GREEN}Servidor backend iniciado em http://localhost:5000{Colors.ENDC}")
    return process  # Retorna o processo para gerenciamento posterior

def setup_signal_handlers(processes):
    """Configura manipuladores de sinais para encerramento limpo.
    Particularmente importante no Linux.
    
    Args:
        processes (list): Lista de processos a serem encerrados
    """
    def signal_handler(sig, frame):
        print(f"\n{Colors.WARNING}Encerrando servidores...{Colors.ENDC}")
        for proc in processes:
            if proc and proc.poll() is None:  # Verifica se o processo ainda está em execução
                if platform.system().lower() == 'windows':
                    # No Windows, usa taskkill para encerrar o processo e seus filhos
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # No Linux, envia SIGTERM para encerrar graciosamente
                    proc.terminate()
                    try:
                        # Espera o processo terminar com timeout
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Se não terminar em 5 segundos, força o encerramento
                        proc.kill()
        sys.exit(0)
    
    # Registra handler para SIGINT (Ctrl+C) e SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    if platform.system().lower() != 'windows':  # SIGTERM não existe no Windows
        signal.signal(signal.SIGTERM, signal_handler)

def main():
    print_header()

    # A PARTIR DAQUI você pode inserir setup de venv, instalação de dependências, etc.
    # Ou chamar a função setup_project_structure(), create_template_files() etc.
    # Mas recomendável já ter rodado 'pip install -r requirements.txt' manualmente.

    # Inicia backend
    backend_process = start_backend()

    # Inicia frontend
    frontend_process = serve_frontend()

    # Configura manipuladores de sinais para encerramento limpo
    setup_signal_handlers([backend_process, frontend_process])

    print(f"Prophit! está rodando!\nFrontend: http://localhost:8000\nBackend: http://localhost:5000\n")
    print("Pressione Ctrl+C para sair.")

    # Mantém processo rodando
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
