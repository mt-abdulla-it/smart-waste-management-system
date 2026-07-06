import sqlite3
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    # Create Bins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            fill_level INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create CollectionLogs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CollectionLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER,
            collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(bin_id) REFERENCES Bins(id)
        )
    ''')
    
    # Create RouteLogs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS RouteLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_path TEXT NOT NULL,
            distance REAL NOT NULL,
            fuel_used REAL NOT NULL,
            fuel_cost REAL NOT NULL,
            driver_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            efficiency TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create BudgetConfig table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BudgetConfig (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fuel_price REAL,
            mileage REAL,
            driver_hourly_rate REAL,
            monthly_budget_limit REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default budget config if empty
    cursor.execute('SELECT COUNT(*) FROM BudgetConfig')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO BudgetConfig (fuel_price, mileage, driver_hourly_rate, monthly_budget_limit)
            VALUES (?, ?, ?, ?)
        ''', (350.0, 12.0, 500.0, 120000.0))


    # Insert some initial mock data if empty
    cursor.execute('SELECT COUNT(*) FROM Bins')
    if cursor.fetchone()[0] == 0:
        mock_bins = [
            ('Galle Face Green', 6.9248, 79.8436, 10),
            ('Viharamahadevi Park', 6.9142, 79.8612, 85),
            ('Independence Square', 6.9044, 79.8675, 45),
            ('Lotus Tower', 6.9274, 79.8586, 95),
            ('Pettah Market', 6.9388, 79.8510, 20),
        ]
        cursor.executemany('''
            INSERT INTO Bins (location_name, latitude, longitude, fill_level)
            VALUES (?, ?, ?, ?)
        ''', mock_bins)
        
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
