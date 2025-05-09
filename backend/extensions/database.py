from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Configura o timeout do SQLite para ser mais paciente com conexões ocupadas
# Default é 5 segundos, aumentamos para 30 segundos
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        # Aumenta o timeout para 30 segundos
        cursor.execute("PRAGMA busy_timeout = 30000;")
        # Configura journal mode para WAL para melhor concorrência
        cursor.execute("PRAGMA journal_mode=WAL;")
        # Sincronização mais segura
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

# Cria a extensão SQLAlchemy
db = SQLAlchemy()

# Função auxiliar para executar operações com retry em caso de erro de banco de dados
def execute_with_retry(session_func, max_attempts=5):
    """
    Executa uma função que contém operações de banco de dados com retry em caso de erro.
    
    Args:
        session_func: Função que contém operações de banco de dados
        max_attempts: Número máximo de tentativas
        
    Returns:
        Resultado da função session_func
    """
    import time
    from sqlalchemy.exc import OperationalError, PendingRollbackError
    
    attempt = 0
    last_error = None
    
    while attempt < max_attempts:
        try:
            result = session_func()
            return result
        except (OperationalError, PendingRollbackError) as e:
            attempt += 1
            last_error = e
            
            if "database is locked" in str(e):
                print(f"[DATABASE] Tentativa {attempt}/{max_attempts}: Database bloqueado, esperando...")
                # Backoff exponencial: 1s, 2s, 4s, 8s, 16s
                time.sleep(2 ** (attempt - 1))
                
                # Se for um erro de rollback pendente, limpamos a sessão
                if isinstance(e, PendingRollbackError):
                    from flask import current_app
                    with current_app.app_context():
                        db.session.rollback()
            else:
                # Se não for erro de lock, reraise
                raise
    
    # Se chegou aqui, esgotou as tentativas
    print(f"[DATABASE] Erro após {max_attempts} tentativas: {last_error}")
    raise last_error

def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask."""
    db.init_app(app)
    
    # Cria todas as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return db