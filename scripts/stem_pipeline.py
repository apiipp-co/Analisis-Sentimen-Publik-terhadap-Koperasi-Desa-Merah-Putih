import pandas as pd
import re
import time
import json
import os
import sys
from collections import Counter
import emoji as emoji_lib
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE, 'scripts', 'stem_progress.log')
FREQ_THRESHOLD = 3  # stem tokens appearing >=3 times in corpus; rarer tokens (typo/long-tail) kept unstemmed

def log(msg):
    with open(LOG_PATH, 'a') as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    print(msg)
    sys.stdout.flush()

open(LOG_PATH, 'w').close()
log('=== START stem_pipeline.py ===')

df = pd.read_parquet(os.path.join(BASE, 'data/interim/clean_comments_kopdes.parquet'))
log(f'Loaded clean data: {len(df):,} rows')

def case_folding(text):
    return text.lower()

def remove_url(text):
    return re.sub(r'https?://\S+|www\.\S+', ' ', text)

def remove_mention(text):
    return re.sub(r'@\w+', ' ', text)

def remove_hashtag(text):
    return re.sub(r'#\w+', ' ', text)

def remove_system_tags(text):
    return re.sub(r'\[sticker\]', ' ', text, flags=re.IGNORECASE)

def remove_emoji(text):
    return emoji_lib.replace_emoji(text, replace=' ')

def remove_number(text):
    return re.sub(r'\d+', ' ', text)

def remove_punctuation(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'_', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_elongation(text):
    # kuatiiirrrr -> kuatiirr (max 2 repeated chars) - reduces spelling-variant explosion
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

t0 = time.time()
df['text_step1_casefold'] = df['comment'].astype(str).apply(case_folding)
df['text_step2_cleaned'] = (
    df['text_step1_casefold']
    .apply(remove_url).apply(remove_mention).apply(remove_hashtag).apply(remove_system_tags)
)
df['text_step3_noemoji'] = df['text_step2_cleaned'].apply(remove_emoji)
df['text_step4_nonum'] = df['text_step3_noemoji'].apply(remove_number)
df['text_step5_clean'] = df['text_step4_nonum'].apply(remove_punctuation).apply(normalize_elongation)
log(f'Cleaning steps 1-5 done in {time.time()-t0:.1f}s')

n_before = len(df)
df = df[df['text_step5_clean'].str.strip() != ''].reset_index(drop=True)
log(f'Drop residu kosong pasca-cleaning: {n_before:,} -> {len(df):,}')

df['tokens'] = df['text_step5_clean'].apply(lambda s: s.split())

stopword_factory = StopWordRemoverFactory()
stopwords_formal = set(stopword_factory.get_stop_words())
stopwords_colloquial = {
    'yg', 'ga', 'gak', 'gk', 'nggak', 'ngga', 'nya', 'dgn', 'dg', 'aja', 'sih', 'deh', 'kok',
    'dong', 'donk', 'banget', 'bgt', 'emang', 'emg', 'udah', 'udh', 'dah', 'nih', 'tuh', 'kan',
    'ya', 'yah', 'loh', 'lho', 'lah', 'kah', 'pun', 'juga', 'jg', 'sm', 'sama', 'trus', 'terus',
    'krn', 'karna', 'utk', 'sdh', 'blm', 'belom', 'gitu', 'gt', 'gini', 'gni', 'klo', 'kalo',
    'gmn', 'gimana', 'org', 'orang', 'sy', 'saya', 'kalian', 'kmu', 'kamu', 'lu', 'lo', 'gue',
    'gw', 'ni', 'si', 'nder', 'wkwk', 'wkwkwk', 'haha', 'hehe',
}
all_stopwords = stopwords_formal | stopwords_colloquial
log(f'Total stopwords: {len(all_stopwords)}')

def remove_stopwords(tokens):
    return [t for t in tokens if t not in all_stopwords and len(t) > 1]

t0 = time.time()
df['tokens_nostop'] = df['tokens'].apply(remove_stopwords)
log(f'Stopword removal done in {time.time()-t0:.1f}s')

# Frequency-based stemming scope
counter = Counter()
for toks in df['tokens_nostop']:
    counter.update(toks)
total_occ = sum(counter.values())
tokens_to_stem = [tok for tok, c in counter.items() if c >= FREQ_THRESHOLD]
occ_covered = sum(counter[t] for t in tokens_to_stem)
log(f'Unique tokens total: {len(counter):,}')
log(f'Tokens to stem (freq>={FREQ_THRESHOLD}): {len(tokens_to_stem):,} '
    f'({len(tokens_to_stem)/len(counter)*100:.1f}% of vocab, '
    f'{occ_covered/total_occ*100:.2f}% of total occurrences)')

factory = StemmerFactory()
stemmer = factory.create_stemmer()

stem_cache = {}
t0 = time.time()
CHECKPOINT_EVERY = 1000
for i, tok in enumerate(tokens_to_stem, 1):
    stem_cache[tok] = stemmer.stem(tok)
    if i % CHECKPOINT_EVERY == 0:
        elapsed = time.time() - t0
        rate = i / elapsed
        remaining = (len(tokens_to_stem) - i) / rate
        log(f'Stemmed {i:,}/{len(tokens_to_stem):,} tokens '
            f'({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining, {rate:.1f} tok/s)')
        # checkpoint save
        with open(os.path.join(BASE, 'scripts', 'stem_cache_checkpoint.json'), 'w') as f:
            json.dump(stem_cache, f)

log(f'Stemming complete: {len(stem_cache):,} tokens in {time.time()-t0:.1f}s')

with open(os.path.join(BASE, 'scripts', 'stem_cache_checkpoint.json'), 'w') as f:
    json.dump(stem_cache, f)

def stem_tokens(tokens):
    return [stem_cache.get(t, t) for t in tokens]

df['tokens_stemmed'] = df['tokens_nostop'].apply(stem_tokens)
df['tokens_stemmed'] = df['tokens_stemmed'].apply(lambda toks: [t for t in toks if t.strip() != ''])
df['text_final'] = df['tokens_stemmed'].apply(lambda toks: ' '.join(toks))

n_before_final = len(df)
empty_final = df['text_final'].str.strip() == ''
log(f'Baris tanpa token tersisa: {empty_final.sum():,}')
df_final = df[~empty_final].reset_index(drop=True)
log(f'Baris final: {n_before_final:,} -> {len(df_final):,}')

assert len(df_final) >= 5000
assert df_final['text_final'].isnull().sum() == 0
assert (df_final['text_final'].str.strip() == '').sum() == 0
log('VALIDASI PASSED')

cols_to_keep = [
    'video_id', 'comment_id', 'parent_comment_id', 'level', 'username', 'nickname',
    'create_time', 'comment', 'text_final', 'tokens_stemmed'
]
df_out = df_final[cols_to_keep].copy()
df_out = df_out.rename(columns={'tokens_stemmed': 'tokens'})
df_out_parquet = df_out.copy()
df_out_parquet['tokens'] = df_out_parquet['tokens'].apply(lambda x: ' '.join(x))

os.makedirs(os.path.join(BASE, 'data/interim'), exist_ok=True)
df_out_parquet.to_parquet(os.path.join(BASE, 'data/interim/preprocessed_comments_kopdes.parquet'), index=False)
df_out_parquet.to_csv(os.path.join(BASE, 'data/interim/preprocessed_comments_kopdes.csv'), index=False)

token_counts = df_final['tokens_stemmed'].apply(len)
preprocessing_summary = {
    'n_rows_input': int(n_before),
    'n_rows_output': int(len(df_out)),
    'n_unique_tokens_total': len(counter),
    'n_unique_tokens_stemmed': len(tokens_to_stem),
    'freq_threshold_for_stemming': FREQ_THRESHOLD,
    'pct_occurrence_coverage_stemmed': round(occ_covered/total_occ*100, 2),
    'avg_tokens_per_comment': float(token_counts.mean()),
    'median_tokens_per_comment': float(token_counts.median()),
    'stopwords_total': len(all_stopwords),
    'steps_applied': [
        'case_folding', 'remove_url', 'remove_mention', 'remove_hashtag', 'remove_system_tags',
        'remove_emoji', 'remove_number', 'remove_punctuation', 'normalize_elongation',
        'tokenization', 'stopword_removal (formal+colloquial)',
        'stemming (Sastrawi, frequency-thresholded + cached)'
    ]
}
with open(os.path.join(BASE, 'reports/preprocessing_summary.json'), 'w') as f:
    json.dump(preprocessing_summary, f, indent=2)

log('=== DONE ===')
log(json.dumps(preprocessing_summary, indent=2))
