"""
pages/5_Dashboard.py
Ringkasan dashboard terintegrasi langsung dari Supabase (melengkapi Metabase Tahap 12,
untuk pengguna yang mengakses lewat aplikasi Streamlit tanpa perlu buka Metabase terpisah).
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.db import test_connection, run_query
from utils.styling import inject_custom_css, eyebrow, metric_card

st.set_page_config(page_title='Dashboard - Kopdes Sentiment', page_icon='📋', layout='wide')
inject_custom_css()
eyebrow('Ringkasan')
st.markdown('# Dashboard')

METABASE_URL = os.getenv('METABASE_PUBLIC_DASHBOARD_URL', '')
if METABASE_URL:
    st.markdown(f'[Buka Dashboard Metabase Lengkap]({METABASE_URL})')

if not test_connection():
    st.error('Belum terkoneksi ke database Supabase. Cek file `.env`.')
    st.stop()

try:
    total = run_query('SELECT COUNT(*) AS total FROM labeled_comments;')['total'].iloc[0]
    dist = run_query("""
        SELECT sentiment_label, COUNT(*) AS jumlah
        FROM labeled_comments GROUP BY sentiment_label ORDER BY jumlah DESC;
    """)

    col1, col2 = st.columns([1, 2])
    with col1:
        metric_card('Total Komentar Berlabel', f'{total:,}', primary=True)

    if not dist.empty:
        fig = px.pie(dist, names='sentiment_label', values='jumlah', title='Distribusi Sentimen',
                     color='sentiment_label',
                     color_discrete_map={'positive': '#55A868', 'neutral': '#4C72B0', 'negative': '#C44E52'})
        col2.plotly_chart(fig, width='stretch')

    st.divider()
    st.subheader('Perbandingan Model')
    model_perf = run_query('SELECT * FROM v_model_performance;')
    if not model_perf.empty:
        st.dataframe(model_perf, width='stretch')
        fig2 = px.bar(model_perf, x='model_name', y=['accuracy', 'macro_precision', 'macro_recall', 'macro_f1'],
                      barmode='group', title='Metrik per Model')
        st.plotly_chart(fig2, width='stretch')

    st.divider()
    st.subheader('Tren Sentimen Harian')
    trend = run_query('SELECT * FROM v_sentiment_daily_trend;')
    if not trend.empty:
        fig3 = px.line(trend, x='comment_date', y='n_comments', color='sentiment_label',
                        title='Tren Sentimen dari Waktu ke Waktu',
                        color_discrete_map={'positive': '#55A868', 'neutral': '#4C72B0', 'negative': '#C44E52'})
        st.plotly_chart(fig3, width='stretch')

    st.divider()
    st.subheader('Log Prediksi Terbaru (dari Halaman Prediction)')
    preds = run_query('SELECT input_text, predicted_label, confidence, model_used, predicted_at '
                       'FROM prediction_history ORDER BY predicted_at DESC LIMIT 20;')
    st.dataframe(preds, width='stretch')

except Exception as e:
    st.warning(f'Sebagian data dashboard belum tersedia (tabel mungkin masih kosong): {e}')
