"""
utils/model.py
Load TF-IDF vectorizer & model klasifikasi terbaik (hasil Tahap 8-10) untuk
dipakai di halaman Prediction.
"""
import os
import joblib
import streamlit as st

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')


@st.cache_resource
def load_vectorizer():
    path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    if not os.path.exists(path):
        return None
    return joblib.load(path)


@st.cache_resource
def load_best_model():
    path = os.path.join(MODELS_DIR, 'best_model.pkl')
    if not os.path.exists(path):
        return None
    return joblib.load(path)


@st.cache_resource
def load_best_model_name():
    path = os.path.join(MODELS_DIR, 'best_model_name.txt')
    if not os.path.exists(path):
        return 'Unknown'
    with open(path) as f:
        return f.read().strip()


@st.cache_resource
def load_all_models():
    """Load ketiga model (LR, SVM, NB) sekaligus untuk perbandingan."""
    names = {
        'Logistic Regression': 'model_logistic_regression.pkl',
        'SVM (LinearSVC)': 'model_svm.pkl',
        'Naive Bayes': 'model_naive_bayes.pkl',
    }
    models = {}
    for name, fname in names.items():
        path = os.path.join(MODELS_DIR, fname)
        if os.path.exists(path):
            models[name] = joblib.load(path)
    return models


def predict_all_models(text_final: str):
    """Prediksi sentimen dengan ketiga model sekaligus, untuk perbandingan."""
    vectorizer = load_vectorizer()
    models = load_all_models()
    if vectorizer is None or not models:
        return {}

    X = vectorizer.transform([text_final])
    results = {}
    for name, model in models.items():
        label = model.predict(X)[0]
        conf = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            conf = float(max(proba))
        elif hasattr(model, 'decision_function'):
            import numpy as np
            scores = model.decision_function(X)[0]
            exp_scores = np.exp(scores - np.max(scores))
            proba = exp_scores / exp_scores.sum()
            classes = list(model.classes_)
            conf = float(proba[classes.index(label)])
        results[name] = {'label': label, 'confidence': conf}
    return results


def top_influential_words(text_final: str, label: str, top_n: int = 8):
    """
    Kata-kata dalam input yang paling berpengaruh terhadap prediksi label,
    berdasarkan bobot koefisien Logistic Regression x skor TF-IDF kata tsb.
    Hanya berfungsi untuk model berbasis koefisien linear (LR/SVM).
    """
    vectorizer = load_vectorizer()
    model = load_best_model()
    if vectorizer is None or model is None or not hasattr(model, 'coef_'):
        return []

    X = vectorizer.transform([text_final])
    feature_names = vectorizer.get_feature_names_out()
    classes = list(model.classes_)
    if label not in classes:
        return []
    class_idx = classes.index(label)

    coef_row = model.coef_[class_idx] if model.coef_.shape[0] > 1 else model.coef_[0]
    nonzero = X.nonzero()[1]
    contributions = [(feature_names[i], X[0, i] * coef_row[i]) for i in nonzero]
    contributions.sort(key=lambda x: x[1], reverse=True)
    return contributions[:top_n]


def predict_sentiment(text_final: str):
    """
    Prediksi sentimen dari teks yang SUDAH dipreprocess (text_final).
    Mengembalikan (label, confidence). confidence None jika model tidak
    mendukung predict_proba/decision_function (mis. LinearSVC default).
    """
    vectorizer = load_vectorizer()
    model = load_best_model()

    if vectorizer is None or model is None:
        return None, None

    X = vectorizer.transform([text_final])
    label = model.predict(X)[0]

    confidence = None
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X)[0]
        confidence = float(max(proba))
    elif hasattr(model, 'decision_function'):
        import numpy as np
        scores = model.decision_function(X)[0]
        # softmax sederhana atas decision scores utk perkiraan confidence relatif
        exp_scores = np.exp(scores - np.max(scores))
        proba = exp_scores / exp_scores.sum()
        classes = list(model.classes_)
        confidence = float(proba[classes.index(label)])

    return label, confidence
