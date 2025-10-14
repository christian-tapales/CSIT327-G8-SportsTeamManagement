import psycopg2

try:
    conn = psycopg2.connect(
        host="db.optirptpfjpyddemxpsg.supabase.co",
        database="postgres",
        user="collabsports",          # lowercase here
        password="TestPass123",
        port="5432",
        sslmode="require"
    )
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
