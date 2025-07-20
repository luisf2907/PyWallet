from flask import Blueprint, request, jsonify, session
from services.crypto_service import get_crypto_service
from models.portfolio import Portfolio
from extensions.database import db
from datetime import datetime
import pytz
import json

crypto_routes = Blueprint('crypto_routes', __name__)
crypto_service = get_crypto_service()

@crypto_routes.route('/api/crypto/validate', methods=['POST'])
def validate_crypto():
    """
    Valida se uma criptomoeda existe e retorna informações normalizadas
    
    Expected JSON payload:
    {
        "crypto": "BTC" ou "Bitcoin" ou qualquer input
    }
    
    Returns:
    {
        "isValid": bool,
        "symbol": "BTC",
        "name": "Bitcoin", 
        "coingecko_id": "bitcoin",
        "auto_recognized": bool,
        "current_price": float (optional)
    }
    """
    try:
        data = request.get_json()
        crypto_input = data.get('crypto', '').strip()
        
        if not crypto_input:
            return jsonify({
                'isValid': False,
                'error': 'Input de criptomoeda não fornecido'
            }), 400
        
        # Primeiro, tenta reconhecimento automático
        crypto_info = crypto_service.recognize_crypto(crypto_input)
        
        if crypto_info and crypto_info['auto_recognized']:
            # Foi reconhecida automaticamente (top 10)
            return jsonify({
                'isValid': True,
                'symbol': crypto_info['symbol'],
                'name': crypto_info['name'],
                'coingecko_id': crypto_info['coingecko_id'],
                'auto_recognized': True
            })
        
        # Não foi reconhecida automaticamente, valida via API
        validation_result = crypto_service.validate_via_api(crypto_input)
        
        if validation_result['is_valid']:
            return jsonify({
                'isValid': True,
                'symbol': validation_result['symbol'],
                'name': validation_result['name'],
                'coingecko_id': validation_result['coingecko_id'],
                'auto_recognized': False,
                'current_price': validation_result.get('current_price')
            })
        else:
            return jsonify({
                'isValid': False,
                'error': validation_result.get('error', 'Criptomoeda não encontrada')
            })
    
    except Exception as e:
        print(f"[validate_crypto] Erro: {e}")
        return jsonify({
            'isValid': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@crypto_routes.route('/api/crypto/estimate-price', methods=['POST'])
def estimate_crypto_price():
    """
    Estima preço médio de uma criptomoeda baseado em histórico
    
    Expected JSON payload:
    {
        "crypto": "BTC",
        "days": 30  (optional, default 30)
    }
    
    Returns:
    {
        "success": bool,
        "estimated_price": float,
        "period_days": int,
        "method": "historical_avg" | "current_price",
        "symbol": "BTC",
        "name": "Bitcoin"
    }
    """
    try:
        data = request.get_json()
        crypto_input = data.get('crypto', '').strip()
        days = data.get('days', 30)
        
        if not crypto_input:
            return jsonify({
                'success': False,
                'error': 'Input de criptomoeda não fornecido'
            }), 400
        
        # Estimar preço médio
        estimation_result = crypto_service.estimate_avg_price(crypto_input, days)
        
        if 'error' in estimation_result:
            return jsonify({
                'success': False,
                'error': estimation_result['error']
            })
        
        # Buscar informações básicas da cripto
        crypto_info = crypto_service.recognize_crypto(crypto_input)
        
        return jsonify({
            'success': True,
            'estimated_price': estimation_result['estimated_price'],
            'period_days': estimation_result['period_days'],
            'method': estimation_result['method'],
            'symbol': crypto_info['symbol'] if crypto_info else crypto_input.upper(),
            'name': crypto_info['name'] if crypto_info else crypto_input.title(),
            'note': estimation_result.get('note')
        })
    
    except Exception as e:
        print(f"[estimate_crypto_price] Erro: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@crypto_routes.route('/api/crypto/batch-update', methods=['POST'])
def batch_update_crypto_portfolio():
    """
    Atualiza carteira de criptomoedas em lote (modo Aporte/Retirada)
    
    Expected JSON payload:
    {
        "criptos": [
            {
                "crypto": "BTC",
                "preco": 57000.0 (optional, null para estimativa automática),
                "quantidade": 0.063628
            }
        ]
    }
    """
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        criptos = data.get('criptos', [])
        
        if not criptos:
            return jsonify({'error': 'Lista de criptomoedas não fornecida'}), 400
        
        tz = pytz.timezone('America/Sao_Paulo')
        timestamp = datetime.now(tz)
        
        results = []
        
        for cripto_data in criptos:
            crypto_input = cripto_data.get('crypto', '').strip()
            preco = cripto_data.get('preco')  # Pode ser None/null
            quantidade = cripto_data.get('quantidade')
            
            if not crypto_input or quantidade is None:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': 'Dados incompletos'
                })
                continue
            
            # Validar/normalizar criptomoeda
            crypto_info = crypto_service.recognize_crypto(crypto_input)
            if not crypto_info:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': 'Criptomoeda inválida'
                })
                continue
            
            # Se não foi reconhecida automaticamente, validar via API
            if not crypto_info['auto_recognized']:
                validation = crypto_service.validate_via_api(crypto_input)
                if not validation['is_valid']:
                    results.append({
                        'crypto': crypto_input,
                        'success': False,
                        'error': 'Criptomoeda não encontrada'
                    })
                    continue
                symbol = validation['symbol']
                name = validation['name']
            else:
                symbol = crypto_info['symbol']
                name = crypto_info['name']
            
            # Se preço não foi fornecido, estimar automaticamente
            if preco is None or preco == 0:
                estimation = crypto_service.estimate_avg_price(symbol)
                if 'error' in estimation:
                    results.append({
                        'crypto': crypto_input,
                        'success': False,
                        'error': f'Não foi possível estimar preço: {estimation["error"]}'
                    })
                    continue
                preco = estimation['estimated_price']
            
            try:
                # Salvar na mesma estrutura que o sistema de ações usa
                # Buscar portfólio atual
                portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
                if portfolio:
                    try:
                        portfolio_data = json.loads(portfolio.data)
                    except Exception:
                        portfolio_data = []
                else:
                    portfolio_data = []
                
                # Atualizar ou criar cripto na carteira
                found = False
                for asset in portfolio_data:
                    if asset['ticker'].strip().upper() == symbol and asset.get('tipo_ativo') == 'CRYPTO':
                        old_qtd = float(asset.get('quantidade', 0))
                        old_pm = float(asset.get('preco_medio', 0))
                        
                        if quantidade > 0:  # compra
                            nova_qtd = old_qtd + quantidade
                            if nova_qtd == 0:
                                asset['quantidade'] = 0
                                asset['preco_medio'] = 0
                            else:
                                asset['preco_medio'] = (old_pm * old_qtd + preco * quantidade) / nova_qtd
                                asset['quantidade'] = nova_qtd
                        else:  # venda
                            nova_qtd = old_qtd + quantidade  # quantidade já é negativa
                            if nova_qtd < 0:
                                results.append({
                                    'crypto': symbol,
                                    'success': False,
                                    'error': 'Quantidade insuficiente para venda'
                                })
                                continue
                            asset['quantidade'] = nova_qtd
                            # Preço médio não muda em venda
                        found = True
                        break
                
                if not found:
                    if quantidade > 0:  # compra
                        portfolio_data.append({
                            'ticker': symbol, 
                            'preco_medio': preco, 
                            'quantidade': quantidade,
                            'tipo_ativo': 'CRYPTO'
                        })
                    else:
                        results.append({
                            'crypto': symbol,
                            'success': False,
                            'error': 'Não é possível vender uma cripto que não está na carteira'
                        })
                        continue
                
                # Remove ativos zerados
                portfolio_data = [a for a in portfolio_data if float(a.get('quantidade', 0)) > 0]
                
                # Salva novo portfólio
                new_portfolio = Portfolio(
                    user_id=user_id,
                    data=json.dumps(portfolio_data),
                    filename=f"crypto_update_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                )
                db.session.add(new_portfolio)
                
                results.append({
                    'crypto': symbol,
                    'name': name,
                    'success': True,
                    'preco_usado': preco,
                    'quantidade': quantidade,
                    'estimated_price': preco if cripto_data.get('preco') is None else None
                })
                
            except Exception as e:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': f'Erro ao salvar: {str(e)}'
                })
        
        # Commit das alterações
        db.session.commit()
        
        successful_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'total_processed': len(criptos),
            'successful': successful_count,
            'failed': len(criptos) - successful_count,
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"[batch_update_crypto_portfolio] Erro: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@crypto_routes.route('/api/crypto/overwrite', methods=['POST'])
def overwrite_crypto_portfolio():
    """
    Sobrescreve completamente a carteira de criptomoedas
    
    Expected JSON payload:
    {
        "criptos": [
            {
                "crypto": "BTC",
                "preco": 57000.0 (optional),
                "quantidade": 0.063628
            }
        ]
    }
    """
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        criptos = data.get('criptos', [])
        
        # Primeiro, remove todos os ativos de criptomoedas existentes
        portfolio = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.uploaded_at.desc()).first()
        if portfolio:
            try:
                portfolio_data = json.loads(portfolio.data)
                # Remove apenas criptomoedas, mantém outros ativos
                portfolio_data = [a for a in portfolio_data if a.get('tipo_ativo') != 'CRYPTO']
            except Exception:
                portfolio_data = []
        else:
            portfolio_data = []
        
        if not criptos:
            # Se lista vazia, apenas remove criptomoedas da carteira
            new_portfolio = Portfolio(
                user_id=user_id,
                data=json.dumps(portfolio_data),
                filename=f"crypto_clear_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            )
            db.session.add(new_portfolio)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Carteira de criptomoedas limpa com sucesso'
            })
        
        tz = pytz.timezone('America/Sao_Paulo')
        timestamp = datetime.now(tz)
        
        results = []
        
        for cripto_data in criptos:
            crypto_input = cripto_data.get('crypto', '').strip()
            preco = cripto_data.get('preco')
            quantidade = cripto_data.get('quantidade')
            
            if not crypto_input or quantidade is None or quantidade <= 0:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': 'Dados inválidos (quantidade deve ser positiva)'
                })
                continue
            
            # Validar/normalizar criptomoeda
            crypto_info = crypto_service.recognize_crypto(crypto_input)
            if not crypto_info:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': 'Criptomoeda inválida'
                })
                continue
            
            # Validação via API se necessário
            if not crypto_info['auto_recognized']:
                validation = crypto_service.validate_via_api(crypto_input)
                if not validation['is_valid']:
                    results.append({
                        'crypto': crypto_input,
                        'success': False,
                        'error': 'Criptomoeda não encontrada'
                    })
                    continue
                symbol = validation['symbol']
                name = validation['name']
            else:
                symbol = crypto_info['symbol']
                name = crypto_info['name']
            
            # Estimativa de preço se necessário
            if preco is None or preco == 0:
                estimation = crypto_service.estimate_avg_price(symbol)
                if 'error' in estimation:
                    results.append({
                        'crypto': crypto_input,
                        'success': False,
                        'error': f'Não foi possível estimar preço: {estimation["error"]}'
                    })
                    continue
                preco = estimation['estimated_price']
            
            try:
                # Adicionar cripto à carteira
                portfolio_data.append({
                    'ticker': symbol,
                    'preco_medio': float(preco),
                    'quantidade': float(quantidade),
                    'tipo_ativo': 'CRYPTO'
                })
                
                results.append({
                    'crypto': symbol,
                    'name': name,
                    'success': True,
                    'preco_usado': preco,
                    'quantidade': quantidade,
                    'estimated_price': preco if cripto_data.get('preco') is None else None
                })
                
            except Exception as e:
                results.append({
                    'crypto': crypto_input,
                    'success': False,
                    'error': f'Erro ao salvar: {str(e)}'
                })
        
        # Commit das alterações
        db.session.commit()
        
        successful_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'message': 'Carteira de criptomoedas sobrescrita com sucesso',
            'total_processed': len(criptos),
            'successful': successful_count,
            'failed': len(criptos) - successful_count,
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"[overwrite_crypto_portfolio] Erro: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@crypto_routes.route('/api/crypto/cleanup-cache', methods=['POST'])
def cleanup_crypto_cache():
    """Endpoint para limpeza manual do cache (útil para desenvolvimento)"""
    try:
        crypto_service.cleanup_cache()
        return jsonify({
            'success': True,
            'message': 'Cache de criptomoedas limpo com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao limpar cache: {str(e)}'
        }), 500
