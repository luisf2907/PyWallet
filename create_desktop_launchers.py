#!/usr/bin/env python3
"""
Script para criar launchers de desktop para arquivos .sh
Isso permite que os scripts .sh sejam executados com duplo clique na interface gráfica.
"""

import os
import stat
import subprocess
from pathlib import Path

def create_desktop_file(sh_path):
    """Cria um arquivo .desktop para o script .sh fornecido"""
    sh_path = Path(sh_path).absolute()
    
    # Verifica se o arquivo existe
    if not sh_path.exists():
        print(f"Erro: O arquivo {sh_path} não existe.")
        return False
    
    # Torna o arquivo executável
    current_permissions = stat.S_IMODE(os.lstat(sh_path).st_mode)
    os.chmod(sh_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    # Nome do script sem a extensão
    script_name = sh_path.stem
    
    # Caminho para o diretório desktop
    desktop_dir = Path.home() / "Desktop"
    if not desktop_dir.exists():
        # Tenta localizar o diretório desktop em diferentes idiomas
        for alt_name in ["Área de Trabalho", "Escritorio", "Bureau"]:
            alt_dir = Path.home() / alt_name
            if alt_dir.exists():
                desktop_dir = alt_dir
                break
    
    # Se ainda não encontrou, usa o diretório home
    if not desktop_dir.exists():
        desktop_dir = Path.home()
    
    # Caminho para o ícone (se existir)
    icon_path = sh_path.parent / "Prophit_logo.png"
    if not icon_path.exists():
        icon_path = Path("/home/prophit/Documents/PyWallet/Prophit_logo.png")
    
    # Conteúdo do arquivo .desktop
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={script_name}
Comment=PyWallet Script Launcher
Exec=gnome-terminal --working-directory={sh_path.parent} -- bash -c "{sh_path} ; echo 'Pressione Enter para fechar...'; read"
Icon={icon_path if icon_path.exists() else ''}
Terminal=true
Categories=Utility;
"""
    
    # Caminho para o arquivo .desktop
    desktop_file_path = desktop_dir / f"{script_name}.desktop"
    
    # Escreve o arquivo .desktop
    with open(desktop_file_path, 'w') as f:
        f.write(desktop_content)
    
    # Torna o arquivo .desktop executável
    os.chmod(desktop_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | 
             stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"Criado launcher para: {sh_path}")
    print(f"Launcher salvo em: {desktop_file_path}")
    return True

def main():
    """Função principal"""
    # Diretório base do projeto
    base_dir = Path("/home/prophit/Documents/PyWallet")
    
    # Lista de arquivos .sh para criar launchers
    sh_files = [
        base_dir / "run_dev.sh",
        base_dir / "ubuntu_setup.sh",
        base_dir / "ubuntu" / "setup_linux.sh",
        base_dir / "ubuntu" / "fix_nodejs.sh",
        base_dir / "ubuntu" / "check_ubuntu.sh"
    ]
    
    # Cria launchers para cada arquivo .sh
    for sh_file in sh_files:
        if sh_file.exists():
            create_desktop_file(sh_file)
        else:
            print(f"Aviso: Arquivo {sh_file} não encontrado.")
    
    print("\nProcesso concluído. Os launchers foram criados na sua Área de Trabalho.")
    print("Agora você pode executar os scripts .sh com duplo clique.")

if __name__ == "__main__":
    main()
