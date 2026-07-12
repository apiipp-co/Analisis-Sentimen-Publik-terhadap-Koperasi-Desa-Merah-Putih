"""
utils/db.py
Koneksi ke Supabase PostgreSQL. Dipakai di halaman Prediction (menyimpan hasil
prediksi ke tabel prediction_history) dan halaman Dashboard (query ringkasan).
"""
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_engine():
    """Buat SQLAlchemy engine ke Supabase PostgreSQL (cached, 1x per sesi app)."""
    def _get_config(key: str, default: str) -> str:
        # Prioritas: environment variable (.env) -> Streamlit secrets (jika ada) -> default
        value = os.getenv(key)
        if value:
            return value
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass  # st.secrets bisa melempar error jika secrets.toml tidak ada - abaikan, pakai default
        return default

    host = _get_config('SUPABASE_DB_HOST', 'localhost')
    port = _get_config('SUPABASE_DB_PORT', '5432')
    dbname = _get_config('SUPABASE_DB_NAME', 'postgres')
    user = _get_config('SUPABASE_DB_USER', 'postgres')
    password = _get_config('SUPABASE_DB_PASSWORD', '')

    url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'
    return create_engine(url, pool_pre_ping=True)


def save_prediction(input_text: str, predicted_label: str, confidence: float, model_used: str):
    """Simpan hasil prediksi ke tabel prediction_history (brief mewajibkan ini)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO prediction_history (input_text, predicted_label, confidence, model_used, source)
                VALUES (:input_text, :predicted_label, :confidence, :model_used, 'streamlit_app')
            """),
            {
                'input_text': input_text,
                'predicted_label': predicted_label,
                'confidence': float(confidence) if confidence is not None else None,
                'model_used': model_used,
            }
        )


def run_query(sql: str) -> pd.DataFrame:
    """Jalankan query SELECT dan kembalikan sebagai DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text('SELECT 1;'))
        return True
    except Exception:
        return False
