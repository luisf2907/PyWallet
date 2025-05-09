from datetime import datetime
from extensions.database import db

class DividendsCache(db.Model):
    """Modelo para cache de dividendos recebidos."""
    __tablename__ = 'dividends_cache'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    ticker = db.Column(db.String(32), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(32), nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False, index=True)

    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'ticker': self.ticker,
            'date': self.date.strftime('%Y-%m-%d'),
            'value': self.value,
            'quantity': self.quantity,
            'event_type': self.event_type or 'Dividendo'
        }

class DividendReceiptStatus(db.Model):
    """Modelo para controle de status de recebimento de proventos."""
    __tablename__ = 'dividend_receipt_status'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    ticker = db.Column(db.String(32), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    received = db.Column(db.Boolean, nullable=False, default=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'ticker', 'date', name='uq_user_ticker_date'),)
    
    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'ticker': self.ticker,
            'date': self.date.strftime('%Y-%m-%d'),
            'received': self.received
        }