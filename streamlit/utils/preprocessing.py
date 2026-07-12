"""
utils/preprocessing.py
Replikasi persis pipeline Text Preprocessing dari Tahap 5, dipakai untuk memproses
input pengguna secara real-time di halaman Prediction agar konsisten dengan teks
yang dipakai saat training model (text_final).
"""
import re
import json
import os
import streamlit as st
import emoji as emoji_lib
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

STOPWORDS_COLLOQUIAL = {
    'yg', 'ga', 'gak', 'gk', 'nggak', 'ngga', 'nya', 'dgn', 'dg', 'aja', 'sih', 'deh', 'kok',
    'dong', 'donk', 'banget', 'bgt', 'emang', 'emg', 'udah', 'udh', 'dah', 'nih', 'tuh', 'kan',
    'ya', 'yah', 'loh', 'lho', 'lah', 'kah', 'pun', 'juga', 'jg', 'sm', 'sama', 'trus', 'terus',
    'krn', 'karna', 'utk', 'sdh', 'blm', 'belom', 'gitu', 'gt', 'gini', 'gni', 'klo', 'kalo',
    'gmn', 'gimana', 'org', 'orang', 'sy', 'saya', 'kalian', 'kmu', 'kamu', 'lu', 'lo', 'gue',
    'gw', 'ni', 'si', 'nder', 'wkwk', 'wkwkwk', 'haha', 'hehe',
}


@st.cache_resource
def load_nlp_tools():
    """Load Sastrawi stemmer, stopwords, dan cache stemming hasil training (jika ada)."""
    stemmer = StemmerFactory().create_stemmer()
    stopwords_formal = set(StopWordRemoverFactory().get_stop_words())
    all_stopwords = stopwords_formal | STOPWORDS_COLLOQUIAL

    cache_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'stem_cache_checkpoint.json')
    stem_cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            stem_cache = json.load(f)

    return stemmer, all_stopwords, stem_cache


def preprocess_text(raw_text: str) -> str:
    """
    Pipeline identik dengan Tahap 5:
    case folding -> cleaning (URL/mention/hashtag/sticker) -> remove emoji ->
    remove number -> remove punctuation -> normalize elongation -> tokenize ->
    stopword removal -> stemming (pakai cache training, fallback live stem).
    """
    stemmer, all_stopwords, stem_cache = load_nlp_tools()

    text = raw_text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#\w+', ' ', text)
    text = re.sub(r'\[sticker\]', ' ', text, flags=re.IGNORECASE)
    text = emoji_lib.replace_emoji(text, replace=' ')
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'_', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)  # normalisasi elongasi huruf

    tokens = text.split()
    tokens = [t for t in tokens if t not in all_stopwords and len(t) > 1]
    tokens_stemmed = [stem_cache.get(t) or stemmer.stem(t) for t in tokens]
    tokens_stemmed = [t for t in tokens_stemmed if t.strip() != '']

    return ' '.join(tokens_stemmed)
