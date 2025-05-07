import os
import sys
import time
import subprocess
import webbrowser
import platform

def wait_for_server_start(url, timeout=10):
    """Aguarda o servidor iniciar ou atinge o timeout"""
    import socket
    import time
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def main():
    # Detectar sistema operacional
    is_windows = platform.system() == 'Windows'
    is_server_mode = '--server' in sys.argv
    
    print("╔═══════════════════════════════════════════╗")
    print("║                 PyWallet                   ║")
    print("║      Analisador de Investimentos          ║")
    print("╚═══════════════════════════════════════════╝")
    print("")
    
    # Obter caminho do diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir comandos adequados para o sistema
    python_cmd = 'python' if is_windows else 'python3'
    
    # Iniciar servidor backend (Flask)
    backend_dir = os.path.join(current_dir, 'backend')
    print("Iniciando o servidor backend...")
    
    backend_cmd = [python_cmd, "app.py"]
    if is_windows:
        backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)
    
    backend_url = "http://localhost:5000"
    if wait_for_server_start(backend_url, 10):
        print(f"Servidor backend iniciado em {backend_url}")
    else:
        print(f"Aviso: Não foi possível confirmar que o servidor backend iniciou. Verifique em {backend_url}")
    
    # Iniciar servidor frontend (Python HTTP server)
    frontend_dir = os.path.join(current_dir, 'frontend')
    print("Iniciando o servidor frontend...")
    
    frontend_cmd = [python_cmd, "-m", "http.server", "8000"]
    if is_windows:
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)
    
    frontend_url = "http://localhost:8000"
    if wait_for_server_start(frontend_url, 5):
        print(f"Servidor frontend iniciado em {frontend_url}")
    else:
        print(f"Aviso: Não foi possível confirmar que o servidor frontend iniciou. Verifique em {frontend_url}")
    
    # Abrir navegador automaticamente (apenas no modo desktop)
    if not is_server_mode:
        print("Abrindo o navegador...")
        webbrowser.open(frontend_url)
    
    print("PyWallet está rodando!")
    print(f"Frontend: {frontend_url}")
    print(f"Backend: {backend_url}")
    print("")
    print("Pressione Ctrl+C para sair.")
    
    try:
        # Manter o programa rodando até Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando PyWallet...")
    finally:
        # Finalizar processos ao encerrar
        try:
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
