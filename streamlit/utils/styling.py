"""
utils/styling.py
Sistem desain terpusat untuk aplikasi — dipanggil di awal tiap halaman.

Konsep desain: "Buku Kas Koperasi Digital" — palet merah-bata & krem kertas
terinspirasi dari nama program (Merah Putih) dan nuansa buku besar/ledger
koperasi desa, dipadukan tipografi serif berkarakter untuk judul dan sans
modern untuk isi. Elemen signature: "Denyut Opini" — pita berjalan berisi
cuplikan komentar asli yang mengalir terus, mewakili suara publik yang hidup.
"""
import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --color-bg: #FAF6EF;
        --color-surface: #FFFFFF;
        --color-ink: #241E1A;
        --color-ink-soft: #5B534A;
        --color-primary: #A33327;
        --color-primary-dark: #7A2019;
        --color-primary-tint: #F3E3DF;
        --color-indigo: #1F3A54;
        --color-indigo-tint: #E7EDF2;
        --color-border: #E8DFD0;
        --color-positive: #3A8556;
        --color-positive-tint: #E4F0E8;
        --color-neutral: #35608A;
        --color-neutral-tint: #E3ECF4;
        --color-negative: #B8433A;
        --color-negative-tint: #F7E5E2;
        --font-display: 'Fraunces', serif;
        --font-body: 'Plus Jakarta Sans', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    html, body, [class*="css"] { font-family: var(--font-body); }

    .stApp { background-color: var(--color-bg); }

    section[data-testid="stSidebar"] {
        background-color: var(--color-indigo);
        border-right: 1px solid var(--color-border);
    }
    section[data-testid="stSidebar"] * { color: #F1EDE4 !important; }
    section[data-testid="stSidebar"] svg { fill: #F1EDE4 !important; }

    h1, h2, h3 {
        font-family: var(--font-display) !important;
        color: var(--color-ink) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    p, div, span, label { color: var(--color-ink); }

    /* --- Eyebrow label (label kecil di atas judul) --- */
    .kop-eyebrow {
        font-family: var(--font-mono);
        font-size: 12px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--color-primary);
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* --- Kartu metrik custom --- */
    .kop-card {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 18px 20px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kop-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(36, 30, 26, 0.08);
    }
    .kop-card-label {
        font-family: var(--font-mono);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--color-ink-soft);
        margin-bottom: 6px;
    }
    .kop-card-value {
        font-family: var(--font-display);
        font-size: 28px;
        font-weight: 600;
        color: var(--color-ink);
        line-height: 1.1;
    }
    .kop-card-value.primary { color: var(--color-primary); }

    /* --- Badge sentimen --- */
    .kop-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 14px;
        font-family: var(--font-body);
    }
    .kop-badge.positive { background: var(--color-positive-tint); color: var(--color-positive); }
    .kop-badge.neutral  { background: var(--color-neutral-tint); color: var(--color-neutral); }
    .kop-badge.negative { background: var(--color-negative-tint); color: var(--color-negative); }

    /* --- Signature element: Denyut Opini (marquee ticker) --- */
    .kop-ticker-wrap {
        background: var(--color-ink);
        border-radius: 10px;
        padding: 10px 0;
        overflow: hidden;
        white-space: nowrap;
        position: relative;
        margin-bottom: 20px;
    }
    .kop-ticker-track {
        display: inline-block;
        animation: kop-scroll 38s linear infinite;
    }
    .kop-ticker-wrap:hover .kop-ticker-track { animation-play-state: paused; }
    @keyframes kop-scroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .kop-tick {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 0 10px;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-family: var(--font-body);
        background: rgba(255,255,255,0.06);
        color: #F1EDE4;
        border-left: 3px solid transparent;
    }
    .kop-tick.positive { border-left-color: #5CB37D; }
    .kop-tick.neutral  { border-left-color: #6E9BC7; }
    .kop-tick.negative { border-left-color: #E07A6D; }

    @media (prefers-reduced-motion: reduce) {
        .kop-ticker-track { animation: none; }
    }

    /* --- Divider bergaya stempel --- */
    .kop-divider {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 22px 0 14px;
        color: var(--color-ink-soft);
        font-family: var(--font-mono);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .kop-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--color-border);
    }

    /* --- Tombol utama --- */
    .stButton > button[kind="primary"] {
        background: var(--color-primary) !important;
        border: none !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--color-primary-dark) !important;
    }
    .stButton > button:not([kind="primary"]) {
        border-radius: 8px !important;
        border-color: var(--color-border) !important;
        font-family: var(--font-body) !important;
    }

    /* --- Progress bar --- */
    .stProgress > div > div > div { background-color: var(--color-primary) !important; }
    </style>
    """, unsafe_allow_html=True)


def eyebrow(text: str):
    st.markdown(f'<div class="kop-eyebrow">{text}</div>', unsafe_allow_html=True)


def section_divider(label: str):
    st.markdown(f'<div class="kop-divider">{label}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, primary: bool = False):
    cls = 'kop-card-value primary' if primary else 'kop-card-value'
    st.markdown(f"""
        <div class="kop-card">
            <div class="kop-card-label">{label}</div>
            <div class="{cls}">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def sentiment_badge(label: str) -> str:
    icons = {'positive': '😊', 'neutral': '😐', 'negative': '😠'}
    names = {'positive': 'Positive', 'neutral': 'Neutral', 'negative': 'Negative'}
    return f'<span class="kop-badge {label}">{icons.get(label,"")} {names.get(label,label)}</span>'


DEFAULT_TICKER_SAMPLES = [
    ("koperasi ini sangat membantu masyarakat desa, terima kasih pemerintah", 'positive'),
    ("saya tidak tahu apakah program ini akan berhasil atau tidak", 'neutral'),
    ("program ini gagal total dan hanya buang-buang anggaran negara", 'negative'),
    ("semoga kedepannya lebih transparan pengelolaannya", 'neutral'),
    ("akhirnya ada yang bantu umkm warung kecil di desa", 'positive'),
    ("kok malah jadi saingan warung madura ya, kasian rakyat kecil", 'negative'),
]


def render_ticker(samples=None):
    samples = samples or DEFAULT_TICKER_SAMPLES
    doubled = samples * 2  # untuk efek scroll looping mulus
    ticks = ''.join(
        f'<span class="kop-tick {label}">{"🟢" if label=="positive" else "🔵" if label=="neutral" else "🔴"} '
        f'&ldquo;{text}&rdquo;</span>'
        for text, label in doubled
    )
    st.markdown(f"""
        <div class="kop-ticker-wrap">
            <div class="kop-ticker-track">{ticks}</div>
        </div>
    """, unsafe_allow_html=True)
