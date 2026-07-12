from sqlalchemy import create_engine, text

DB_HOST = "supabase kamu apa namannya"
DB_PORT = "6543"
DB_NAME = "hehehe898x"
DB_USER = "apipgantengg"
DB_PASSWORD = "hehehegoodluck"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

try:
    with engine.connect() as conn:
        print("✅ Koneksi berhasil!")
        print("Database :", conn.execute(text("SELECT current_database();")).scalar())
        print("Versi    :", conn.execute(text("SELECT version();")).scalar())

        print("\nDaftar tabel:")
        tables = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        for row in tables:
            print("-", row[0])

except Exception as e:
    print("❌ Koneksi gagal!")
    print(e)
