import sqlite3
import os
import json
from datetime import datetime

def check_portfolio_history():
    db_path = os.path.join('..', '..', 'instance', 'pywallet.db')
    print(f"Checking database at: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify if portfolio_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
        if not cursor.fetchone():
            print("The portfolio_history table does not exist!")
            return
            
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM portfolio_history")
        total = cursor.fetchone()[0]
        print(f"Total records in portfolio_history: {total}")
        
        # Get distribution by date
        cursor.execute("SELECT date, COUNT(*) FROM portfolio_history GROUP BY date ORDER BY date DESC")
        date_counts = cursor.fetchall()
        print("\nRecords by date:")
        for date_str, count in date_counts:
            print(f"  {date_str}: {count} records")
            
        # Check April 2025 records specifically
        cursor.execute("SELECT * FROM portfolio_history WHERE date LIKE '2025-04-%'")
        april_records = cursor.fetchall()
        print(f"\nApril 2025 records: {len(april_records)}")
        
        for record in april_records:
            record_id, user_id, date_str, data_json, created_at = record
            print(f"ID: {record_id}, User: {user_id}, Date: {date_str}")
            try:
                portfolio_data = json.loads(data_json)
                print(f"  Assets: {len(portfolio_data)} items")
                for asset in portfolio_data[:3]:
                    print(f"    {asset.get('ticker', 'N/A')}: {asset.get('quantidade', 'N/A')} @ {asset.get('preco_medio', 'N/A')}")
            except Exception as e:
                print(f"  Error decoding JSON: {e}")
                
        # Check the most recent records
        cursor.execute("SELECT * FROM portfolio_history ORDER BY id DESC LIMIT 5")
        recent_records = cursor.fetchall()
        print("\nMost recent 5 records:")
        for record in recent_records:
            record_id, user_id, date_str, data_json, created_at = record
            print(f"ID: {record_id}, User: {user_id}, Date: {date_str}")
            
    except Exception as e:
        print(f"Error accessing database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            
if __name__ == "__main__":
    check_portfolio_history()
