import requests
import json
from datetime import datetime, timedelta
from flask import current_app
import threading
import time

# Lista das 10 maiores criptomoedas para reconhecimento automático
TOP_10_CRYPTOS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum', 
    'USDT': 'tether',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'SOL': 'solana',
    'USDC': 'usd-coin',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'AVAX': 'avalanche-2'
}

# Mapa reverso: nome completo -> sigla
CRYPTO_NAME_TO_SYMBOL = {
    'BITCOIN': 'BTC',
    'ETHEREUM': 'ETH',
    'TETHER': 'USDT',
    'BINANCE COIN': 'BNB',
    'XRP': 'XRP',
    'SOLANA': 'SOL',
    'USD COIN': 'USDC',
    'CARDANO': 'ADA',
    'DOGECOIN': 'DOGE',
    'AVALANCHE': 'AVAX'
}

# Cache global para validações e preços
crypto_cache = {
    'validated_cryptos': {},  # Cache de criptos já validadas
    'price_cache': {},        # Cache de preços
    'last_cleanup': datetime.now()
}

# Lock para operações thread-safe no cache
crypto_cache_lock = threading.Lock()

class CryptoService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 10
        
    def recognize_crypto(self, input_text):
        """
        Reconhece criptomoeda da lista das 10 maiores ou normaliza input
        
        Args:
            input_text (str): Input do usuário (sigla ou nome)
            
        Returns:
            dict: {
                'symbol': str,           # Sigla normalizada (ex: BTC)
                'coingecko_id': str,     # ID para CoinGecko API (ex: bitcoin)
                'name': str,             # Nome completo (ex: Bitcoin)
                'auto_recognized': bool  # Se foi reconhecida automaticamente
            }
        """
        if not input_text:
            return None
            
        input_upper = input_text.strip().upper()
        
        # Verifica se é uma sigla das top 10
        if input_upper in TOP_10_CRYPTOS:
            coingecko_id = TOP_10_CRYPTOS[input_upper]
            name = self._get_name_from_symbol(input_upper)
            return {
                'symbol': input_upper,
                'coingecko_id': coingecko_id,
                'name': name,
                'auto_recognized': True
            }
        
        # Verifica se é um nome completo das top 10
        if input_upper in CRYPTO_NAME_TO_SYMBOL:
            symbol = CRYPTO_NAME_TO_SYMBOL[input_upper]
            coingecko_id = TOP_10_CRYPTOS[symbol]
            return {
                'symbol': symbol,
                'coingecko_id': coingecko_id,
                'name': input_text.title(),
                'auto_recognized': True
            }
        
        # Não foi reconhecida automaticamente
        return {
            'symbol': input_upper,
            'coingecko_id': None,
            'name': input_text.title(),
            'auto_recognized': False
        }
    
    def _get_name_from_symbol(self, symbol):
        """Converte sigla para nome completo das top 10"""
        name_map = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'USDT': 'Tether',
            'BNB': 'Binance Coin',
            'XRP': 'XRP',
            'SOL': 'Solana',
            'USDC': 'USD Coin',
            'ADA': 'Cardano',
            'DOGE': 'Dogecoin',
            'AVAX': 'Avalanche'
        }
        return name_map.get(symbol, symbol)
    
    def validate_via_api(self, crypto_input):
        """
        Valida criptomoeda via CoinGecko API
        
        Args:
            crypto_input (str): Nome ou sigla da criptomoeda
            
        Returns:
            dict: {
                'is_valid': bool,
                'symbol': str,           # Sigla encontrada
                'coingecko_id': str,     # ID para futuras consultas
                'name': str,             # Nome oficial
                'current_price': float   # Preço atual em USD (se disponível)
            }
        """
        if not crypto_input:
            return {'is_valid': False, 'error': 'Input vazio'}
        
        # Verificar cache primeiro
        with crypto_cache_lock:
            cache_key = crypto_input.upper()
            if cache_key in crypto_cache['validated_cryptos']:
                cached_result = crypto_cache['validated_cryptos'][cache_key]
                # Cache válido por 1 hora
                if datetime.now() - cached_result['timestamp'] < timedelta(hours=1):
                    return cached_result['data']
        
        try:
            # Buscar via API de search do CoinGecko
            search_url = f"{self.base_url}/search"
            params = {'query': crypto_input}
            
            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            search_data = response.json()
            coins = search_data.get('coins', [])
            
            if not coins:
                result = {'is_valid': False, 'error': 'Criptomoeda não encontrada'}
            else:
                # Pega o primeiro resultado (mais relevante)
                coin = coins[0]
                
                # Buscar preço atual
                current_price = self._get_current_price(coin['id'])
                
                result = {
                    'is_valid': True,
                    'symbol': coin['symbol'].upper(),
                    'coingecko_id': coin['id'],
                    'name': coin['name'],
                    'current_price': current_price
                }
            
            # Salvar no cache
            with crypto_cache_lock:
                crypto_cache['validated_cryptos'][cache_key] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
            
            return result
            
        except requests.RequestException as e:
            print(f"[CryptoService] Erro na API do CoinGecko: {e}")
            return {'is_valid': False, 'error': f'Erro na API: {str(e)}'}
        except Exception as e:
            print(f"[CryptoService] Erro inesperado: {e}")
            return {'is_valid': False, 'error': f'Erro inesperado: {str(e)}'}
    
    def _get_current_price(self, coingecko_id):
        """
        Busca preço atual de uma criptomoeda
        
        Args:
            coingecko_id (str): ID da CoinGecko (ex: 'bitcoin')
            
        Returns:
            float: Preço atual em USD ou None se não disponível
        """
        try:
            price_url = f"{self.base_url}/simple/price"
            params = {
                'ids': coingecko_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(price_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            price_data = response.json()
            return price_data.get(coingecko_id, {}).get('usd')
            
        except Exception as e:
            print(f"[CryptoService] Erro ao buscar preço para {coingecko_id}: {e}")
            return None
    
    def estimate_avg_price(self, crypto_symbol, days=30):
        """
        Estima preço médio de uma criptomoeda baseado em histórico
        
        Args:
            crypto_symbol (str): Sigla da criptomoeda (ex: BTC)
            days (int): Número de dias para calcular a média
            
        Returns:
            dict: {
                'estimated_price': float,
                'period_days': int,
                'method': str  # 'historical_avg' ou 'current_price'
            }
        """
        # Primeiro, identifica a criptomoeda
        crypto_info = self.recognize_crypto(crypto_symbol)
        if not crypto_info:
            return {'error': 'Criptomoeda não reconhecida'}
        
        # Se não foi reconhecida automaticamente, valida via API
        if not crypto_info['auto_recognized']:
            validation = self.validate_via_api(crypto_symbol)
            if not validation['is_valid']:
                return {'error': 'Criptomoeda inválida'}
            coingecko_id = validation['coingecko_id']
        else:
            coingecko_id = crypto_info['coingecko_id']
        
        try:
            # Buscar histórico de preços
            history_url = f"{self.base_url}/coins/{coingecko_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(history_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            if prices:
                # Calcular média dos preços
                price_values = [price[1] for price in prices]
                avg_price = sum(price_values) / len(price_values)
                
                return {
                    'estimated_price': round(avg_price, 8),
                    'period_days': len(price_values),
                    'method': 'historical_avg'
                }
            else:
                # Fallback: usar preço atual
                current_price = self._get_current_price(coingecko_id)
                if current_price:
                    return {
                        'estimated_price': current_price,
                        'period_days': 1,
                        'method': 'current_price'
                    }
                else:
                    return {'error': 'Não foi possível obter preço'}
                    
        except Exception as e:
            print(f"[CryptoService] Erro ao estimar preço médio: {e}")
            # Fallback: tentar preço atual
            current_price = self._get_current_price(coingecko_id)
            if current_price:
                return {
                    'estimated_price': current_price,
                    'period_days': 1,
                    'method': 'current_price',
                    'note': 'Usando preço atual devido a erro no histórico'
                }
            return {'error': f'Erro ao estimar preço: {str(e)}'}
    
    def cleanup_cache(self):
        """Remove entradas antigas do cache (chamado periodicamente)"""
        with crypto_cache_lock:
            now = datetime.now()
            
            # Limpar validações antigas (mais de 1 hora)
            expired_validations = []
            for key, data in crypto_cache['validated_cryptos'].items():
                if now - data['timestamp'] > timedelta(hours=1):
                    expired_validations.append(key)
            
            for key in expired_validations:
                del crypto_cache['validated_cryptos'][key]
            
            # Limpar preços antigos (mais de 15 minutos)
            expired_prices = []
            for key, data in crypto_cache['price_cache'].items():
                if now - data['timestamp'] > timedelta(minutes=15):
                    expired_prices.append(key)
            
            for key in expired_prices:
                del crypto_cache['price_cache'][key]
            
            crypto_cache['last_cleanup'] = now
            
            if expired_validations or expired_prices:
                print(f"[CryptoService] Cache cleanup: removidas {len(expired_validations)} validações e {len(expired_prices)} preços")

# Instância global do serviço
crypto_service = CryptoService()

def get_crypto_service():
    """Retorna a instância global do CryptoService"""
    return crypto_service
