"""
pages/2_EDA.py
"""
import os
import sys
import streamlit as st
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.styling import inject_custom_css, eyebrow

st.set_page_config(page_title='EDA - Kopdes Sentiment', page_icon='📈', layout='wide')
inject_custom_css()
eyebrow('Eksplorasi')
st.markdown('# Exploratory Data Analysis')

FIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'figures')

st.markdown("Visualisasi berikut dihasilkan dari notebook `03_eda_awal.ipynb` dan "
            "`07_eda_setelah_labeling.ipynb`.")

section = st.radio('Pilih bagian:', ['EDA Awal (Sebelum Labeling)', 'EDA Setelah Labeling'], horizontal=True)


def show_fig(filename, caption):
    path = os.path.join(FIG_DIR, filename)
    if os.path.exists(path):
        st.image(Image.open(path), caption=caption, width='stretch')
    else:
        st.info(f'Figure belum tersedia: {filename} (jalankan notebook terkait terlebih dahulu)')


if section == 'EDA Awal (Sebelum Labeling)':
    col1, col2 = st.columns(2)
    with col1:
        show_fig('01_missing_values.png', 'Missing Value per Kolom')
        show_fig('03_top_videos.png', 'Top 15 Video')
        show_fig('05_activity_pattern.png', 'Pola Aktivitas Komentar')
    with col2:
        show_fig('02_duplicate_proportion.png', 'Proporsi Data Unik vs Duplikat')
        show_fig('04_daily_volume.png', 'Volume Komentar Harian')
        show_fig('06_comment_length.png', 'Distribusi Panjang Komentar')
    show_fig('07_level_structure.png', 'Struktur Level Komentar')

else:
    col1, col2 = st.columns(2)
    with col1:
        show_fig('08_sentiment_distribution.png', 'Distribusi Sentimen')
        show_fig('10_wordcloud_positive.png', 'WordCloud - Positive')
        show_fig('12_wordcloud_neutral.png', 'WordCloud - Neutral')
        show_fig('15_sentiment_by_video.png', 'Sentimen per Video')
    with col2:
        show_fig('09_confidence_by_class.png', 'Confidence Score per Kelas')
        show_fig('11_wordcloud_negative.png', 'WordCloud - Negative')
        show_fig('13_top_words_per_class.png', 'Top Words per Kelas')
        show_fig('16_sentiment_trend.png', 'Tren Sentimen Harian')
    show_fig('14_bigram_trigram.png', 'Bigram & Trigram per Kelas')

    st.info(
        'Bagian ini butuh output Tahap 6 (IndoBERT labeling di Colab) dan Tahap 7 '
        '(notebook EDA setelah labeling) untuk tampil. Jika belum ada figure, jalankan '
        'kedua notebook tersebut terlebih dahulu.'
    )
