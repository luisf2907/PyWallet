import os
import json
import pandas as pd
from datetime import datetime
from flask import current_app

from extensions.database import db
from models.portfolio import Portfolio
from services.price_service import get_price, get_cached_dollar_rate
from services.dividend_service import update_dividends_for_user
from utils.ticker_utils import format_ticker
from utils.cache_utils import clear_evolution_cache_for_user

def upload_portfolio(user_id, file):
    """
    Processa e salva um arquivo de portfólio para um usuário.
    
    Args:
        user_id (str): ID do usuário
        file (FileStorage): Arquivo enviado (CSV ou XLSX)
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    if not file or file.filename == '':
        return {'error': 'Nenhum arquivo enviado'}, 400
        
    if not file.filename.endswith(('.csv', '.xlsx')):
        return {'error': 'Formato de arquivo não suportado. Use CSV ou XLSX'}, 400
    
    # Gera nome único para o arquivo
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(file.filename)[1]}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    
    try:
        # Salva o arquivo
        file.save(filepath)
        
        # Processa o arquivo
        portfolio_data, summary = process_portfolio_file(filepath)
        
        # Salva no banco de dados
        portfolio = Portfolio(
            user_id=user_id,
            data=json.dumps(portfolio_data),
            filename=filename
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # Limpa cache de evolução do portfólio para este usuário
        clear_evolution_cache_for_user(user_id)
        
        # Inicia atualização de cache em background
        from models.user import User
        user = User.query.get(user_id)
        if user:
            update_dividends_for_user(user)
        
        return {
            'message': 'Portfólio carregado com sucesso',
            'portfolio_summary': {
                'total_assets': summary['total_assets'],
                'total_value': summary['total_value']
            }
        }, 200
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        return {'error': f'Erro ao processar arquivo: {str(e)}'}, 500

def process_portfolio_file(filepath):
    """
    Processa um arquivo de portfólio (CSV ou XLSX).
    
    Args:
        filepath (str): Caminho para o arquivo
        
    Returns:
        tuple: (list, dict) - Dados do portfólio e resumo
    """
    if filepath.endswith('.csv'):
        df = process_csv(filepath)
    else:
        df = process_excel(filepath)
        
    # Normaliza dados
    df['ticker'] = df['ticker'].astype(str).str.strip().str.upper()
    df['preco_medio'] = pd.to_numeric(df['preco_medio'], errors='coerce')
    df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
    
    # Tenta converter valores com vírgula
    if df['preco_medio'].isna().all():
        df['preco_medio'] = df['preco_medio'].astype(str).str.replace(',', '.').astype(float)
        
    # Remove linhas com valores inválidos
    df = df.dropna()
    df = df[df['quantidade'] > 0]
    
    # Calcula valor total
    df['valor_total'] = df['preco_medio'] * df['quantidade']
    
    # Converte para lista de dicionários
    portfolio_data = df.to_dict('records')
    
    # Resumo básico
    summary = {
        'total_assets': len(df),
        'total_value': df['valor_total'].sum()
    }
    
    return portfolio_data, summary

def process_csv(filepath):
    """
    Processa um arquivo CSV de portfólio.
    
    Args:
        filepath (str): Caminho para o arquivo CSV
        
    Returns:
        DataFrame: DataFrame pandas com os dados do portfólio
    """
    try:
        df = pd.read_csv(filepath)
        if df.shape[1] >= 3:
            cols = df.columns.str.lower()
            if any(col in ['código', 'ticker', 'ativo'] for col in cols):
                col_ticker = next((i for i, col in enumerate(cols) if col in ['código', 'ticker', 'ativo']), 0)
                col_price = next((i for i, col in enumerate(cols) if col in ['preço', 'medio', 'médio']), 1)
                col_qty = next((i for i, col in enumerate(cols) if col in ['qtd', 'quantidade', 'quant']), 2)
                df = df.iloc[:, [col_ticker, col_price, col_qty]]
                df.columns = ['ticker', 'preco_medio', 'quantidade']
            else:
                df = df.iloc[:, :3]
                df.columns = ['ticker', 'preco_medio', 'quantidade']
        else:
            df = pd.read_csv(filepath, sep=';')
            df = df.iloc[:, :3]
            df.columns = ['ticker', 'preco_medio', 'quantidade']
    except Exception:
        df = pd.read_csv(filepath, header=None)
        if df.shape[1] >= 3:
            df = df.iloc[:, :3]
            df.columns = ['ticker', 'preco_medio', 'quantidade']
        else:
            raise ValueError("CSV não tem pelo menos 3 colunas")
            
    # Remove cabeçalho se estiver nos dados
    if isinstance(df['ticker'].iloc[0], str) and df['ticker'].iloc[0].lower() in ['código', 'ticker', 'ativo']:
        df = df.iloc[1:].reset_index(drop=True)
        
    return df

def process_excel(filepath):
    """
    Processa um arquivo Excel de portfólio.
    
    Args:
        filepath (str): Caminho para o arquivo Excel
        
    Returns:
        DataFrame: DataFrame pandas com os dados do portfólio
    """
    try:
        df = pd.read_excel(filepath)
        if df.shape[1] >= 3:
            cols = [str(col).lower() for col in df.columns]
            if any('código' in col or 'ticker' in col or 'ativo' in col for col in cols):
                col_ticker = next((i for i, col in enumerate(cols) if 'código' in col or 'ticker' in col or 'ativo' in col), 0)
                col_price = next((i for i, col in enumerate(cols) if 'preço' in col or 'medio' in col or 'médio' in col), 1)
                col_qty = next((i for i, col in enumerate(cols) if 'qtd' in col or 'quantidade' in col or 'quant' in col), 2)
                df = df.iloc[:, [col_ticker, col_price, col_qty]]
                df.columns = ['ticker', 'preco_medio', 'quantidade']
            else:
                df = df.iloc[:, :3]
                df.columns = ['ticker', 'preco_medio', 'quantidade']
    except Exception:
        df = pd.read_excel(filepath, header=None)
        if df.shape[1] >= 3:
            df = df.iloc[:, :3]
            df.columns = ['ticker', 'preco_medio', 'quantidade']
        else:
            raise ValueError("XLSX não tem pelo menos 3 colunas")
            
    # Remove cabeçalho se estiver nos dados
    if isinstance(df['ticker'].iloc[0], str) and df['ticker'].iloc[0].lower() in ['código', 'ticker', 'ativo']:
        df = df.iloc[1:].reset_index(drop=True)
        
    return df

def get_portfolio_distribution(user_id):
    """
    Calcula a distribuição do portfólio por ticker.
    
    Args:
        user_id (str): ID do usuário
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    # Busca o portfólio mais recente do usuário
    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if not portfolio:
        return {'error': 'Portfólio não encontrado'}, 404
        
    try:
        portfolio_data = json.loads(portfolio.data)
    except Exception as e:
        return {'distribution': []}, 200
        
    if not portfolio_data:
        return {'distribution': []}, 200
        
    # Busca preços atuais
    from models.price import PriceCache
    price_cache = {p.ticker: p.price for p in PriceCache.query.all()}
    exch_rate = get_cached_dollar_rate()
    
    total_current_value = 0.0
    dist_map = {}
    
    # Calcula o valor atual de cada ativo
    for asset in portfolio_data:
        ticker_orig = asset['ticker'].strip().upper()
        final_ticker = format_ticker(ticker_orig)
        try:
            avg_price = float(asset.get('preco_medio', 0))
            quantity = float(asset.get('quantidade', 0))
        except:
            continue
            
        is_us = not final_ticker.endswith('.SA')
        current_price = price_cache.get(ticker_orig) or price_cache.get(final_ticker) or avg_price
        current_value = current_price * quantity * exch_rate if is_us else current_price * quantity
        
        if current_value <= 0:
            continue
            
        total_current_value += current_value
        
        # Adiciona sufixo para identificar tipo de ativo
        label = ticker_orig
        if is_us:
            label += ' (US)'
        elif final_ticker.endswith('34.SA') or final_ticker.endswith('35.SA') or final_ticker.endswith('32.SA'):
            label += ' (BDR)'
            
        dist_map[label] = dist_map.get(label, 0) + current_value
    
    # Calcula percentuais
    distribution_list = []
    for tck, val in dist_map.items():
        pct = (val / total_current_value) * 100 if total_current_value else 0
        distribution_list.append({'ticker': tck, 'percentage': pct})
        
    # Ordena por percentual
    distribution_list.sort(key=lambda x: x['percentage'], reverse=True)
    
    return {'distribution': distribution_list}, 200

# A função generate_template_file foi removida pois o template agora é obtido diretamente do Google Drive

def register_transaction(user_id, tipo, ticker, preco, quantidade):
    """
    Registra uma transação (compra/venda) no portfólio.
    
    Args:
        user_id (str): ID do usuário
        tipo (str): Tipo da transação ('compra' ou 'venda')
        ticker (str): Código do ticker
        preco (float): Preço da transação
        quantidade (int): Quantidade negociada
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    # Validação dos dados
    ticker = ticker.strip().upper()
    if not ticker or preco <= 0 or quantidade <= 0 or tipo not in ['compra', 'venda']:
        return {'error': 'Dados inválidos'}, 400
        
    # Validação do ticker (checa se existe na B3 ou EUA)
    try:
        import yfinance as yf
        yf_ticker = format_ticker(ticker)
        tinfo = yf.Ticker(yf_ticker).info
        if not tinfo.get('regularMarketPrice') and not tinfo.get('currentPrice'):
            return {'error': 'Ticker não encontrado'}, 400
    except Exception:
        return {'error': 'Ticker não encontrado'}, 400
        
    # Carregar portfólio atual
    portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
    if portfolio:
        try:
            portfolio_data = json.loads(portfolio.data)
        except Exception:
            portfolio_data = []
    else:
        portfolio_data = []
        
    # Atualizar ou criar ativo
    found = False
    for asset in portfolio_data:
        if asset['ticker'].strip().upper() == ticker:
            old_qtd = float(asset.get('quantidade', 0))
            old_pm = float(asset.get('preco_medio', 0))
            
            if tipo == 'compra':
                nova_qtd = old_qtd + quantidade
                if nova_qtd == 0:
                    asset['quantidade'] = 0
                    asset['preco_medio'] = 0
                else:
                    asset['preco_medio'] = (old_pm * old_qtd + preco * quantidade) / nova_qtd
                    asset['quantidade'] = nova_qtd
            else:  # venda
                nova_qtd = old_qtd - quantidade
                if nova_qtd < 0:
                    return {'error': 'Quantidade insuficiente para venda'}, 400
                asset['quantidade'] = nova_qtd
                # Preço médio não muda em venda
            found = True
            break
            
    if not found:
        if tipo == 'compra':
            portfolio_data.append({'ticker': ticker, 'preco_medio': preco, 'quantidade': quantidade})
        else:
            return {'error': 'Não é possível vender um ativo que não está na carteira'}, 400
            
    # Remove ativos zerados
    portfolio_data = [a for a in portfolio_data if float(a.get('quantidade', 0)) > 0]
    
    # Salva novo portfólio
    new_portfolio = Portfolio(
        user_id=user_id,
        data=json.dumps(portfolio_data),
        filename=f"aporte_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    )
    db.session.add(new_portfolio)
    db.session.commit()
    
    # Limpa cache de evolução do portfólio para este usuário
    clear_evolution_cache_for_user(user_id)
    
    return {'message': 'Transação registrada com sucesso!'}, 200

def update_empresa_manual(user_id, codigo, preco, quantidade, tipo_operacao='compra'):
    """
    Atualiza manualmente a posição de uma empresa no portfólio.
    
    Args:
        user_id (str): ID do usuário
        codigo (str): Código do ticker
        preco (float): Novo preço médio
        quantidade (int/float): Nova quantidade
        tipo_operacao (str): Tipo da operação ('compra' ou 'venda')
        
    Returns:
        tuple: (dict, int) - Resposta e código HTTP
    """
    try:
        # Validações básicas
        codigo = codigo.strip().upper()
        if not codigo:
            return {'error': 'Código da empresa não informado'}, 400
        
        try:
            preco = float(preco)
            if ',' in str(preco):
                preco = float(str(preco).replace(',', '.'))
        except (ValueError, TypeError):
            return {'error': 'Preço inválido'}, 400
            
        try:
            quantidade = float(quantidade)
            if ',' in str(quantidade):
                quantidade = float(str(quantidade).replace(',', '.'))
        except (ValueError, TypeError):
            return {'error': 'Quantidade inválida'}, 400
        
        # Validar se o ticker existe
        try:
            import yfinance as yf
            yf_ticker = format_ticker(codigo)
            tinfo = yf.Ticker(yf_ticker).info
            if not tinfo.get('regularMarketPrice') and not tinfo.get('currentPrice'):
                return {'error': 'Ticker não encontrado'}, 400
        except Exception:
            # Se falhar a validação online, ainda permite atualizar
            print(f"Erro ao validar ticker {codigo}, mas permitindo atualização")
          # Ajustar sinal da quantidade baseado no tipo de operação
        quantidade_com_sinal = quantidade
        if tipo_operacao == 'venda':
            quantidade_com_sinal = -quantidade  # Quantidade negativa para venda
            
        # Carregar portfólio atual
        portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
        if not portfolio:
            # Se não há portfólio, criar um novo com apenas este ativo
            if tipo_operacao == 'compra' and quantidade > 0:  # Só adiciona na compra
                portfolio_data = [{'ticker': codigo, 'preco_medio': preco, 'quantidade': quantidade}]
            else:
                return {'error': 'Não é possível vender um ativo que não existe no portfólio'}, 400
        else:
            try:
                portfolio_data = json.loads(portfolio.data)
            except Exception:
                portfolio_data = []
            
            # Procurar e atualizar o ativo
            found = False
            for asset in portfolio_data:
                if asset['ticker'].strip().upper() == codigo:
                    # Em caso de compra/venda, ajustar valores
                    if tipo_operacao == 'compra' or tipo_operacao == 'venda':
                        # Calcular nova quantidade
                        nova_quantidade = float(asset['quantidade']) + quantidade_com_sinal
                        
                        # Se for compra, recalcular o preço médio
                        if tipo_operacao == 'compra' and nova_quantidade > 0:
                            valor_atual = float(asset['preco_medio']) * float(asset['quantidade'])
                            valor_novo = preco * quantidade
                            valor_total = valor_atual + valor_novo
                            nova_quantidade_total = float(asset['quantidade']) + quantidade
                            novo_preco_medio = valor_total / nova_quantidade_total
                            asset['preco_medio'] = novo_preco_medio
                        
                        # Atualizar quantidade
                        if nova_quantidade >= 0:  # Garantir que não fica negativo
                            asset['quantidade'] = nova_quantidade
                        else:
                            return {'error': 'A quantidade a vender é maior que a disponível no portfólio'}, 400
                    else:
                        # Atualização manual direta
                        asset['preco_medio'] = preco
                        asset['quantidade'] = quantidade
                        
                    found = True
                    break            # Se não encontrou e é uma compra, adicionar novo
            if not found and tipo_operacao == 'compra' and quantidade > 0:
                portfolio_data.append({'ticker': codigo, 'preco_medio': preco, 'quantidade': quantidade})
            elif not found and tipo_operacao == 'venda':
                return {'error': f'Não é possível vender {codigo} pois não existe no portfólio'}, 404
            elif not found:
                return {'error': f'Empresa {codigo} não encontrada no portfólio'}, 404
            
            # Remover ativos com quantidade zero ou negativa
            portfolio_data = [a for a in portfolio_data if float(a.get('quantidade', 0)) > 0]
        
        # Salvar novo estado do portfólio
        new_portfolio = Portfolio(
            user_id=user_id,
            data=json.dumps(portfolio_data),
            filename=f"manual_update_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )
        db.session.add(new_portfolio)
        db.session.commit()
          # Limpar cache
        clear_evolution_cache_for_user(user_id)
        
        operacao_desc = 'comprada' if tipo_operacao == 'compra' else 'vendida'
        return {
            'message': f'Operação de {tipo_operacao.upper()} para {codigo} registrada com sucesso!',
            'ticker': codigo,
            'preco_medio': preco,
            'quantidade': quantidade,
            'tipo_operacao': tipo_operacao
        }, 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f'Erro ao atualizar empresa: {str(e)}'}, 500