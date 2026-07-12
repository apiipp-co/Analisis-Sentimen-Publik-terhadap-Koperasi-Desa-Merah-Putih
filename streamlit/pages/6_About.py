"""
pages/6_About.py
"""
import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.styling import inject_custom_css, eyebrow

st.set_page_config(page_title='About - Kopdes Sentiment', page_icon='ℹ️', layout='wide')
inject_custom_css()
eyebrow('Tentang')
st.markdown('# Tentang Proyek Ini')

st.markdown("""
## Final Project: Sentiment Analysis
### Sentimen terhadap Koperasi Desa Merah Putih (Kopdes)

Proyek ini membangun pipeline **end-to-end sentiment analysis** terhadap opini publik
Indonesia mengenai Koperasi Desa Merah Putih (Kopdes), menggunakan data komentar TikTok riil
(220.051 komentar dari 27 video).

### Tech Stack
| Komponen | Teknologi |
|---|---|
| Data Processing | Google Colab, Python, Pandas |
| NLP | Sastrawi (stemming Bahasa Indonesia), IndoBERT (labeling) |
| Feature Engineering | TF-IDF (scikit-learn) |
| Modeling | Logistic Regression, SVM, Naive Bayes |
| Database | Supabase PostgreSQL |
| Database Development | DBeaver |
| Dashboard | Metabase |
| Deployment | Streamlit |
| Version Control | GitHub |

### Alur Pipeline (14 Tahap)
1. Data Collection
2. Data Quality Audit
3. EDA Awal
4. Data Cleaning
5. Text Preprocessing
6. Sentiment Labeling (IndoBERT)
7. EDA Setelah Labeling
8. Feature Engineering (TF-IDF)
9. Modeling
10. Model Evaluation
11. Database (Supabase + DBeaver)
12. Dashboard (Metabase)
13. Deployment (Streamlit) — **halaman yang sedang kamu lihat ini**
14. Dokumentasi GitHub

### Sumber Data
Komentar publik TikTok dari 27 video terkait topik Koperasi Desa Merah Putih, dikumpulkan
periode Juli 2025 - Mei 2026.

### Repository
Kode lengkap tersedia di GitHub — lihat `README.md` pada repository untuk struktur folder,
cara menjalankan tiap tahap, dan dokumentasi teknis lengkap.
""")
