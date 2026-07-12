"""
app.py — Home
Final Project: Sentiment Analysis - Koperasi Desa Merah Putih (Kopdes)
"""
import os
import sys
import json
import streamlit as st

sys.path.append(os.path.dirname(__file__))
from utils.db import test_connection, run_query
from utils.styling import inject_custom_css, eyebrow, section_divider, metric_card, render_ticker

st.set_page_config(
    page_title='Kopdes Sentiment Analysis',
    page_icon='📊',
    layout='wide',
)
inject_custom_css()

# ---------- HERO ----------
eyebrow('Final Project · Sentiment Analysis')
st.markdown('# Denyut Opini Warga soal Koperasi Merah Putih')
st.markdown(
    '<p style="font-size:16px;color:var(--color-ink-soft);max-width:720px;">'
    'Membaca suara publik Indonesia dari 220.051 komentar TikTok riil — dari desa ke data, '
    'dari data ke keputusan.</p>',
    unsafe_allow_html=True
)

st.write('')
render_ticker()

# ---------- METRICS ----------
reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
collection_meta_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'collection_metadata.json')

n_raw = '—'
if os.path.exists(collection_meta_path):
    with open(collection_meta_path) as f:
        n_raw = f'{json.load(f)["n_rows_raw"]:,}'

evaluation_path = os.path.join(reports_dir, 'evaluation_summary.json')
best_model, best_acc, best_f1 = '—', '—', '—'
if os.path.exists(evaluation_path):
    with open(evaluation_path) as f:
        ev = json.load(f)
    best_model = ev.get('best_model', '—')
    metrics = ev.get('best_model_metrics', {})
    best_acc = f"{metrics.get('Accuracy', 0):.1%}" if metrics.get('Accuracy') else '—'
    best_f1 = f"{metrics.get('Macro F1', 0):.3f}" if metrics.get('Macro F1') else '—'

section_divider('Ringkasan Pipeline')
col1, col2, col3, col4 = st.columns(4)
with col1: metric_card('Total Komentar Mentah', n_raw)
with col2: metric_card('Model Terbaik', best_model, primary=True)
with col3: metric_card('Accuracy', best_acc)
with col4: metric_card('Macro F1-Score', best_f1)

# ---------- STATUS DB ----------
section_divider('Status Koneksi')
if test_connection():
    st.success('🟢 Terkoneksi ke Supabase PostgreSQL', icon=None)
    try:
        df_count = run_query('SELECT COUNT(*) AS total FROM labeled_comments;')
        st.markdown(
            f'<p style="color:var(--color-ink-soft);font-size:14px;">Total komentar berlabel di '
            f'database saat ini: <b style="color:var(--color-ink);">{df_count["total"].iloc[0]:,}</b></p>',
            unsafe_allow_html=True
        )
    except Exception:
        st.warning('Terkoneksi, tapi tabel `labeled_comments` belum terisi.')
else:
    st.error('🔴 Belum terkoneksi ke database — cek file `.env` (kredensial Supabase).')

# ---------- TENTANG DATA ----------
section_divider('Tentang Data Ini')

col_a, col_b = st.columns([3, 2])
with col_a:
    st.markdown("""
        <div class="kop-card" style="height:100%;">
            <p style="font-family:var(--font-display);font-weight:600;font-size:17px;margin-bottom:10px;">
                Dari mana data ini berasal?
            </p>
            <p style="font-size:14px;line-height:1.7;color:var(--color-ink-soft);">
                Seluruh data adalah <b style="color:var(--color-ink);">komentar publik asli dari TikTok</b>
                (termasuk balasan berjenjang), diambil dari <b style="color:var(--color-ink);">27 video</b>
                yang membahas program <b style="color:var(--color-ink);">Koperasi Desa Merah Putih (Kopdes)</b> —
                bukan data simulasi atau contoh buatan. Periode pengambilan:
                <b style="color:var(--color-ink);">13 Juli 2025 – 27 Mei 2026</b>.
            </p>
            <p style="font-size:14px;line-height:1.7;color:var(--color-ink-soft);">
                Data mentah kemudian melewati proses pembersihan (menghapus duplikat & komentar
                tanpa makna), diberi label sentimen otomatis memakai model <b style="color:var(--color-ink);">IndoBERT</b>,
                lalu dipakai melatih model Machine Learning yang menggerakkan halaman
                <b style="color:var(--color-ink);">Prediction</b> di aplikasi ini.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
        <div class="kop-card" style="height:100%;">
            <p style="font-family:var(--font-display);font-weight:600;font-size:17px;margin-bottom:10px;">
                Kolom yang tersedia
            </p>
            <table style="width:100%;font-size:13px;color:var(--color-ink-soft);border-collapse:collapse;">
                <tr><td style="padding:4px 0;"><code>video_id</code></td><td>ID video TikTok sumber</td></tr>
                <tr><td style="padding:4px 0;"><code>comment</code></td><td>Isi komentar asli</td></tr>
                <tr><td style="padding:4px 0;"><code>username</code></td><td>Akun pengirim</td></tr>
                <tr><td style="padding:4px 0;"><code>create_time</code></td><td>Waktu komentar diposting</td></tr>
                <tr><td style="padding:4px 0;"><code>level</code></td><td>Komentar utama / balasan</td></tr>
            </table>
            <p style="font-size:12px;color:var(--color-ink-soft);margin-top:10px;">
                Lihat detail lengkap di halaman <b>Dataset</b> →
            </p>
        </div>
    """, unsafe_allow_html=True)
section_divider('Jelajahi Aplikasi')
nav_items = [
    ('🗂️', 'Dataset', 'Preview data mentah, bersih, dan berlabel'),
    ('📈', 'EDA', 'Distribusi, WordCloud, dan pola komentar'),
    ('🔮', 'Prediction', 'Coba prediksi sentimen kalimatmu sendiri'),
    ('📐', 'Evaluation', 'Perbandingan performa & confusion matrix'),
    ('📋', 'Dashboard', 'Ringkasan metrik terintegrasi Supabase'),
    ('ℹ️', 'About', 'Tech stack dan metodologi proyek'),
]
cols = st.columns(3)
for i, (icon, name, desc) in enumerate(nav_items):
    with cols[i % 3]:
        st.markdown(f"""
            <div class="kop-card" style="margin-bottom:14px;">
                <div style="font-size:22px;margin-bottom:4px;">{icon}</div>
                <div style="font-family:var(--font-display);font-weight:600;font-size:16px;color:var(--color-ink);">{name}</div>
                <div style="font-size:13px;color:var(--color-ink-soft);margin-top:2px;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)

st.write('')
st.caption('Gunakan menu di sidebar kiri untuk berpindah halaman · Dibangun dengan Streamlit')
