import re

def format_ticker(ticker):
    """
    Adiciona '.SA' se for ticker BR (sem ponto ou '='); senão retorna o original.
    
    Args:
        ticker (str): Código do ticker a ser formatado
        
    Returns:
        str: Ticker formatado com sufixo .SA se necessário
    """
    ticker = ticker.strip().upper()
    
    # Normaliza ticker fracionado (ex: VALE3F -> VALE3)
    if re.match(r'^[A-Z0-9]{4,6}F$', ticker):
        ticker = ticker[:-1]
    
    if '=' in ticker:
        return ticker
    if '.' in ticker:
        return ticker
    if not re.fullmatch(r'[A-Z]{1,5}', ticker):
        return ticker + '.SA'
    return ticker

def is_us_stock(ticker):
    """
    Verifica se um ticker é de uma ação americana (padrão de 1-5 letras maiúsculas).
    
    Args:
        ticker (str): Código do ticker a ser verificado
        
    Returns:
        bool: True se for uma ação americana, False caso contrário
    """
    return re.fullmatch(r"[A-Z]{1,5}", ticker.strip().upper()) is not None

def is_bdr(ticker):
    """
    Verifica se um ticker é de um BDR (termina com 32, 34 ou 35 e .SA).
    
    Args:
        ticker (str): Código do ticker a ser verificado
        
    Returns:
        bool: True se for um BDR, False caso contrário
    """
    ticker = ticker.strip().upper()
    return ticker.endswith(('32.SA', '34.SA', '35.SA'))

def get_ticker_type(ticker):
    """
    Retorna o tipo do ticker (BR, US, BDR, FX).
    
    Args:
        ticker (str): Código do ticker a ser verificado
        
    Returns:
        str: Tipo do ticker ('BR', 'US', 'BDR', 'FX')
    """
    ticker = ticker.strip().upper()
    if '=' in ticker:
        return 'FX'
    if is_bdr(ticker):
        return 'BDR'
    if ticker.endswith('.SA'):
        return 'BR'
    if is_us_stock(ticker):
        return 'US'
    # Caso não identificado, assume BR
    return 'BR'

def normalize_fractional_ticker(ticker):
    """
    Converte um ticker fracionado para sua versão normal.
    
    Args:
        ticker (str): Código do ticker a ser normalizado
        
    Returns:
        str: Ticker normalizado (sem o F no final se for fracionado)
    """
    if not ticker:
        return ''
    
    ticker = ticker.strip().upper()
    
    # Verifica se é um ticker fracionado (termina com F)
    if re.match(r'^[A-Z0-9]{4,6}F$', ticker):
        return ticker[:-1]
    
    return ticker