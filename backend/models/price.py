from datetime import datetime
from extensions.database import db

class PriceCache(db.Model):
    """Modelo para cache de preços dos ativos."""
    __tablename__ = 'price_cache'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=True, index=True)  # Permite NULL para valores globais
    ticker = db.Column(db.String(32), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, index=True)
    
    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'ticker': self.ticker,
            'price': self.price,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }