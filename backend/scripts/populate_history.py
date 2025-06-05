"""
Script para popular a tabela portfolio_history com dados históricos
baseados nas transações anteriores. Isso garante que teremos pontos de dados
para exibir na evolução da carteira.
"""
import os
import sys
import json
from datetime import datetime, timedelta

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions.database import db
from models.portfolio import Portfolio
from models.portfolio_history import PortfolioHistory
from services.portfolio_history_service import save_portfolio_history

def populate_history():
    """
    Obtém todos os portfólios dos usuários e cria registros históricos
    para os últimos 30 dias.
    """
    print("Iniciando população da tabela portfolio_history...")
    
    try:
        # Inicializa o app Flask para poder usar os modelos
        from flask import Flask
        from config import Config
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            # Obtém portfólios únicos por usuário (o mais recente de cada)
            portfolios = db.session.query(Portfolio).\
                order_by(Portfolio.user_id, Portfolio.uploaded_at.desc()).all()
            
            unique_users = set()
            latest_portfolios = []
            
            for p in portfolios:
                if p.user_id not in unique_users:
                    unique_users.add(p.user_id)
                    latest_portfolios.append(p)
            
            print(f"Encontrados {len(latest_portfolios)} portfólios únicos")
            
            today = datetime.now().date()
            
            # Para cada usuário, cria registros históricos para os últimos 30 dias
            for portfolio in latest_portfolios:
                user_id = portfolio.user_id
                portfolio_data = json.loads(portfolio.data)
                print(f"Processando usuário {user_id} com {len(portfolio_data)} ativos")
                
                # Verifica registros existentes
                existing_records = PortfolioHistory.query.filter_by(user_id=user_id).all()
                existing_dates = [record.date for record in existing_records]
                
                print(f"Usuário {user_id} tem {len(existing_records)} registros históricos")
                
                # Cria registros para os últimos 30 dias
                for days_back in range(30):
                    date_to_add = today - timedelta(days=days_back)
                    
                    # Pula se já existe registro para esta data
                    if date_to_add in existing_dates:
                        print(f"Já existe registro para {date_to_add}, pulando")
                        continue
                    
                    # Adiciona registro histórico
                    date_str = date_to_add.strftime('%Y-%m-%d')
                    print(f"Adicionando registro para {date_str}")
                    save_portfolio_history(user_id, portfolio_data, date_str)
            
            print("População de histórico concluída com sucesso!")
                    
    except Exception as e:
        print(f"Erro ao popular histórico: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_history()
