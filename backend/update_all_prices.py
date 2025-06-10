import os
import sys
from datetime import datetime
import pytz

# Ajusta o path para importar módulos do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.extensions.database import db
from backend.models.price import PriceCache
from backend.services.price_service import get_price


def update_all_prices():
    tz = pytz.timezone('America/Sao_Paulo')
    tickers = [p.ticker for p in PriceCache.query.all()]
    print(f"[UPDATE_ALL_PRICES] Atualizando {len(tickers)} tickers...")
    for ticker in tickers:
        price = get_price(ticker)
        if price is not None:
            obj = PriceCache.query.filter_by(ticker=ticker).first()
            if obj:
                obj.price = price
                obj.last_updated = datetime.now(tz)
                db.session.commit()
                print(f"[OK] {ticker}: {price}")
            else:
                db.session.add(PriceCache(
                    user_id=None,
                    ticker=ticker,
                    price=price,
                    last_updated=datetime.now(tz)
                ))
                db.session.commit()
                print(f"[NEW] {ticker}: {price}")
        else:
            print(f"[FAIL] {ticker}: preço não encontrado")
    print("[UPDATE_ALL_PRICES] Atualização concluída.")

if __name__ == "__main__":
    from backend.app import app
    with app.app_context():
        update_all_prices()
