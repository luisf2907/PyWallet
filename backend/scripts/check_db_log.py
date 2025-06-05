"""
Script para verificar se a tabela de histórico de portfólio foi criada corretamente.
Escreve o resultado em um arquivo de log.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_portfolio_history_table():
    """
    Verifica se a tabela portfolio_history existe e mostra seus campos
    """
    # Cria arquivo de log
    log_file = os.path.join(os.path.dirname(__file__), 'db_check.log')
    with open(log_file, 'w') as f:
        f.write(f"Verificação da tabela portfolio_history - {datetime.now()}\n")
        f.write("="*80 + "\n\n")
        
        # Conecta ao banco de dados
        try:
            conn = sqlite3.connect('instance/pywallet.db')
            cursor = conn.cursor()
            
            # Verifica se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
            if not cursor.fetchone():
                f.write("A tabela portfolio_history não existe!\n")
                return
            
            f.write("A tabela portfolio_history existe.\n")
            
            # Mostra a estrutura da tabela
            cursor.execute("PRAGMA table_info(portfolio_history)")
            columns = cursor.fetchall()
            f.write("\nEstrutura da tabela portfolio_history:\n")
            for col in columns:
                f.write(f"  {col[1]} ({col[2]})\n")
            
            # Conta quantos registros existem
            cursor.execute("SELECT COUNT(*) FROM portfolio_history")
            count = cursor.fetchone()[0]
            f.write(f"\nTotal de registros: {count}\n")
            
            # Mostra alguns registros
            if count > 0:
                f.write("\nAlguns registros de exemplo:\n")
                cursor.execute("SELECT id, user_id, date, substr(data, 1, 50) || '...' FROM portfolio_history LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    f.write(f"  ID: {row[0]}, User ID: {row[1]}, Data: {row[2]}, Dados: {row[3]}\n")
            
        except Exception as e:
            f.write(f"Erro ao verificar tabela portfolio_history: {str(e)}\n")
        finally:
            if conn:
                conn.close()
        
        f.write("\nVerificação concluída!\n")
    
    print(f"Verificação concluída! Resultados salvos em {log_file}")

if __name__ == "__main__":
    check_portfolio_history_table()
