import sqlite3
import pandas as pd
from datetime import datetime
import os
import streamlit as st

DB_PATH = "analytics.db"

def get_supabase_client():
    from supabase import create_client, Client
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def init_db():
    """Inicializa o banco de dados se ele não existir (apenas para fallback local)."""
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
    """Registra um evento de processamento no Supabase ou banco local."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    supabase = get_supabase_client()
    if supabase:
        try:
            data = {
                "timestamp": timestamp,
                "filename": filename,
                "bank": bank,
                "status": status,
                "row_count": row_count,
                "error_message": error_message
            }
            supabase.table("file_logs").insert(data).execute()
            return
        except Exception as e:
            print(f"Erro ao salvar no Supabase: {e}")
            # Fallback for local
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO file_logs (timestamp, filename, bank, status, row_count, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, filename, bank, status, row_count, error_message))
    conn.commit()
    conn.close()

def get_analytics_data():
    """Retorna todos os logs como um DataFrame do Pandas, do Supabase ou banco local."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("file_logs").select("*").order("timestamp", desc=True).execute()
            data = response.data
            if data:
                return pd.DataFrame(data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao ler do Supabase: {e}")
            # Fallback for local
            
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM file_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

