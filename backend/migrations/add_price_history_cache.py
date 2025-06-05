from backend.models.price_history_cache import PriceHistoryCache
from extensions.database import db

def upgrade():
    # Cria a tabela de cache de históricos se não existir
    PriceHistoryCache.__table__.create(bind=db.engine, checkfirst=True)

def downgrade():
    # Remove a tabela
    PriceHistoryCache.__table__.drop(bind=db.engine, checkfirst=True)
