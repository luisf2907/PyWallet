import sqlite3
import json
from datetime import datetime

def check_portfolio_history():
    try:
        conn = sqlite3.connect('../instance/pywallet.db')
        cursor = conn.cursor()
        
    # Verifica se a tabela portfolio_history existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
    if not cursor.fetchone():
        print("A tabela portfolio_history não existe!")
        
        # Tenta criar a tabela portfolio_history se não existir
        try:
            cursor.execute('''
            CREATE TABLE portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            print("Tabela portfolio_history criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabela: {e}")
        return
        
        # Conta total de registros
        cursor.execute("SELECT COUNT(*) FROM portfolio_history")
        total = cursor.fetchone()[0]
        print(f"Total de registros na tabela portfolio_history: {total}")
        
        # Busca registros específicos para abril/2025
        cursor.execute("SELECT * FROM portfolio_history WHERE date LIKE '2025-04-%'")
        april_records = cursor.fetchall()
        print(f"\nRegistros de abril/2025: {len(april_records)}")
        
        # Exibe os últimos 5 registros
        cursor.execute("SELECT * FROM portfolio_history ORDER BY id DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        print("\nÚltimos 5 registros:")
        for record in recent_records:
            record_id, user_id, date_str, data_json, created_at = record
            print(f"ID: {record_id}, Usuário: {user_id}, Data: {date_str}")
            try:
                portfolio_data = json.loads(data_json)
                print(f"  Ativos: {len(portfolio_data)} itens")
                for asset in portfolio_data[:3]:  # Mostra apenas os 3 primeiros ativos
                    print(f"    {asset.get('ticker')}: {asset.get('quantidade')} @ {asset.get('preco_medio')}")
                if len(portfolio_data) > 3:
                    print(f"    ... e mais {len(portfolio_data) - 3} ativos")
            except Exception as e:
                print(f"  Erro ao decodificar JSON: {e}")
        
    except Exception as e:
        print(f"Erro ao verificar banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_portfolio_history()
