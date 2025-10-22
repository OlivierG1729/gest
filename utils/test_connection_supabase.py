import psycopg2

conn = psycopg2.connect(
    host="aws-1-eu-west-3.pooler.supabase.com",
    port=5432,
    database="postgres",
    user="postgres.rjwmpufueodmnbvnllst",
    password="Otaku1729#1729"
)
print("✅ Connexion réussie à Supabase via IPv4 (Session Pooler) !")
conn.close()
