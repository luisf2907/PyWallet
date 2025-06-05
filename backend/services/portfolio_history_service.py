import json
import pandas as pd
from datetime import datetime, date
from flask import current_app

from extensions.database import db
from models.portfolio import Portfolio
from models.portfolio_history import PortfolioHistory
from utils.cache_utils import clear_evolution_cache_for_user

def save_portfolio_history(user_id, portfolio_data, date_str=None):
    """
    Salva um snapshot do portfólio no histórico.
    
    Args:
        user_id (str): ID do usuário
        portfolio_data (list): Dados do portfólio
        date_str (str, optional): Data no formato 'YYYY-MM-DD'. Se não informada, usa a data atual.
        
    Returns:
        PortfolioHistory: Objeto salvo no histórico
    """
    # Se não foi informada uma data, usa a data atual
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Log detalhado dos dados recebidos
    current_app.logger.info(f"Salvando histórico para usuário {user_id} na data {date_str}")
    current_app.logger.info(f"Dados do portfólio: {len(portfolio_data)} ativos")
    
    # Validação adicional dos dados do portfólio
    valid_portfolio = []
    for asset in portfolio_data:
        try:
            ticker = asset.get('ticker', '').strip()
            quantidade = float(asset.get('quantidade', 0))
            preco_medio = float(asset.get('preco_medio', 0))
            
            # Só considera ativos com ticker, quantidade e preço válidos
            if ticker and quantidade > 0 and preco_medio > 0:
                valid_portfolio.append({
                    'ticker': ticker,
                    'quantidade': quantidade,
                    'preco_medio': preco_medio
                })
            else:
                current_app.logger.warning(f"Ignorando ativo inválido: {asset}")
        except Exception as e:
            current_app.logger.error(f"Erro ao processar ativo {asset}: {str(e)}")
    
    # Atualiza o portfolio_data com dados validados
    portfolio_data = valid_portfolio
    
    current_app.logger.info(f"Salvando {len(portfolio_data)} ativos válidos no histórico")
        
    # Tenta salvar no histórico
    try:
        result = PortfolioHistory.save_portfolio_snapshot(
            user_id=user_id,
            date=date_str,
            portfolio_data=portfolio_data
        )
        current_app.logger.info(f"Histórico salvo com sucesso para {date_str}")
        return result
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar histórico de portfólio: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def get_portfolio_history(user_id, start_date=None, end_date=None):
    """
    Retorna o histórico de portfólio de um usuário.
    
    Args:
        user_id (str): ID do usuário
        start_date (str, optional): Data inicial no formato 'YYYY-MM-DD'
        end_date (str, optional): Data final no formato 'YYYY-MM-DD'
        
    Returns:
        list: Lista de dicionários com o histórico do portfólio
    """
    try:
        history = PortfolioHistory.get_history_for_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        result = []
        for entry in history:
            result.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'portfolio': entry.get_data()
            })
            
        return result
    except Exception as e:
        current_app.logger.error(f"Erro ao obter histórico de portfólio: {str(e)}")
        return []

def calculate_portfolio_evolution(user_id, start_date=None, end_date=None):
    """
    Calcula a evolução diária do valor total do portfólio.
    
    Args:
        user_id (str): ID do usuário
        start_date (str, optional): Data inicial no formato 'YYYY-MM-DD'
        end_date (str, optional): Data final no formato 'YYYY-MM-DD'
        
    Returns:
        dict: Dados de evolução do portfólio, com datas como chaves e valores como valores
    """
    from services.price_service import get_price
    import traceback
    
    # Log detalhado dos parâmetros
    current_app.logger.info(f"Calculando evolução para usuário {user_id}, período: {start_date} até {end_date}")
    
    try:
        # Busca o histórico do portfólio
        history = get_portfolio_history(user_id, start_date, end_date)
        
        # Log do resultado da busca
        current_app.logger.info(f"Encontrados {len(history)} registros no histórico")
        
        # Se não há dados históricos, retorna um dicionário vazio
        if not history:
            current_app.logger.warning(f"Nenhum dado histórico encontrado para {user_id} no período")
            return {"labels": [], "values": []}
        
        evolution = {}
        
        for entry in history:
            entry_date = entry['date']
            portfolio = entry['portfolio']
            
            # Log do conteúdo de cada entrada
            current_app.logger.info(f"Processando data {entry_date}: {len(portfolio)} ativos")
            
            # Se o portfólio estiver vazio nesta data, continue
            if not portfolio:
                current_app.logger.warning(f"Portfólio vazio para a data {entry_date}")
                evolution[entry_date] = 0
                continue
            
            total_value = 0
            
            for asset in portfolio:
                # Extrai e valida os dados do ativo
                ticker = asset.get('ticker', '')
                
                try:
                    quantidade = float(asset.get('quantidade', 0))
                    preco_medio = float(asset.get('preco_medio', 0))
                except (ValueError, TypeError) as e:
                    current_app.logger.error(f"Erro ao converter dados do ativo {ticker}: {str(e)}")
                    continue
                
                if quantidade <= 0:
                    current_app.logger.debug(f"Ignorando {ticker} com quantidade {quantidade}")
                    continue
                
                # Log detalhado para cada ativo
                current_app.logger.debug(f"Processando ativo: {ticker}, quantidade: {quantidade}, preço médio: {preco_medio}")
                
                # Tenta obter o preço histórico ou usa o preço médio como fallback
                try:
                    current_price = get_price(ticker, entry_date)
                    
                    if current_price is None or current_price <= 0:
                        current_app.logger.warning(f"Preço histórico para {ticker} em {entry_date} não encontrado, usando preço médio {preco_medio}")
                        current_price = preco_medio
                    else:
                        current_app.logger.debug(f"Preço histórico para {ticker} em {entry_date}: {current_price}")
                except Exception as e:
                    current_app.logger.error(f"Erro ao obter preço para {ticker} em {entry_date}: {str(e)}")
                    current_price = preco_medio
                
                # Calcula o valor do ativo
                asset_value = current_price * quantidade
                total_value += asset_value
                
                current_app.logger.debug(f"Valor de {ticker} em {entry_date}: {asset_value:.2f} (preço={current_price}, qtd={quantidade})")
            
            # Registra o valor total para esta data
            current_app.logger.info(f"Valor total da carteira em {entry_date}: R${total_value:.2f}")
            evolution[entry_date] = total_value
        
        # Se após processar tudo, não temos valores, retorna um dicionário vazio
        if not evolution:
            current_app.logger.warning("Nenhum valor de evolução calculado")
            return {"labels": [], "values": []}
        
        # Formata para a resposta esperada pelo frontend
        result = {
            "labels": list(evolution.keys()),
            "values": list(evolution.values())
        }
        
        current_app.logger.info(f"Retornando evolução com {len(result['labels'])} pontos de dados")
        return result
        
    except Exception as e:
        # Log detalhado de qualquer erro
        current_app.logger.error(f"Erro ao calcular evolução do portfólio: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return {"labels": [], "values": []}
