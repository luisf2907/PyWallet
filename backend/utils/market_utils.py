from datetime import datetime, time as dt_time
import pytz

def is_market_open():
    """
    Verifica se o mercado está aberto no momento atual.
    Considera o horário de funcionamento da B3 e da NYSE, convertidos para horário de Brasília.
    
    Returns:
        bool: True se algum mercado estiver aberto, False caso contrário
    """
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    weekday = now.weekday()  # 0=Segunda,6=Domingo
    current_time = now.time()

    # Finais de semana - mercado fechado
    if weekday >= 5:
        return False

    # B3: 10:00 - 17:55
    b3_open_time = dt_time(10, 0)
    b3_close_time = dt_time(17, 55)
    
    # NYSE (aproximado, em horário de Brasília)
    ny_open_time_br = dt_time(10, 30)
    ny_close_time_br = dt_time(17, 0)

    is_b3_open = b3_open_time <= current_time <= b3_close_time
    is_nyse_open = ny_open_time_br <= current_time <= ny_close_time_br
    
    return is_b3_open or is_nyse_open

def get_next_market_open():
    """
    Retorna o próximo horário de abertura do mercado.
    
    Returns:
        datetime: Data e hora da próxima abertura do mercado
    """
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    weekday = now.weekday()  # 0=Segunda,6=Domingo
    
    # Se for final de semana, a próxima abertura será na segunda-feira
    if weekday >= 5:  # Sábado ou domingo
        days_to_add = 7 - weekday  # Dias para segunda-feira
        next_opening = now.replace(hour=10, minute=0, second=0, microsecond=0)
        return next_opening.replace(day=next_opening.day + days_to_add)
    
    # Se for durante a semana e antes da abertura
    if now.time() < dt_time(10, 0):
        return now.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Se for durante a semana após o fechamento
    if now.time() > dt_time(17, 55):
        if weekday == 4:  # Sexta-feira
            days_to_add = 3  # Próxima abertura na segunda-feira
        else:
            days_to_add = 1  # Próxima abertura no dia seguinte
        next_opening = now.replace(hour=10, minute=0, second=0, microsecond=0)
        return next_opening.replace(day=next_opening.day + days_to_add)
    
    # Se estiver dentro do horário de funcionamento, já está aberto
    return now