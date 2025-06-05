"""
Script para verificar se a tabela de histórico de portfólio foi criada corretamente.
"""
import os
import sys
import sqlite3

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_portfolio_history_table():
    """
    Verifica se a tabela portfolio_history existe e mostra seus campos
    """
    # Conecta ao banco de dados
    try:
        conn = sqlite3.connect('instance/pywallet.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
        if not cursor.fetchone():
            print("A tabela portfolio_history não existe!")
            return
        
        print("A tabela portfolio_history existe.")
        
        # Mostra a estrutura da tabela
        cursor.execute("PRAGMA table_info(portfolio_history)")
        columns = cursor.fetchall()
        print("\nEstrutura da tabela portfolio_history:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Conta quantos registros existem
        cursor.execute("SELECT COUNT(*) FROM portfolio_history")
        count = cursor.fetchone()[0]
        print(f"\nTotal de registros: {count}")
        
        # Mostra alguns registros
        if count > 0:
            print("\nAlguns registros de exemplo:")
            cursor.execute("SELECT id, user_id, date, substr(data, 1, 50) || '...' FROM portfolio_history LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  ID: {row[0]}, User ID: {row[1]}, Data: {row[2]}, Dados: {row[3]}")
        
    except Exception as e:
        print(f"Erro ao verificar tabela portfolio_history: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_portfolio_history_table()
