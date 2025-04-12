"""
portfolio_evolution.py - Funções para cálculo da evolução histórica do portfólio

Este módulo contém as funções necessárias para baixar e processar dados históricos
de ativos financeiros e calcular a evolução do valor de um portfólio ao longo do tempo.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import random
import time
import threading
import copy

def get_historical_prices(ticker, start_date, end_date, retries=3, delay=1):
    """
    Obtém os preços históricos de um ativo com retry em caso de falha.
    
    Args:
        ticker: Código do ativo
        start_date: Data inicial (string no formato 'YYYY-MM-DD')
        end_date: Data final (string no formato 'YYYY-MM-DD')
        retries: Número de tentativas em caso de falha
        delay: Tempo de espera entre tentativas (segundos)
        
    Returns:
        pandas.DataFrame ou None: Dataframe com os preços históricos ou None em caso de falha
    """
    for attempt in range(retries):
        try:
            # Criar uma nova sessão para cada download para evitar problemas de concorrência
            ticker_obj = yf.Ticker(ticker)
            history = ticker_obj.history(
                start=start_date,
                end=end_date,
                interval='1d'
            )
            
            if not history.empty and 'Close' in history.columns:
                return history
            
            # Se não retornou dados válidos mas não deu exceção, espera e tenta novamente
            if attempt < retries - 1:
                time.sleep(delay)
                
        except Exception as e:
            if attempt < retries - 1:
                print(f"Tentativa {attempt+1} falhou para {ticker}: {e}. Tentando novamente...")
                time.sleep(delay)
            else:
                print(f"Todas as tentativas falharam para {ticker}: {e}")
                
    return None

def process_asset_historical_data(asset, start_date, end_date, date_range, exchange_rate=None, format_ticker_func=None):
    """
    Processa dados históricos de um ativo e retorna uma série com valores do ativo ao longo do tempo.
    
    Args:
        asset: Dicionário contendo dados do ativo (ticker, quantidade, etc.)
        start_date: Data inicial (string no formato 'YYYY-MM-DD')
        end_date: Data final (string no formato 'YYYY-MM-DD')
        date_range: pandas.DatetimeIndex com as datas para as quais calcular os valores
        exchange_rate: Taxa de câmbio para conversão de moeda (por padrão 5.8187)
        format_ticker_func: Função para formatar o ticker para API (por padrão None)
        
    Returns:
        pandas.Series: Série com os valores do ativo ao longo do tempo
    """
    # Valores padrão
    if exchange_rate is None:
        exchange_rate = 5.8187
        
    # Extrair dados do ativo
    ticker_orig = asset['ticker'].strip().upper()
    
    # Aplicar função de formatação de ticker se fornecida
    if format_ticker_func:
        try:
            final_ticker = format_ticker_func(ticker_orig)
        except Exception:
            final_ticker = ticker_orig
    else:
        final_ticker = ticker_orig
        # Adicionar '.SA' para ativos brasileiros se não houver função de formatação
        if not ticker_orig.endswith('.SA') and not '.' in ticker_orig and not '=' in ticker_orig:
            final_ticker += '.SA'
    
    try:
        qty = float(asset.get('quantidade', 0))
        avg_price = float(asset.get('preco_medio', 0))
    except (ValueError, TypeError):
        print(f"Dados inválidos para {ticker_orig}")
        return pd.Series(0, index=date_range)
    
    # Verificar se é ativo dos EUA
    is_us = not final_ticker.endswith('.SA')
    conv_factor = exchange_rate if is_us else 1.0
    
    # Adicionar buffer de dias antes da data inicial para garantir dados suficientes
    buffer_days = 14
    start_with_buffer = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=buffer_days)).strftime('%Y-%m-%d')
    
    # Obter dados históricos
    history = get_historical_prices(final_ticker, start_with_buffer, end_date)
    
    if history is not None and not history.empty:
        try:
            # Processar preços de fechamento
            close_prices = history['Close'].copy()
            # Converter o índice para tz-naive para compatibilidade com o date_range
            close_prices.index = close_prices.index.tz_localize(None)
            # Preencher valores ausentes
            close_prices = close_prices.fillna(method='ffill')
            
            # Reindexar para o range de datas desejado
            try:
                asset_prices = close_prices.reindex(date_range, method='ffill')
            except Exception as e:
                print(f"Erro ao reindexar preços para {ticker_orig}: {e}")
                # Criar série com todos os valores iguais ao último preço disponível
                last_price = close_prices.iloc[-1] if not close_prices.empty else avg_price
                asset_prices = pd.Series(last_price, index=date_range)
            
            # Se ainda tiver NaN após reindexar, preencher com o primeiro valor válido
            if asset_prices.isna().any():
                first_valid = asset_prices.first_valid_index()
                if first_valid is not None:
                    first_value = asset_prices.loc[first_valid]
                    asset_prices = asset_prices.fillna(first_value)
                else:
                    # Fallback para preço médio se não houver valores válidos
                    asset_prices = pd.Series(avg_price, index=date_range)
            
            # Calcular valores
            asset_values = asset_prices * qty * conv_factor
            return asset_values
        except Exception as e:
            print(f"Erro ao processar dados históricos para {ticker_orig}: {e}")
            # Fallback para preço médio
            return pd.Series(avg_price * qty * conv_factor, index=date_range)
    else:
        # Fallback: usar preço médio para todas as datas
        print(f"Usando preço médio para {ticker_orig} devido à falta de dados históricos")
        return pd.Series(avg_price * qty * conv_factor, index=date_range)

def calculate_portfolio_evolution(portfolio_data, start_date, end_date, exchange_rate=None, format_ticker_func=None):
    """
    Calcula a evolução histórica do valor do portfólio.
    
    Args:
        portfolio_data: Lista de ativos no portfólio
        start_date: Data inicial (string no formato 'YYYY-MM-DD')
        end_date: Data final (string no formato 'YYYY-MM-DD')
        exchange_rate: Taxa de câmbio para conversão de moeda (opcional)
        format_ticker_func: Função para formatar o ticker para API (opcional)
        
    Returns:
        list: Lista de dicionários com a evolução do portfólio
    """
    try:
        # Converter strings para objetos datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Determinar frequência baseada no tamanho do período
        days_diff = (end_date_obj - start_date_obj).days
        
        if days_diff > 365:
            # Para períodos > 1 ano, usar dados semanais
            freq = 'W-MON'
        elif days_diff > 90:
            # Para períodos entre 3 meses e 1 ano, usar dados a cada 3 dias
            freq = '3D'
        else:
            # Para períodos curtos, usar dados diários
            freq = 'D'
            
        # Criar range de datas
        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Adicionar data final se não estiver no range
        if end_date_obj not in date_range:
            date_range = date_range.append(pd.DatetimeIndex([end_date_obj]))
        
        # Inicializar série com zeros
        total_values = pd.Series(0.0, index=date_range)
        
        # Fazer uma cópia do portfolio_data para evitar problemas de concorrência
        safe_portfolio_data = copy.deepcopy(portfolio_data)
        
        # Processar cada ativo sequencialmente para evitar problemas de concorrência
        for asset in safe_portfolio_data:
            try:
                asset_values = process_asset_historical_data(
                    asset, 
                    start_date, 
                    end_date,
                    date_range,
                    exchange_rate,
                    format_ticker_func
                )
                if asset_values is not None:
                    total_values = total_values.add(asset_values, fill_value=0)
            except Exception as e:
                print(f"Erro ao processar {asset.get('ticker', 'ativo desconhecido')}: {e}")
        
        # Converter para lista de dicionários
        evolution_list = [
            {'date': d.strftime('%Y-%m-%d'), 'value': float(v)} 
            for d, v in total_values.items()
        ]
        
        # Ordenar por data
        evolution_list.sort(key=lambda x: x['date'])
        
        return evolution_list
    
    except Exception as e:
        print(f"Erro ao calcular evolução do portfólio: {e}")
        return []

def generate_simulated_evolution(start_date, end_date, start_value, end_value, num_points=30):
    """
    Gera uma evolução simulada do portfólio entre dois valores.
    Útil como fallback quando não há dados históricos disponíveis.
    
    Args:
        start_date: Data inicial (string no formato 'YYYY-MM-DD')
        end_date: Data final (string no formato 'YYYY-MM-DD')
        start_value: Valor inicial do portfólio
        end_value: Valor final do portfólio
        num_points: Número de pontos a gerar
        
    Returns:
        list: Lista de dicionários com a evolução simulada
    """
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        days_diff = (end_date_obj - start_date_obj).days
        
        # Limitar número de pontos
        actual_points = min(num_points, max(2, days_diff))
        
        # Gerar datas espaçadas uniformemente
        dates = []
        if days_diff <= actual_points:
            # Se o período for curto, usar todas as datas
            for i in range(days_diff + 1):
                date = start_date_obj + timedelta(days=i)
                dates.append(date)
        else:
            # Distribuir pontos uniformemente
            step = days_diff / (actual_points - 1)
            for i in range(actual_points):
                day_offset = int(i * step)
                date = start_date_obj + timedelta(days=day_offset)
                dates.append(date)
            
            # Garantir que a data final esteja incluída
            if dates[-1].date() != end_date_obj.date():
                dates[-1] = end_date_obj
        
        # Gerar valores usando uma curva de crescimento realista
        values = []
        for i, date in enumerate(dates):
            # Usar uma função de crescimento não-linear
            progress = i / (len(dates) - 1)
            
            # Função cúbica para dar uma aparência mais natural
            # Essa função produz uma curva em S suave
            base_curve = progress * progress * (3 - 2 * progress)
            
            # Valor base neste ponto da curva
            base_value = start_value + (end_value - start_value) * base_curve
            
            # Adicionar variação aleatória para simular flutuações de mercado
            # Maior no meio do período, menor no início e no fim
            variation_factor = 0.025  # ±2.5%
            # Ajustar variação máxima no meio do período (forma de sino)
            window_factor = 4 * progress * (1 - progress)
            random_factor = 1 + (random.random() * 2 - 1) * variation_factor * window_factor
            
            # O último ponto é sempre exatamente o valor final
            if i == len(dates) - 1:
                values.append(end_value)
            else:
                values.append(base_value * random_factor)
        
        # Criar lista de resultados
        result = [
            {'date': date.strftime('%Y-%m-%d'), 'value': float(value)}
            for date, value in zip(dates, values)
        ]
        
        return result
    
    except Exception as e:
        print(f"Erro ao gerar evolução simulada: {e}")
        # Fallback mínimo
        return [
            {'date': start_date, 'value': float(start_value)},
            {'date': end_date, 'value': float(end_value)}
        ]
