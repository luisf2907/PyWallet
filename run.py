import os
import webbrowser
import threading
import time
import subprocess
import sys
import platform
import shutil

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════╗")
    print("║                 PyWallet                  ║")
    print("║      Analisador de Investimentos          ║")
    print("╚═══════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

def serve_frontend():
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
        subprocess.Popen([python_exe, '-m', 'http.server', '8000'])
        print(f"{Colors.GREEN}Servidor frontend iniciado em http://localhost:8000{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Erro ao iniciar o servidor frontend: {e}{Colors.ENDC}")
    finally:
        os.chdir(original_dir)

def start_backend():
    print(f"{Colors.BLUE}Iniciando o servidor backend...{Colors.ENDC}")
    venv_dir = os.path.abspath('venv')
    if platform.system().lower() == 'windows':
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        if not os.path.exists(python_exe):
            python_exe = os.path.join(venv_dir, 'Scripts', 'python')
    else:
        python_exe = os.path.join(venv_dir, 'bin', 'python')

    subprocess.Popen([python_exe, 'backend/app.py'])
    print(f"{Colors.GREEN}Servidor backend iniciado em http://localhost:5000{Colors.ENDC}")

def main():
    print_header()

    # A PARTIR DAQUI você pode inserir setup de venv, instalação de dependências, etc.
    # Ou chamar a função setup_project_structure(), create_template_files() etc.
    # Mas recomendável já ter rodado 'pip install -r requirements.txt' manualmente.

    # Inicia backend
    start_backend()

    # Inicia frontend
    serve_frontend()

    # Abre navegador automaticamente após 3 segundos
    # Descomente a função abaixo e sua chamada se desejar este comportamento
    # open_browser()

    print(f"PyWallet está rodando!\nFrontend: http://localhost:8000\nBackend: http://localhost:5000\n")
    print("Pressione Ctrl+C para sair.")

    # Mantém processo rodando
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
