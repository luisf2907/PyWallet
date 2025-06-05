"""
Script para forçar a criação de um registro histórico para uma data específica
"""
import os
import sys
import json
from datetime import datetime

# Adiciona o diretório pai ao path para importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def force_create_history():
    try:
        # Inicializa o app Flask para poder usar os modelos
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        from extensions.database import db
        db.init_app(app)
        
        with app.app_context():
            from models.portfolio import Portfolio
            from models.portfolio_history import PortfolioHistory
            
            # Use os IDs reais dos usuários
            user_ids = []
            users_query = db.session.execute('SELECT id FROM user').fetchall()
            for user in users_query:
                user_ids.append(user[0])
                
            if not user_ids:
                print("Nenhum usuário encontrado!")
                return
                
            print(f"Encontrados {len(user_ids)} usuários: {user_ids}")
            
            # Data específica para criar o histórico
            target_date = "2025-04-22"
            
            for user_id in user_ids:
                # Busca o portfólio mais recente do usuário
                portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
                
                if not portfolio:
                    print(f"Usuário {user_id} não tem portfólio")
                    continue
                    
                try:
                    portfolio_data = json.loads(portfolio.data)
                    print(f"Portfólio do usuário {user_id}: {len(portfolio_data)} ativos")
                    
                    # Print some portfolio data for verification
                    for asset in portfolio_data[:3]:
                        print(f"  {asset.get('ticker')}: {asset.get('quantidade')} @ {asset.get('preco_medio')}")
                        
                    # Cria ou atualiza o registro histórico
                    history = PortfolioHistory.save_portfolio_snapshot(
                        user_id=user_id,
                        date=target_date,
                        portfolio_data=portfolio_data
                    )
                    
                    print(f"Snapshot criado/atualizado para {user_id} na data {target_date}")
                    
                except Exception as e:
                    print(f"Erro ao processar portfólio do usuário {user_id}: {str(e)}")
    
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_create_history()
    print("Script concluído!")
