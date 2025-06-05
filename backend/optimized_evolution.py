"""
Módulo para cálculo otimizado da evolução do portfólio
Implementa versão mais eficiente com batching e caching
"""
from datetime import datetime, timedelta
import pandas as pd
import time
import random
import yfinance as yf
import copy
from utils.memory_cache import memory_cache
from models.portfolio import PortfolioEvolutionCache
from extensions.database import db
from flask import session

@memory_cache(ttl_seconds=3600)  # Cache por 1 hora
def optimized_portfolio_evolution(portfolio_data, start_date, end_date, exchange_rate=None, format_ticker_func=None, price_cache=None):
    """
    Versão otimizada do cálculo de evolução de portfólio usando batch download e cache.
    
    Args:
        portfolio_data: Lista de ativos do portfólio
        start_date: Data inicial (string no formato 'YYYY-MM-DD')
        end_date: Data final (string no formato 'YYYY-MM-DD')
        exchange_rate: Taxa de câmbio USD/BRL (opcional)
        format_ticker_func: Função para formatar tickers (opcional)
        price_cache: Dicionário com preços em cache (opcional)
        
    Returns:
        list: Lista com evolução do portfólio
    """
    user_id = session.get('user_id') if hasattr(session, 'get') else None
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Determinar frequência baseada no período
    days_diff = (end_date_obj - start_date_obj).days
    if days_diff > 365:
        freq = 'W-MON'  # Semanal para períodos longos
    elif days_diff > 90:
        freq = '3D'     # A cada 3 dias para períodos médios
    else:
        freq = 'D'      # Diário para períodos curtos
    
    # Criar range de datas
    date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
    if end_date_obj not in date_range:
        date_range = date_range.append(pd.DatetimeIndex([end_date_obj]))
    
    # Cópia segura dos dados
    safe_portfolio_data = copy.deepcopy(portfolio_data)
    
    # Modo rápido com PriceCache
    if price_cache is not None:
        total_invested = 0.0
        total_current = 0.0
        
        for asset in safe_portfolio_data:
            ticker_orig = asset['ticker'].strip().upper()
            final_ticker = ticker_orig
            if not ticker_orig.endswith('.SA') and not '.' in ticker_orig and not '=' in ticker_orig:
                final_ticker += '.SA'
                
            try:
                qty = float(asset.get('quantidade', 0))
                avg_price = float(asset.get('preco_medio', 0))
            except (ValueError, TypeError):
                continue
                
            is_us = not final_ticker.endswith('.SA')
            conv_factor = exchange_rate if (exchange_rate and is_us) else 1.0
            
            invested = avg_price * qty * conv_factor
            price = price_cache.get(ticker_orig) or price_cache.get(final_ticker) or avg_price
            current = price * qty * conv_factor
            
            total_invested += invested
            total_current += current
        
        # Gerar evolução simulada
        return generate_simulated_evolution(
            start_date=start_date,
            end_date=end_date,
            start_value=total_invested,
            end_value=total_current,
            num_points=len(date_range)
        )
    
    # Se não tiver cache ou precisar de dados reais, usar método otimizado
    try:
        # Preparar tickers
        tickers = []
        ticker_map = {}
        
        for asset in safe_portfolio_data:
            ticker_orig = asset['ticker'].strip().upper()
            
            if format_ticker_func:
                try:
                    final_ticker = format_ticker_func(ticker_orig)
                except Exception:
                    final_ticker = ticker_orig
            else:
                final_ticker = ticker_orig
                if not ticker_orig.endswith('.SA') and not '.' in ticker_orig and not '=' in ticker_orig:
                    final_ticker += '.SA'
                    
            tickers.append(final_ticker)
            ticker_map[final_ticker] = asset
        
        # Taxa de câmbio padrão
        if exchange_rate is None:
            exchange_rate = 5.8187
        
        # Adicionar buffer para garantir dados suficientes
        buffer_days = 14
        start_with_buffer = (start_date_obj - timedelta(days=buffer_days)).strftime('%Y-%m-%d')
        
        # Baixar dados em lote otimizado
        print(f"[EVOLUTION] Baixando dados para {len(set(tickers))} tickers")
        unique_tickers = list(set(tickers))
        
        # Usar lotes menores para evitar erros
        batch_size = 20
        all_ticker_data = {}
        
        for i in range(0, len(unique_tickers), batch_size):
            batch = unique_tickers[i:i+batch_size]
            print(f"[EVOLUTION] Baixando lote {i//batch_size + 1} de {(len(unique_tickers) + batch_size - 1) // batch_size}")
            
            try:
                batch_data = yf.download(
                    tickers=batch,
                    start=start_with_buffer,
                    end=end_date,
                    interval='1d',
                    group_by='ticker',
                    progress=False,
                    threads=True
                )
                
                # Se tiver apenas um ticker, não terá estrutura multi-índice
                if len(batch) == 1 and not isinstance(batch_data.columns, pd.MultiIndex):
                    ticker = batch[0]
                    all_ticker_data[ticker] = batch_data
                else:
                    # Para múltiplos tickers, é um MultiIndex
                    for ticker in batch:
                        if ticker in batch_data.columns.levels[0]:
                            all_ticker_data[ticker] = batch_data[ticker]
            
            except Exception as e:
                print(f"[EVOLUTION] Erro no download do lote {i//batch_size + 1}: {e}")
                
            # Pequena pausa entre lotes
            if len(batch) > 1 and i + batch_size < len(unique_tickers):
                time.sleep(1)
        
        # Calcular valores totais para cada data
        total_values = pd.Series(0.0, index=date_range)
        
        for final_ticker, asset in ticker_map.items():
            try:
                qty = float(asset.get('quantidade', 0))
                avg_price = float(asset.get('preco_medio', 0))
                is_us = not final_ticker.endswith('.SA')
                conv_factor = exchange_rate if is_us else 1.0
                
                # Processar dados históricos deste ticker
                ticker_data = all_ticker_data.get(final_ticker)
                
                if ticker_data is not None and 'Close' in ticker_data.columns:
                    # Processar preços de fechamento
                    close_prices = ticker_data['Close'].copy()
                    
                    # Normalizar índice
                    if hasattr(close_prices.index, 'tz_localize'):
                        close_prices.index = close_prices.index.tz_localize(None)
                    
                    # Preencher valores ausentes
                    close_prices = close_prices.ffill()
                    
                    # Reindexar para o range de datas
                    try:
                        asset_prices = close_prices.reindex(date_range, method='ffill')
                        
                        # Tratar NaN
                        if asset_prices.isna().any():
                            first_valid = asset_prices.first_valid_index()
                            if first_valid:
                                first_value = asset_prices.loc[first_valid]
                                asset_prices = asset_prices.fillna(first_value)
                            else:
                                asset_prices = pd.Series(avg_price, index=date_range)
                    
                    except Exception as e:
                        print(f"[EVOLUTION] Erro ao reindexar {final_ticker}: {e}")
                        asset_prices = pd.Series(avg_price, index=date_range)
                
                else:
                    # Fallback para preço médio
                    asset_prices = pd.Series(avg_price, index=date_range)
                
                # Calcular valores
                asset_values = asset_prices * qty * conv_factor
                total_values = total_values.add(asset_values, fill_value=0)
            
            except Exception as e:
                print(f"[EVOLUTION] Erro ao processar ativo {final_ticker}: {e}")
        
        # Formatar resultado
        evolution_list = [
            {'date': d.strftime('%Y-%m-%d'), 'value': float(v)}
            for d, v in total_values.items()
        ]
        
        # Ordenar por data
        evolution_list.sort(key=lambda x: x['date'])
        
        # Salvar no cache persistente
        if user_id:
            for entry in evolution_list:
                date_obj = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                obj = PortfolioEvolutionCache.query.filter_by(user_id=user_id, date=date_obj).first()
                if obj:
                    obj.total_value = entry['value']
                    obj.last_updated = datetime.now()
                else:
                    db.session.add(PortfolioEvolutionCache(
                        user_id=user_id,
                        date=date_obj,
                        total_value=entry['value'],
                        last_updated=datetime.now()
                    ))
            db.session.commit()
        
        return evolution_list
    
    except Exception as e:
        print(f"[EVOLUTION] Erro geral no cálculo: {e}")
        
        # Tentar recuperar do cache persistente
        if user_id:
            try:
                cached = PortfolioEvolutionCache.query.filter_by(user_id=user_id).order_by(PortfolioEvolutionCache.date.asc()).all()
                
                if cached:
                    print("[FALLBACK] Usando cache persistente devido a erro")
                    cache_df = pd.DataFrame([{'date': c.date, 'value': c.total_value} for c in cached])
                    cache_df = cache_df.set_index('date').sort_index()
                    
                    # Forward fill para cada data
                    values = []
                    last_value = None
                    
                    for d in date_range:
                        d_date = d.date()
                        if d_date in cache_df.index:
                            last_value = cache_df.loc[d_date, 'value']
                        values.append({
                            'date': d.strftime('%Y-%m-%d'), 
                            'value': float(last_value) if last_value is not None else 0.0
                        })
                    
                    return values
            
            except Exception as e2:
                print(f"[EVOLUTION] Erro ao usar cache persistente: {e2}")
        
        return []

def generate_simulated_evolution(start_date, end_date, start_value, end_value, num_points=30):
    """
    Gera uma evolução simulada do portfólio entre dois valores.
    
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
        
        # Gerar datas uniformemente
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
        
        # Gerar valores usando curva de crescimento realista
        values = []
        for i, date in enumerate(dates):
            # Progresso de 0 a 1
            progress = i / (len(dates) - 1)
            
            # Função cúbica para curva S suave
            base_curve = progress * progress * (3 - 2 * progress)
            
            # Valor base neste ponto da curva
            base_value = start_value + (end_value - start_value) * base_curve
            
            # Variação aleatória para simular flutuações de mercado
            # Maior no meio do período, menor no início e fim
            variation_factor = 0.02  # ±2%
            window_factor = 4 * progress * (1 - progress)  # Forma de sino
            random_factor = 1 + (random.random() * 2 - 1) * variation_factor * window_factor
            
            # Último ponto é exatamente o valor final
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
        print(f"[EVOLUTION] Erro ao gerar evolução simulada: {e}")
        # Fallback mínimo
        return [
            {'date': start_date, 'value': float(start_value)},
            {'date': end_date, 'value': float(end_value)}
        ]
