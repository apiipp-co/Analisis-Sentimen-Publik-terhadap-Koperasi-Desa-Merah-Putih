"""
pages/1_Dataset.py
"""
import os
import sys
import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.styling import inject_custom_css, eyebrow

st.set_page_config(page_title='Dataset - Kopdes Sentiment', page_icon='🗂️', layout='wide')
inject_custom_css()
eyebrow('Eksplorasi')
st.markdown('# Dataset')
st.markdown(
    '<p style="color:var(--color-ink-soft);">Seluruh data berasal dari komentar publik TikTok '
    'asli (27 video, topik Koperasi Desa Merah Putih) — bukan data simulasi. '
    'Tiap tab di bawah menunjukkan tahap pemrosesan yang berbeda.</p>',
    unsafe_allow_html=True
)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

tab1, tab2, tab3 = st.tabs(['📥 Raw Data', '🧹 Clean Data', '🏷️ Labeled Data'])

with tab1:
    st.markdown("""
        <div class="kop-card" style="margin-bottom:16px;">
        <b>Data mentah, apa adanya.</b> Ini hasil scraping langsung dari TikTok, sebelum ada
        pemrosesan apa pun — termasuk duplikat dan komentar yang belum bersih. Dipakai sebagai
        titik awal (Tahap 1: Data Collection) dan arsip yang bisa ditelusuri ulang kapan saja.
        </div>
    """, unsafe_allow_html=True)
    path = os.path.join(DATA_DIR, 'raw', 'raw_comments_kopdes.parquet')
    if os.path.exists(path):
        df = pd.read_parquet(path)
        st.write(f'Total baris: **{len(df):,}** | Video unik: **{df["video_id"].nunique()}**')
        st.dataframe(df.head(100), width='stretch')
        st.download_button('Download sample (100 baris) sebagai CSV', df.head(100).to_csv(index=False),
                            file_name='raw_comments_sample.csv')
    else:
        st.warning('File raw data belum ditemukan.')

with tab2:
    st.markdown("""
        <div class="kop-card" style="margin-bottom:16px;">
        <b>Data setelah dibersihkan (Tahap 4).</b> Duplikat artefak scraper (42% data mentah)
        dan komentar tanpa makna tekstual (stiker, emoji-only, dsb) sudah dihapus — dengan alasan
        terdokumentasi untuk tiap baris yang dibuang. Teks komentar sendiri belum diubah.
        </div>
    """, unsafe_allow_html=True)
    path = os.path.join(DATA_DIR, 'interim', 'clean_comments_kopdes.parquet')
    if os.path.exists(path):
        df = pd.read_parquet(path)
        st.write(f'Total baris: **{len(df):,}**')
        st.dataframe(df.head(100), width='stretch')
    else:
        st.warning('File clean data belum ditemukan.')

with tab3:
    st.markdown("""
        <div class="kop-card" style="margin-bottom:16px;">
        <b>Data dengan label sentimen (Tahap 6).</b> Setiap komentar diberi label
        Positive/Neutral/Negative secara otomatis oleh model <b>IndoBERT</b>
        (<code>mdhugol/indonesia-bert-sentiment-classification</code>), lengkap dengan skor
        keyakinan model. Data inilah yang dipakai melatih model prediksi di halaman Prediction.
        </div>
    """, unsafe_allow_html=True)
    path = os.path.join(DATA_DIR, 'processed', 'labeled_comments_kopdes.parquet')
    if os.path.exists(path):
        df = pd.read_parquet(path)
        st.write(f'Total baris: **{len(df):,}**')
        st.dataframe(df.head(100), width='stretch')
        st.bar_chart(df['sentiment_label'].value_counts())
    else:
        st.warning(
            'File labeled data belum ditemukan. Jalankan dulu '
            '`06_sentiment_labeling_indobert.ipynb` di Google Colab.'
        )
