import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta

# Database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'pywallet.db'))

def insert_test_data():
    print(f"Using database at: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify if portfolio_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
        if not cursor.fetchone():
            print("Creating portfolio_history table...")
            cursor.execute('''
            CREATE TABLE portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            print("Table created successfully")
        
        # Get users from the database
        cursor.execute("SELECT id FROM user")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database")
            return
            
        print(f"Found {len(users)} users")
        
        # Get most recent portfolio for each user
        for user_row in users:
            user_id = user_row[0]
            
            # Get the most recent portfolio
            cursor.execute("""
            SELECT data FROM portfolio 
            WHERE user_id = ? 
            ORDER BY uploaded_at DESC 
            LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                print(f"No portfolio found for user {user_id}")
                continue
                
            portfolio_data = result[0]
            
            # Create sample data for different dates
            now = datetime.now()
            
            # Insert data for the last 7 days
            for days_back in range(7):
                target_date = now - timedelta(days=days_back)
                date_str = target_date.strftime('%Y-%m-%d')
                
                # Check if record already exists
                cursor.execute("""
                SELECT id FROM portfolio_history 
                WHERE user_id = ? AND date = ?
                """, (user_id, date_str))
                
                if cursor.fetchone():
                    print(f"Record already exists for user {user_id} on {date_str}")
                else:
                    # Insert new record
                    cursor.execute("""
                    INSERT INTO portfolio_history (user_id, date, data)
                    VALUES (?, ?, ?)
                    """, (user_id, date_str, portfolio_data))
                    print(f"Inserted record for user {user_id} on {date_str}")
            
            # Insert April 22, 2025 data specifically
            april_date = '2025-04-22'
            
            # Check if record already exists
            cursor.execute("""
            SELECT id FROM portfolio_history 
            WHERE user_id = ? AND date = ?
            """, (user_id, april_date))
            
            if cursor.fetchone():
                print(f"April 22 record already exists for user {user_id}")
                # Update it with current portfolio data
                cursor.execute("""
                UPDATE portfolio_history
                SET data = ?
                WHERE user_id = ? AND date = ?
                """, (portfolio_data, user_id, april_date))
                print(f"Updated April 22 record for user {user_id}")
            else:
                # Insert new record
                cursor.execute("""
                INSERT INTO portfolio_history (user_id, date, data)
                VALUES (?, ?, ?)
                """, (user_id, april_date, portfolio_data))
                print(f"Inserted April 22 record for user {user_id}")
        
        # Commit all changes
        conn.commit()
        print("All test data inserted successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    insert_test_data()
