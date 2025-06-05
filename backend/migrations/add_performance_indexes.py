"""
Script de migração para adicionar índices de performance ao banco de dados
"""
from extensions.database import db
from models.portfolio import Portfolio, PortfolioEvolutionCache
from models.price import PriceCache
from app import app

def create_indexes():
    """
    Cria índices no banco de dados para melhorar a performance das consultas.
    """
    print("Iniciando criação de índices para melhorar performance...")
    with app.app_context():
        try:
            # Criar índice composto em Portfolio
            db.session.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_user_date ON portfolio (user_id, uploaded_at)')
            
            # Criar índice composto em PriceCache
            db.session.execute('CREATE INDEX IF NOT EXISTS idx_ticker_updated ON price_cache (ticker, last_updated)')
            
            # Verificar se o índice em PortfolioEvolutionCache já existe
            db.session.execute('CREATE INDEX IF NOT EXISTS idx_evolution_user_date ON portfolio_evolution_cache (user_id, date)')
            
            db.session.commit()
            print("Índices criados com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar índices: {e}")

if __name__ == "__main__":
    create_indexes()
