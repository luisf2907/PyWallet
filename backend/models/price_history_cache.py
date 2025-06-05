from datetime import datetime
from extensions.database import db

class PriceHistoryCache(db.Model):
    """Cache de preços históricos diários para evolução do portfólio."""
    __tablename__ = 'price_history_cache'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(32), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    close = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('ticker', 'date', name='uix_ticker_date'),
    )

    def to_dict(self):
        return {
            'ticker': self.ticker,
            'date': self.date.isoformat(),
            'close': self.close,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
