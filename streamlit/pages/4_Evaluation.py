"""
pages/4_Evaluation.py
"""
import os
import sys
import json
import pandas as pd
import streamlit as st
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.styling import inject_custom_css, eyebrow, metric_card

st.set_page_config(page_title='Evaluation - Kopdes Sentiment', page_icon='📐', layout='wide')
inject_custom_css()
eyebrow('Hasil')
st.markdown('# Model Evaluation')

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')

comparison_path = os.path.join(REPORTS_DIR, 'final_model_comparison.csv')
if os.path.exists(comparison_path):
    df = pd.read_csv(comparison_path)
    st.subheader('Perbandingan Performa Model')
    st.dataframe(df, width='stretch')

    best_row = df.sort_values('Macro F1', ascending=False).iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card('Model Terbaik', str(best_row['Model']), primary=True)
    with col2: metric_card('Accuracy', f"{best_row['Accuracy']:.1%}")
    with col3: metric_card('Macro Precision', f"{best_row['Macro Precision']:.1%}")
    with col4: metric_card('Macro F1', f"{best_row['Macro F1']:.3f}")

    st.bar_chart(df.set_index('Model')[['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1']])
else:
    st.warning(
        'File `final_model_comparison.csv` belum ada. Jalankan dulu notebook '
        '`09_modeling.ipynb` dan `10_model_evaluation.ipynb`.'
    )

st.divider()
st.subheader('Confusion Matrix')
cm_path = os.path.join(REPORTS_DIR, 'figures', '17_confusion_matrix_all_models.png')
if os.path.exists(cm_path):
    st.image(Image.open(cm_path), width='stretch')
else:
    st.info('Confusion matrix belum tersedia.')

st.divider()
st.subheader('Ringkasan Error Analysis')
eval_summary_path = os.path.join(REPORTS_DIR, 'evaluation_summary.json')
if os.path.exists(eval_summary_path):
    with open(eval_summary_path) as f:
        ev = json.load(f)
    st.write(f"Model terbaik: **{ev.get('best_model')}**")
    st.write(f"Jumlah kesalahan prediksi: **{ev.get('n_errors_best_model'):,}** "
             f"({ev.get('error_rate_best_model', 0):.2%} dari test set)")
else:
    st.info('Ringkasan evaluasi belum tersedia.')
