"""
Script para criar as tabelas necessárias para o histórico de portfólio.
Execute este script uma vez para configurar as tabelas no banco de dados.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_portfolio_history_table():
    """
    Cria a tabela portfolio_history se ela não existir
    """
    # Conecta ao banco de dados
    try:
        conn = sqlite3.connect('instance/pywallet.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
        if cursor.fetchone():
            print("A tabela portfolio_history já existe.")
            return
        
        # Cria a tabela portfolio_history
        cursor.execute('''
        CREATE TABLE portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date DATE NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
        ''')
        
        # Cria índices para melhorar performance
        cursor.execute('CREATE INDEX idx_portfolio_history_user_id ON portfolio_history (user_id)')
        cursor.execute('CREATE INDEX idx_portfolio_history_date ON portfolio_history (date)')
        cursor.execute('CREATE INDEX idx_portfolio_history_user_date ON portfolio_history (user_id, date)')
        
        conn.commit()
        print("Tabela portfolio_history criada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar tabela portfolio_history: {str(e)}")
    finally:
        if conn:
            conn.close()

def populate_initial_history():
    """
    Popula a tabela de histórico com os dados atuais dos portfólios de cada usuário
    """
    try:
        conn = sqlite3.connect('instance/pywallet.db')
        cursor = conn.cursor()
        
        # Obtém todos os portfólios mais recentes de cada usuário
        cursor.execute('''
        SELECT p.user_id, p.data, MAX(p.uploaded_at) 
        FROM portfolio p 
        GROUP BY p.user_id
        ''')
        
        portfolios = cursor.fetchall()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Para cada portfólio, cria um registro no histórico com a data atual
        for user_id, data, _ in portfolios:
            # Verifica se já existe um registro para este usuário nesta data
            cursor.execute('''
            SELECT id FROM portfolio_history 
            WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            
            if cursor.fetchone():
                print(f"Já existe um registro para o usuário {user_id} na data {today}")
                continue
            
            # Insere no histórico
            cursor.execute('''
            INSERT INTO portfolio_history (user_id, date, data)
            VALUES (?, ?, ?)
            ''', (user_id, today, data))
            
            print(f"Histórico inicial criado para o usuário {user_id}")
        
        conn.commit()
        print("Migração inicial de dados para o histórico concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro ao popular histórico inicial: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_portfolio_history_table()
    populate_initial_history()
    print("Migração do banco de dados concluída!")
