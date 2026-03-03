import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "analytics.db"

def init_db():
    """Inicializa o banco de dados se ele não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            filename TEXT,
            bank TEXT,
            status TEXT,
            row_count INTEGER,
            error_message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(filename, bank, status, row_count=0, error_message=None):
    """Registra um evento de processamento no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO file_logs (timestamp, filename, bank, status, row_count, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, bank, status, row_count, error_message))
    conn.commit()
    conn.close()

def get_analytics_data():
    """Retorna todos os logs como um DataFrame do Pandas."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM file_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df
