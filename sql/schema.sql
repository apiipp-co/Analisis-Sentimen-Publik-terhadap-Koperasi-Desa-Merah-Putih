-- =====================================================================
-- Final Project: Sentiment Analysis - Koperasi Desa Merah Putih (Kopdes)
-- Database Schema untuk Supabase PostgreSQL
-- Dikembangkan & diuji menggunakan DBeaver terhadap PostgreSQL
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. raw_comments — data mentah hasil scraping (Tahap 1), TANPA modifikasi
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_comments (
    id                  BIGSERIAL PRIMARY KEY,
    video_id            BIGINT NOT NULL,
    comment_id          BIGINT NOT NULL,
    parent_comment_id   BIGINT,
    level               SMALLINT,
    username            TEXT,
    nickname            TEXT,
    comment             TEXT,
    create_time         TIMESTAMP NOT NULL,
    loaded_at           TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 2. clean_comments — hasil Tahap 4 (dedup + drop non-tekstual)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean_comments (
    id                  BIGSERIAL PRIMARY KEY,
    video_id            BIGINT NOT NULL,
    comment_id          BIGINT NOT NULL,
    parent_comment_id   BIGINT,
    level               SMALLINT,
    username            TEXT,
    nickname            TEXT,
    comment             TEXT NOT NULL,
    create_time         TIMESTAMP NOT NULL,
    loaded_at           TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_clean_comments_video_comment UNIQUE (video_id, comment_id)
);

-- ---------------------------------------------------------------------
-- 3. preprocessed_comments — hasil Tahap 5 (teks final utk TF-IDF)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS preprocessed_comments (
    id                  BIGSERIAL PRIMARY KEY,
    video_id            BIGINT NOT NULL,
    comment_id          BIGINT NOT NULL,
    text_final          TEXT NOT NULL,
    tokens              TEXT,
    loaded_at           TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_preprocessed_video_comment UNIQUE (video_id, comment_id)
);

-- ---------------------------------------------------------------------
-- 4. labeled_comments — hasil Tahap 6 (IndoBERT sentiment labeling)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS labeled_comments (
    id                    BIGSERIAL PRIMARY KEY,
    video_id              BIGINT NOT NULL,
    comment_id            BIGINT NOT NULL,
    comment               TEXT NOT NULL,
    text_for_bert         TEXT,
    sentiment_label       VARCHAR(10) NOT NULL
                          CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    sentiment_confidence  NUMERIC(6,4) CHECK (sentiment_confidence BETWEEN 0 AND 1),
    create_time           TIMESTAMP,
    loaded_at             TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_labeled_video_comment UNIQUE (video_id, comment_id)
);

-- ---------------------------------------------------------------------
-- 5. model_results — hasil Tahap 9-10 (perbandingan performa model)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_results (
    id                    BIGSERIAL PRIMARY KEY,
    model_name            VARCHAR(50) NOT NULL,
    dataset                VARCHAR(100),
    accuracy              NUMERIC(6,4),
    macro_precision        NUMERIC(6,4),
    macro_recall           NUMERIC(6,4),
    macro_f1               NUMERIC(6,4),
    weighted_precision     NUMERIC(6,4),
    weighted_recall        NUMERIC(6,4),
    weighted_f1            NUMERIC(6,4),
    cv_f1_macro_mean       NUMERIC(6,4),
    training_time_seconds  NUMERIC(10,3),
    n_test_samples         INTEGER,
    is_best_model          BOOLEAN NOT NULL DEFAULT FALSE,
    evaluated_at           TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 6. prediction_history — log prediksi dari aplikasi Streamlit (Tahap 13)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_history (
    id                BIGSERIAL PRIMARY KEY,
    input_text        TEXT NOT NULL,
    predicted_label   VARCHAR(10) NOT NULL
                      CHECK (predicted_label IN ('positive', 'neutral', 'negative')),
    confidence        NUMERIC(6,4),
    model_used        VARCHAR(50),
    source            VARCHAR(20) NOT NULL DEFAULT 'streamlit_app',
    predicted_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 7. dashboard_summary — ringkasan metrik untuk Metabase (Tahap 12)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dashboard_summary (
    id              BIGSERIAL PRIMARY KEY,
    metric_scope    VARCHAR(20) NOT NULL,   -- 'global' atau 'per_video'
    video_id        BIGINT,                  -- NULL jika metric_scope = 'global'
    metric_name     VARCHAR(50) NOT NULL,
    metric_value    NUMERIC(14,4),
    metric_text     TEXT,
    computed_at     TIMESTAMP NOT NULL DEFAULT now()
);

-- =====================================================================
-- INDEX — untuk mempercepat query dashboard Metabase & aplikasi Streamlit
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_raw_comments_video_id            ON raw_comments (video_id);
CREATE INDEX IF NOT EXISTS idx_raw_comments_create_time          ON raw_comments (create_time);

CREATE INDEX IF NOT EXISTS idx_clean_comments_video_id           ON clean_comments (video_id);

CREATE INDEX IF NOT EXISTS idx_preprocessed_video_id             ON preprocessed_comments (video_id);

CREATE INDEX IF NOT EXISTS idx_labeled_comments_video_id         ON labeled_comments (video_id);
CREATE INDEX IF NOT EXISTS idx_labeled_comments_sentiment        ON labeled_comments (sentiment_label);
CREATE INDEX IF NOT EXISTS idx_labeled_comments_create_time      ON labeled_comments (create_time);

CREATE INDEX IF NOT EXISTS idx_model_results_model_name          ON model_results (model_name);
CREATE INDEX IF NOT EXISTS idx_model_results_is_best             ON model_results (is_best_model);

CREATE INDEX IF NOT EXISTS idx_prediction_history_predicted_at   ON prediction_history (predicted_at);
CREATE INDEX IF NOT EXISTS idx_prediction_history_label          ON prediction_history (predicted_label);

CREATE INDEX IF NOT EXISTS idx_dashboard_summary_scope_metric    ON dashboard_summary (metric_scope, metric_name);

-- =====================================================================
-- VIEW — agregasi siap-pakai untuk Metabase (Tahap 12)
-- =====================================================================

-- View 1: komposisi sentimen per video (untuk chart "Trend Sentimen" & "Perbandingan per Video")
CREATE OR REPLACE VIEW v_sentiment_by_video AS
SELECT
    lc.video_id,
    COUNT(*)                                                  AS total_comments,
    COUNT(*) FILTER (WHERE lc.sentiment_label = 'positive')   AS positive_count,
    COUNT(*) FILTER (WHERE lc.sentiment_label = 'neutral')    AS neutral_count,
    COUNT(*) FILTER (WHERE lc.sentiment_label = 'negative')   AS negative_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE lc.sentiment_label = 'positive') / COUNT(*), 2) AS positive_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE lc.sentiment_label = 'neutral')  / COUNT(*), 2) AS neutral_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE lc.sentiment_label = 'negative') / COUNT(*), 2) AS negative_pct,
    ROUND(AVG(lc.sentiment_confidence)::numeric, 4)           AS avg_confidence
FROM labeled_comments lc
GROUP BY lc.video_id;

-- View 2: tren sentimen harian (untuk chart "Trend Sentimen" berbasis waktu)
CREATE OR REPLACE VIEW v_sentiment_daily_trend AS
SELECT
    DATE(lc.create_time)                                       AS comment_date,
    lc.sentiment_label,
    COUNT(*)                                                    AS n_comments
FROM labeled_comments lc
WHERE lc.create_time IS NOT NULL
GROUP BY DATE(lc.create_time), lc.sentiment_label
ORDER BY comment_date;

-- View 3: ringkasan performa model (untuk chart "Perbandingan Model", "Accuracy", dst.)
CREATE OR REPLACE VIEW v_model_performance AS
SELECT
    model_name,
    accuracy,
    macro_precision,
    macro_recall,
    macro_f1,
    is_best_model,
    evaluated_at
FROM model_results
ORDER BY macro_f1 DESC;
