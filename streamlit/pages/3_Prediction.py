"""
pages/3_Prediction.py
Fitur inti wajib brief: terima input kalimat, tampilkan prediksi sentimen +
confidence score, simpan setiap hasil prediksi ke Supabase.

Fitur tambahan: perbandingan 3 model, explainability, contoh cepat, riwayat.
"""
import os
import sys
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.preprocessing import preprocess_text
from utils.model import (
    load_vectorizer, load_best_model, load_best_model_name,
    predict_sentiment, predict_all_models, top_influential_words,
)
from utils.db import save_prediction, test_connection, run_query
from utils.styling import inject_custom_css, eyebrow, section_divider, sentiment_badge

st.set_page_config(page_title='Prediction - Kopdes Sentiment', page_icon='🔮', layout='centered')
inject_custom_css()

eyebrow('Coba Sendiri')
st.markdown('# Prediksi Sentimen')
st.markdown(
    '<p style="color:var(--color-ink-soft);">Tulis komentar berbahasa Indonesia, dan model akan '
    'menebak nada bicaranya — lengkap dengan alasannya.</p>',
    unsafe_allow_html=True
)

vectorizer = load_vectorizer()
model = load_best_model()
model_name = load_best_model_name()

if vectorizer is None or model is None:
    st.error(
        'Model belum tersedia. Pastikan `models/tfidf_vectorizer.pkl` dan `models/best_model.pkl` '
        'sudah dihasilkan dari notebook 08 (Feature Engineering) dan 09/10 (Modeling/Evaluation).'
    )
    st.stop()

st.markdown(
    f'<span style="font-family:var(--font-mono);font-size:12px;background:var(--color-indigo-tint);'
    f'color:var(--color-indigo);padding:4px 10px;border-radius:6px;">MODEL AKTIF · {model_name}</span>',
    unsafe_allow_html=True
)

st.write('')
st.markdown('**Coba contoh kalimat:**')
examples = [
    'koperasi ini sangat membantu masyarakat desa, terima kasih pemerintah',
    'saya tidak tahu apakah program ini akan berhasil atau tidak',
    'program ini gagal total dan hanya buang-buang anggaran negara',
]
ex_cols = st.columns(3)
for i, ex in enumerate(examples):
    if ex_cols[i].button(f'Contoh {i+1}', width='stretch', key=f'ex_{i}'):
        st.session_state['prediction_input'] = ex

user_input = st.text_area(
    'Tulis komentar/opini kamu di sini:',
    placeholder='Contoh: koperasi ini sangat membantu masyarakat desa, terima kasih pemerintah',
    height=120,
    key='prediction_input',
)

col1, col2 = st.columns([1, 3])
predict_clicked = col1.button('🔍 Prediksi Sentimen', type='primary', width='stretch')

if predict_clicked:
    if not user_input.strip():
        st.warning('Tulis dulu kalimatnya sebelum prediksi.')
    else:
        with st.spinner('Memproses teks & memprediksi...'):
            text_final = preprocess_text(user_input)

            if not text_final.strip():
                st.warning(
                    'Setelah preprocessing, teks menjadi kosong (kemungkinan hanya berisi '
                    'stopword/simbol). Coba tulis kalimat yang lebih deskriptif.'
                )
            else:
                label, confidence = predict_sentiment(text_final)

                section_divider('Hasil')
                st.markdown(sentiment_badge(label), unsafe_allow_html=True)
                st.write('')

                if confidence is not None:
                    st.markdown(
                        f'<div class="kop-card"><div class="kop-card-label">Confidence Score</div>'
                        f'<div class="kop-card-value primary">{confidence:.1%}</div></div>',
                        unsafe_allow_html=True
                    )
                    st.write('')
                    st.progress(confidence)
                else:
                    st.caption('(Model ini tidak menyediakan confidence score / probabilitas)')

                # --- Kata paling berpengaruh (explainability) ---
                influential = top_influential_words(text_final, label, top_n=8)
                if influential:
                    st.write('')
                    st.markdown('**Kata paling berpengaruh terhadap prediksi ini:**')
                    word_cols = st.columns(len(influential))
                    for wc, (word, score) in zip(word_cols, influential):
                        bg = 'var(--color-positive-tint)' if score > 0 else 'var(--color-negative-tint)'
                        fg = 'var(--color-positive)' if score > 0 else 'var(--color-negative)'
                        wc.markdown(
                            f"<div style='text-align:center;padding:8px 4px;border-radius:8px;"
                            f"background:{bg};color:{fg};font-family:var(--font-body);'>"
                            f"<b style='font-size:13px;'>{word}</b><br>"
                            f"<span style='font-size:11px;font-family:var(--font-mono);'>{score:+.3f}</span></div>",
                            unsafe_allow_html=True
                        )
                    st.caption('Semakin kuat warnanya, semakin kata itu mendorong ke label yang diprediksi.')

                # --- Perbandingan 3 model ---
                with st.expander('📊 Bandingkan prediksi dari 3 model sekaligus'):
                    all_results = predict_all_models(text_final)
                    if all_results:
                        for mname, res in all_results.items():
                            conf_str = f"{res['confidence']:.1%}" if res['confidence'] is not None else '-'
                            st.markdown(
                                f"**{mname}** — {sentiment_badge(res['label'])} "
                                f"<span style='color:var(--color-ink-soft);font-size:13px;'>(confidence: {conf_str})</span>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption('Model lain tidak tersedia untuk perbandingan.')

                with st.expander('Detail teknis (teks setelah preprocessing)'):
                    st.code(text_final)

                # Simpan ke Supabase (wajib brief)
                if test_connection():
                    try:
                        save_prediction(user_input, label, confidence, model_name)
                        st.success('Hasil prediksi tersimpan ke database (prediction_history).')
                    except Exception as e:
                        st.warning(f'Prediksi berhasil, tapi gagal menyimpan ke database: {e}')
                else:
                    st.warning(
                        'Prediksi berhasil, tapi tidak tersimpan ke database (belum terkoneksi ke '
                        'Supabase — cek file `.env`).'
                    )

# --- Riwayat prediksi terakhir ---
section_divider('Riwayat Prediksi Terakhir')

@st.cache_data(ttl=15)
def get_recent_history():
    return run_query(
        "SELECT input_text, predicted_label, confidence, predicted_at "
        "FROM prediction_history ORDER BY predicted_at DESC LIMIT 10;"
    )

if test_connection():
    try:
        history = get_recent_history()
        if not history.empty:
            st.dataframe(history, width='stretch', hide_index=True)
        else:
            st.caption('Belum ada riwayat prediksi.')
    except Exception:
        st.caption('Riwayat belum tersedia (tabel prediction_history mungkin masih kosong).')
else:
    st.caption('Tidak terkoneksi ke database — riwayat tidak dapat ditampilkan.')

st.divider()
st.caption(
    'Catatan: model utama adalah model Machine Learning klasik (TF-IDF + '
    f'{model_name}) yang dilatih dari label hasil IndoBERT di Tahap 6 — '
    'bukan menjalankan IndoBERT secara langsung, agar prediksi real-time tetap ringan & cepat.'
)
