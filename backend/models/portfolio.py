from datetime import datetime
import json
from extensions.database import db

class Portfolio(db.Model):
    """Modelo de portfólio de ativos do usuário."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON string com os ativos (dados originais)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False)
    cached_prices = db.Column(db.Text, nullable=True)  # JSON string com preços atualizados
    cache_timestamp = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'filename': self.filename,
            'cache_timestamp': self.cache_timestamp.isoformat() if self.cache_timestamp else None
        }
        
    def get_assets(self):
        """Retorna os ativos como uma lista de dicionários."""
        try:
            return json.loads(self.data)
        except:
            return []
            
    def get_cached_prices(self):
        """Retorna os preços em cache como um dicionário."""
        if not self.cached_prices:
            return {}
        try:
            return json.loads(self.cached_prices)
        except:
            return {}
            
    def update_cache(self, prices_dict):
        """Atualiza o cache de preços."""
        self.cached_prices = json.dumps(prices_dict)
        self.cache_timestamp = datetime.utcnow()

class PortfolioEvolutionCache(db.Model):
    """Modelo para cache da evolução do portfólio ao longo do tempo."""
    __tablename__ = 'portfolio_evolution_cache'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    __table_args__ = (
        db.Index('idx_evolution_user_date', 'user_id', 'date'),
    )
    
    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'value': float(self.total_value)
        }