"""
Script para criar manualmente a tabela portfolio_history
"""
import os
import sys
import sqlite3

def create_portfolio_history_table_manually():
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect('c:/Users/w10/Documents/PyWallet/instance/pywallet.db')
        cursor = conn.cursor()
        
        # Primeiro, verifica se a tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
        if cursor.fetchone():
            print("A tabela portfolio_history já existe. Pulando criação.")
            return
            
        # Cria a tabela
        cursor.execute('''
        CREATE TABLE portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date DATE NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Cria os índices
        cursor.execute('CREATE INDEX idx_portfolio_history_user_id ON portfolio_history (user_id)')
        cursor.execute('CREATE INDEX idx_portfolio_history_date ON portfolio_history (date)')
        
        conn.commit()
        print("Tabela portfolio_history criada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar tabela: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_portfolio_history_table_manually()
