# Sentiment Analysis: Koperasi Desa Merah Putih (Kopdes)

Analisis sentimen publik Indonesia terhadap program **Koperasi Desa Merah Putih (Kopdes)**
berdasarkan 220.051 komentar TikTok riil dari 27 video, menggunakan pipeline end-to-end mulai
dari data collection hingga deployment production-ready.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Status](https://img.shields.io/badge/Status-Completed-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Daftar Isi

- [Ringkasan Project](#-ringkasan-project)
- [Hasil Utama](#-hasil-utama)
- [Tech Stack](#-tech-stack)
- [Arsitektur Pipeline](#-arsitektur-pipeline)
- [Struktur Repository](#-struktur-repository)
- [Cara Menjalankan](#-cara-menjalankan)
- [Dataset](#-dataset)
- [Metodologi](#-metodologi)
- [Model & Evaluasi](#-model--evaluasi)
- [Database Schema](#-database-schema)
- [Dashboard & Deployment](#-dashboard--deployment)
- [Keterbatasan & Catatan](#-keterbatasan--catatan)

---

## 🎯 Ringkasan Project

Project ini membangun sistem analisis sentimen end-to-end untuk memahami opini publik Indonesia
terhadap kebijakan **Koperasi Desa Merah Putih** — program koperasi berbasis desa yang menjadi
perbincangan hangat di media sosial pada 2025-2026. Data dikumpulkan dari komentar TikTok riil
(bukan sample/dummy), diproses melalui pipeline lengkap: cleaning, preprocessing NLP Bahasa
Indonesia, pelabelan otomatis menggunakan IndoBERT, feature engineering, machine learning
modeling, hingga deployment aplikasi web interaktif.

## 🏆 Hasil Utama

| Metrik | Nilai |
|---|---|
| Total komentar mentah dikumpulkan | 220.051 (27 video TikTok) |
| Total komentar setelah cleaning | 120.707 |
| Total komentar berlabel sentimen | 119.565 |
| Distribusi sentimen | Negative 58,0% · Neutral 23,3% · Positive 18,7% |
| Model terbaik | Logistic Regression (TF-IDF) |
| Accuracy | 71,98% |
| Macro F1-Score | 0,693 |
| Rata-rata confidence labeling IndoBERT | 0,89 |

> Distribusi sentimen yang condong negatif konsisten dengan sifat topik kebijakan pemerintah
> yang kontroversial di media sosial — bukan indikasi bias pelabelan (divalidasi lewat WordCloud
> & sanity check kualitatif, lihat notebook `07_eda_setelah_labeling.ipynb`).

## 🛠️ Tech Stack

| Kategori | Teknologi |
|---|---|
| Notebook & Compute | Google Colab (GPU T4) |
| Bahasa | Python 3.12 |
| Data Processing | Pandas, NumPy, PyArrow |
| NLP | Sastrawi (stemming Bahasa Indonesia), Emoji, IndoBERT (`mdhugol/indonesia-bert-sentiment-classification`) |
| Feature Engineering | scikit-learn (TF-IDF) |
| Machine Learning | scikit-learn (Logistic Regression, SVM, Naive Bayes) |
| Database | Supabase (PostgreSQL) |
| DB Development | DBeaver |
| Dashboard BI | Metabase |
| Deployment | Streamlit |
| Visualisasi | Matplotlib, Seaborn, WordCloud, Plotly |

## 🔄 Arsitektur Pipeline

```
1. Data Collection          ── Scraping komentar TikTok (220.051 baris, 27 video)
2. Data Quality Audit        ── Audit missing value, duplikasi, konsistensi, spam
3. EDA Awal                  ── Visualisasi eksplorasi sebelum cleaning
4. Data Cleaning             ── Dedup, drop non-tekstual (→ 120.707 baris)
5. Text Preprocessing        ── Case fold, clean, tokenize, stopword, stemming
6. Sentiment Labeling        ── IndoBERT (zero-shot) → 119.565 baris berlabel
7. EDA Setelah Labeling      ── Distribusi, WordCloud, Top Words, Bigram/Trigram
8. Feature Engineering       ── TF-IDF Vectorizer (train-only fit)
9. Modeling                  ── Logistic Regression, SVM, Naive Bayes
10. Model Evaluation         ── Confusion matrix, error analysis, model selection
11. Database                 ── Supabase PostgreSQL (7 tabel + index + view)
12. Dashboard                ── Metabase (9 card visualisasi)
13. Deployment                ── Streamlit multipage app (real-time prediction)
14. Dokumentasi               ── README ini
```

## 📁 Struktur Repository

```
sentiment-kopdes/
├── notebooks/                      # Notebook Jupyter/Colab tiap tahap (01-11)
│   ├── 01_data_collection.ipynb
│   ├── 02_data_quality_audit.ipynb
│   ├── 03_eda_awal.ipynb
│   ├── 04_data_cleaning.ipynb
│   ├── 05_text_preprocessing.ipynb
│   ├── 06_sentiment_labeling_indobert.ipynb
│   ├── 07_eda_setelah_labeling.ipynb
│   ├── 08_feature_engineering.ipynb
│   ├── 09_modeling.ipynb
│   ├── 10_model_evaluation.ipynb
│   └── 11_database_supabase.ipynb
├── sql/
│   ├── schema.sql                  # DDL: 7 tabel, index, view
│   └── metabase_queries.sql        # 11 query siap-pakai untuk dashboard
├── streamlit/                      # Aplikasi deployment
│   ├── app.py                      # Halaman Home
│   ├── pages/                      # Dataset, EDA, Prediction, Evaluation, Dashboard, About
│   ├── utils/                      # Preprocessing, model loader, db connector
│   ├── requirements.txt
│   └── .streamlit/config.toml
├── models/                         # Model terlatih (.pkl)
│   ├── tfidf_vectorizer.pkl
│   ├── best_model.pkl
│   ├── model_logistic_regression.pkl
│   ├── model_svm.pkl
│   └── model_naive_bayes.pkl
├── data/
│   ├── raw/                        # Data mentah (immutable)
│   ├── interim/                    # Data hasil cleaning & preprocessing
│   └── processed/                  # Data siap modeling & hasil label
├── reports/
│   ├── figures/                    # 17 visualisasi (EDA, wordcloud, confusion matrix)
│   └── *_summary.json              # Ringkasan tiap tahap
├── scripts/
│   └── stem_pipeline.py            # Script stemming standalone (frequency-thresholded)
├── README.md
├── requirements.txt                 # Dependencies notebook/pipeline
├── .gitignore
└── LICENSE
```

## 🚀 Cara Menjalankan

### 1. Clone & Setup
```bash
git clone <repo-url>
cd sentiment-kopdes
pip install -r requirements.txt
```

### 2. Jalankan Pipeline (Notebook)
Jalankan notebook di `notebooks/` secara berurutan (01 → 11) di Google Colab (disarankan untuk
Tahap 6 yang butuh GPU) atau Jupyter lokal.

> **Catatan `notebooks/01_data_collection.ipynb`**: cell pertama membaca file sumber mentah
> `KDMP.xlsx` (~15MB, hasil scraping TikTok) yang **tidak disertakan** di repository ini karena
> ukurannya besar dan outputnya sudah tersimpan permanen di `data/raw/raw_comments_kopdes.parquet`.
> Notebook 02-11 tidak butuh file ini — semua sudah bisa langsung dijalankan dari data yang ada
> di folder `data/`.

Tahap 11 butuh kredensial Supabase — buat file
`.env` di root project:
```bash
SUPABASE_DB_HOST=your-project.pooler.supabase.com
SUPABASE_DB_PORT=6543
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.xxxxxxxxxxxx
SUPABASE_DB_PASSWORD=your-password
```
**PENTING:** jangan pernah hardcode kredensial database langsung di cell notebook — selalu
lewat `.env` (sudah masuk `.gitignore`, tidak akan ter-commit).

### 3. Jalankan Aplikasi Streamlit
```bash
cd streamlit
cp .env.example .env   # isi dengan kredensial Supabase
pip install -r requirements.txt
streamlit run app.py
```

### 4. Setup Dashboard Metabase
Lihat panduan lengkap di [`reports/tahap12_dashboard_metabase_setup.md`](reports/tahap12_dashboard_metabase_setup.md).

## 📊 Dataset

- **Sumber**: Komentar publik TikTok (termasuk reply berjenjang) dari 27 video terkait topik
  Koperasi Desa Merah Putih
- **Periode**: 13 Juli 2025 – 27 Mei 2026
- **Volume**: 220.051 baris mentah → 120.707 setelah cleaning → 119.565 berlabel sentimen
- **Kolom**: `video_id`, `comment_id`, `parent_comment_id`, `level`, `username`, `nickname`,
  `comment`, `create_time`

## 🔬 Metodologi

### Data Cleaning (Tahap 4)
Ditemukan 42% data merupakan duplikat artefak scraper (komentar top-level ter-ekspor dua kali
dengan `level` berbeda). Setelah dedup + drop komentar non-tekstual (sticker, emoji-only,
punctuation-only), data bersih: **120.707 baris** — seluruh keputusan penghapusan
terdokumentasi dengan bukti kuantitatif di `reports/cleaning_log.csv`.

### Text Preprocessing (Tahap 5)
Pipeline: case folding → remove URL/mention/hashtag/emoji/number/punctuation → normalisasi
elongasi huruf → tokenisasi → stopword removal (Sastrawi formal + kolokial medsos) → stemming
(Sastrawi, dioptimasi dengan *frequency-thresholding* + disk caching untuk korpus besar).

### Sentiment Labeling (Tahap 6)
Menggunakan model IndoBERT pre-trained `mdhugol/indonesia-bert-sentiment-classification`
(bukan lexicon-based) untuk memberi label Positive/Neutral/Negative pada teks yang **dibersihkan
ringan** (mempertahankan struktur kalimat natural, berbeda dari teks ter-stem di Tahap 5 yang
dipakai khusus untuk TF-IDF).

### Feature Engineering (Tahap 8)
TF-IDF (`max_features=10000`, `ngram_range=(1,2)`) di-*fit* hanya pada data train (80%) untuk
mencegah data leakage ke test set (20%).

## 🤖 Model & Evaluasi

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 |
|---|---|---|---|---|
| **Logistic Regression** ⭐ | 71,98% | 0,679 | 0,729 | **0,693** |
| SVM (LinearSVC) | 72,65% | 0,680 | 0,699 | 0,686 |
| Naive Bayes | 71,69% | 0,719 | 0,596 | 0,629 |

Model dipilih berdasarkan **Macro F1** (bukan hanya Accuracy) karena lebih adil terhadap
distribusi kelas yang tidak seimbang. Detail confusion matrix & error analysis ada di
`notebooks/10_model_evaluation.ipynb` dan `reports/figures/17_confusion_matrix_all_models.png`.

## 🗄️ Database Schema

7 tabel di Supabase PostgreSQL: `raw_comments`, `clean_comments`, `preprocessed_comments`,
`labeled_comments`, `model_results`, `prediction_history`, `dashboard_summary` — lengkap dengan
12 index dan 3 view (`v_sentiment_by_video`, `v_sentiment_daily_trend`, `v_model_performance`).
Skema lengkap: [`sql/schema.sql`](sql/schema.sql).

## 📈 Dashboard & Deployment

- **Metabase**: 9 card wajib (Total Data, Distribusi Sentimen, Top Words, Trend Sentimen,
  Perbandingan Model, Accuracy/Precision/Recall/F1) — query siap pakai di
  [`sql/metabase_queries.sql`](sql/metabase_queries.sql)
- **Streamlit**: aplikasi multipage (Home, Dataset, EDA, Prediction, Evaluation, Dashboard,
  About) — prediksi sentimen real-time tersimpan otomatis ke `prediction_history`

## ⚠️ Keterbatasan & Catatan

- Label sentimen dihasilkan oleh model IndoBERT pre-trained (bukan anotasi manual manusia),
  sehingga mewarisi keterbatasan model tersebut (mis. kesulitan menangkap sarkasme).
- Model klasik (Logistic Regression/SVM/Naive Bayes) dipakai untuk deployment real-time
  (bukan IndoBERT langsung) demi kecepatan respons aplikasi.
- Distribusi kelas tidak seimbang (58% negative) — metrik Macro F1 dipakai sebagai kriteria
  utama untuk mengurangi bias evaluasi ke kelas mayoritas.

---

**Dibuat sebagai Final Project Data Analyst/Data Science — BLKPP DIY**
