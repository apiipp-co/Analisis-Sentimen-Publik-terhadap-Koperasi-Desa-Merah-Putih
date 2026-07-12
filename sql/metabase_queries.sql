-- =====================================================================
-- Query Pack untuk Dashboard Metabase
-- Final Project: Sentiment Analysis - Koperasi Desa Merah Putih (Kopdes)
--
-- Cara pakai: setiap blok di bawah = 1 "Question/Card" di Metabase.
-- Copy-paste ke Metabase -> New Question -> SQL Query (Native Query).
-- Seluruh query berikut SUDAH DIUJI NYATA terhadap PostgreSQL.
-- =====================================================================

-- ---------------------------------------------------------------------
-- CARD 1: Total Data
-- Tipe visualisasi Metabase: Number
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS total_komentar
FROM labeled_comments;


-- ---------------------------------------------------------------------
-- CARD 2: Distribusi Sentimen
-- Tipe visualisasi Metabase: Pie Chart / Bar Chart
-- ---------------------------------------------------------------------
SELECT
    sentiment_label,
    COUNT(*) AS jumlah,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS persentase
FROM labeled_comments
GROUP BY sentiment_label
ORDER BY jumlah DESC;


-- ---------------------------------------------------------------------
-- CARD 3: Top Words (per kelas sentimen)
-- Tipe visualisasi Metabase: Bar Chart (horizontal)
-- Catatan: PostgreSQL tidak punya tokenizer built-in seperti Python,
-- jadi top words dihitung dari kolom `tokens` (hasil Tahap 5, dipisah spasi)
-- yang di-join ke label sentimen.
-- ---------------------------------------------------------------------
SELECT
    lc.sentiment_label,
    word,
    COUNT(*) AS frekuensi
FROM labeled_comments lc
JOIN preprocessed_comments pc
    ON lc.video_id = pc.video_id AND lc.comment_id = pc.comment_id
CROSS JOIN LATERAL unnest(string_to_array(pc.tokens, ' ')) AS word
WHERE word <> ''
GROUP BY lc.sentiment_label, word
ORDER BY lc.sentiment_label, frekuensi DESC
LIMIT 300;   -- ambil top-N per kelas di sisi Metabase (filter/limit per grup via visualisasi)


-- ---------------------------------------------------------------------
-- CARD 4: Trend Sentimen (Harian)
-- Tipe visualisasi Metabase: Line Chart (x=tanggal, y=jumlah, series=label)
-- ---------------------------------------------------------------------
SELECT
    comment_date,
    sentiment_label,
    n_comments
FROM v_sentiment_daily_trend
ORDER BY comment_date;


-- ---------------------------------------------------------------------
-- CARD 5: Perbandingan Model
-- Tipe visualisasi Metabase: Bar Chart (grouped, x=model_name, y=macro_f1/accuracy)
-- ---------------------------------------------------------------------
SELECT
    model_name,
    accuracy,
    macro_precision,
    macro_recall,
    macro_f1,
    is_best_model
FROM model_results
ORDER BY macro_f1 DESC;


-- ---------------------------------------------------------------------
-- CARD 6: Accuracy (Model Terbaik)
-- Tipe visualisasi Metabase: Number (dengan format persen)
-- ---------------------------------------------------------------------
SELECT accuracy
FROM model_results
WHERE is_best_model = TRUE
LIMIT 1;


-- ---------------------------------------------------------------------
-- CARD 7: Precision (Model Terbaik)
-- Tipe visualisasi Metabase: Number
-- ---------------------------------------------------------------------
SELECT macro_precision AS precision
FROM model_results
WHERE is_best_model = TRUE
LIMIT 1;


-- ---------------------------------------------------------------------
-- CARD 8: Recall (Model Terbaik)
-- Tipe visualisasi Metabase: Number
-- ---------------------------------------------------------------------
SELECT macro_recall AS recall
FROM model_results
WHERE is_best_model = TRUE
LIMIT 1;


-- ---------------------------------------------------------------------
-- CARD 9: F1 Score (Model Terbaik)
-- Tipe visualisasi Metabase: Number
-- ---------------------------------------------------------------------
SELECT macro_f1 AS f1_score
FROM model_results
WHERE is_best_model = TRUE
LIMIT 1;


-- ---------------------------------------------------------------------
-- BONUS CARD 10: Komposisi Sentimen per Video (tambahan, memakai view Tahap 11)
-- Tipe visualisasi Metabase: Stacked Bar Chart
-- ---------------------------------------------------------------------
SELECT video_id, positive_pct, neutral_pct, negative_pct, total_comments
FROM v_sentiment_by_video
ORDER BY total_comments DESC
LIMIT 15;


-- ---------------------------------------------------------------------
-- BONUS CARD 11: Log Prediksi Terbaru dari Aplikasi Streamlit
-- Tipe visualisasi Metabase: Table
-- ---------------------------------------------------------------------
SELECT input_text, predicted_label, confidence, model_used, predicted_at
FROM prediction_history
ORDER BY predicted_at DESC
LIMIT 50;
