# Tahap 12 — Setup Dashboard Metabase
**Final Project: Sentiment Analysis — Koperasi Desa Merah Putih (Kopdes)**

Metabase adalah aplikasi BI (GUI), bukan kode yang dieksekusi di notebook — sehingga tahap ini
berupa **panduan langkah demi langkah** + **paket query SQL yang sudah diuji nyata** (lihat
`sql/metabase_queries.sql`, seluruh query sudah divalidasi jalan tanpa error terhadap
PostgreSQL).

---

## 1. Instalasi Metabase

Pilih salah satu:

### Opsi A — Docker (direkomendasikan, paling mudah)
```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```
Setelah container jalan (~1-2 menit warm-up), buka `http://localhost:3000`.

### Opsi B — JAR (jika tidak punya Docker)
Butuh Java 11+.
```bash
# Unduh dari situs resmi Metabase (bukan GitHub release, OSS jar didistribusikan terpisah):
# https://www.metabase.com/start/oss/jar
java -jar metabase.jar
```
Buka `http://localhost:3000`.

### Opsi C — Metabase Cloud
Jika ingin dashboard bisa diakses publik tanpa hosting sendiri, daftar di
`https://www.metabase.com/cloud` (ada free trial).

---

## 2. Setup Akun & Koneksi ke Supabase

1. Buka `http://localhost:3000`, ikuti wizard setup awal (buat akun admin).
2. Saat diminta "Add your data", pilih **PostgreSQL**.
3. Isi form koneksi dengan kredensial Supabase (sama seperti `.env` di Tahap 11):

| Field | Isi dengan |
|---|---|
| Display name | Kopdes Sentiment DB |
| Host | `db.xxxxxxxxxxxx.supabase.co` (dari Supabase Dashboard) |
| Port | `5432` |
| Database name | `postgres` |
| Username | `postgres` |
| Password | (password Supabase project kamu) |
| Use a secure connection (SSL) | **ON** (wajib untuk Supabase) |

4. Klik **Save**. Metabase akan otomatis melakukan *sync* skema (mendeteksi 7 tabel + 3 view
   dari Tahap 11).

---

## 3. Membuat 9 Card Wajib + 2 Bonus

Untuk tiap card: **New -> Question -> Native query (SQL)**, pilih database "Kopdes Sentiment
DB", paste query dari `sql/metabase_queries.sql`, klik **Visualize**, pilih tipe chart sesuai
tabel di bawah, lalu **Save**.

| # | Nama Card | Query (lihat file) | Tipe Visualisasi |
|---|---|---|---|
| 1 | Total Data | CARD 1 | Number |
| 2 | Distribusi Sentimen | CARD 2 | Pie Chart |
| 3 | Top Words | CARD 3 | Bar Chart (gunakan filter/segment per `sentiment_label` di Metabase) |
| 4 | Trend Sentimen | CARD 4 | Line Chart (x=`comment_date`, series=`sentiment_label`) |
| 5 | Perbandingan Model | CARD 5 | Bar Chart (grouped, x=`model_name`) |
| 6 | Accuracy | CARD 6 | Number (format: Percent) |
| 7 | Precision | CARD 7 | Number (format: Percent) |
| 8 | Recall | CARD 8 | Number (format: Percent) |
| 9 | F1 Score | CARD 9 | Number (format: Percent) |
| 10 (bonus) | Sentimen per Video | BONUS CARD 10 | Stacked Bar Chart |
| 11 (bonus) | Log Prediksi Terbaru | BONUS CARD 11 | Table |

**Catatan Card 3 (Top Words):** query mengembalikan top words per kelas sekaligus. Di Metabase,
tambahkan **filter** pada visualisasi (klik kolom `sentiment_label` -> Add filter) supaya bisa
toggle antar kelas, atau buat 3 card terpisah (tambahkan `WHERE sentiment_label = 'positive'`
dkk pada query) jika ingin ketiganya tampil berdampingan di dashboard.

---

## 4. Menyusun Dashboard

1. **New -> Dashboard**, beri nama "Kopdes Sentiment Analysis Dashboard".
2. Tambahkan seluruh card di atas, susun layout:
   - Baris 1: Total Data, Accuracy, Precision, Recall, F1 Score (5 number card kecil sejajar)
   - Baris 2: Distribusi Sentimen (kiri), Perbandingan Model (kanan)
   - Baris 3: Trend Sentimen (lebar penuh)
   - Baris 4: Top Words (kiri), Sentimen per Video (kanan)
   - Baris 5: Log Prediksi Terbaru (lebar penuh, tabel)
3. **Save**. Aktifkan **Auto-refresh** (klik ikon jam di pojok kanan atas dashboard, pilih
   interval mis. 1 jam) supaya dashboard ter-update otomatis saat ada prediksi baru dari
   Streamlit (Tahap 13).

---

## 5. Validasi Checklist

- [ ] Koneksi Metabase -> Supabase berhasil (skema 7 tabel + 3 view tersinkron)
- [ ] Semua 9 card wajib dibuat dan menampilkan data (bukan error/kosong)
- [ ] Dashboard tersimpan dan bisa diakses ulang
- [ ] Auto-refresh dashboard aktif

**Status: Tahap 12 (Dashboard Metabase) — panduan & query pack selesai, seluruh query
tervalidasi nyata terhadap PostgreSQL.** Eksekusi setup GUI-nya dilakukan langsung oleh kamu
(butuh instance Metabase berjalan + kredensial Supabase asli). Lanjut ke **Tahap 13: Deployment
Streamlit**.
