import json
import datetime
from extensions.database import db

class PortfolioHistory(db.Model):
    """
    Modelo para armazenar o histórico diário de portfólios dos usuários.
    
    Este modelo é utilizado para armazenar instantâneos da carteira do usuário em diferentes datas,
    permitindo visualizar a evolução da carteira ao longo do tempo.
    """
    __tablename__ = 'portfolio_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    data = db.Column(db.Text, nullable=False)  # JSON com os dados do portfólio
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, user_id, date, portfolio_data):
        """
        Inicializa um novo registro de histórico de portfólio.
        
        Args:
            user_id (str): ID do usuário
            date (date): Data do registro do portfólio
            portfolio_data (list): Lista de dicionários com os dados do portfólio
        """
        self.user_id = user_id
        
        # Se a data for string, converte para objeto date
        if isinstance(date, str):
            self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            self.date = date
            
        # Armazena os dados em formato JSON
        self.data = json.dumps(portfolio_data)
    
    def get_data(self):
        """
        Retorna os dados do portfólio como objeto Python.
        
        Returns:
            list: Lista de dicionários com os dados do portfólio
        """
        return json.loads(self.data)
        
    @classmethod
    def get_history_for_user(cls, user_id, start_date=None, end_date=None):
        """
        Retorna o histórico de portfólio de um usuário em um intervalo de datas.
        
        Args:
            user_id (str): ID do usuário
            start_date (date, optional): Data inicial (inclusive)
            end_date (date, optional): Data final (inclusive)
            
        Returns:
            list: Lista de objetos PortfolioHistory ordenados por data
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(cls.date >= start_date)
            
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(cls.date <= end_date)
            
        return query.order_by(cls.date).all()
    
    @classmethod
    def get_latest_for_user(cls, user_id, before_date=None):
        """
        Retorna o registro de portfólio mais recente para um usuário.
        
        Args:
            user_id (str): ID do usuário
            before_date (date, optional): Data limite (retorna o mais recente antes desta data)
            
        Returns:
            PortfolioHistory: Objeto com o registro mais recente, ou None se não houver
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if before_date:
            if isinstance(before_date, str):
                before_date = datetime.datetime.strptime(before_date, '%Y-%m-%d').date()
            query = query.filter(cls.date <= before_date)
            
        return query.order_by(cls.date.desc()).first()
    
    @classmethod
    def save_portfolio_snapshot(cls, user_id, date, portfolio_data):
        """
        Salva um instantâneo do portfólio para uma data específica.
        Se já existir um registro para a mesma data, ele será atualizado.
        
        Args:
            user_id (str): ID do usuário
            date (date): Data do snapshot
            portfolio_data (list): Lista de dicionários com os dados do portfólio
            
        Returns:
            PortfolioHistory: Objeto salvo
        """
        # Converte string para date se necessário
        if isinstance(date, str):
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date_obj = date
            
        # Verifica se já existe um registro para esta data
        existing = cls.query.filter_by(
            user_id=user_id,
            date=date_obj
        ).first()
        
        if existing:
            # Atualiza o registro existente
            existing.data = json.dumps(portfolio_data)
            db.session.commit()
            return existing
        else:
            # Cria um novo registro
            new_history = cls(
                user_id=user_id,
                date=date_obj,
                portfolio_data=portfolio_data
            )
            db.session.add(new_history)
            db.session.commit()
            return new_history
