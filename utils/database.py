import psycopg
import streamlit as st

# --- Configuration de la base Supabase ---
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "port": st.secrets.get("DB_PORT", 5432),
    "sslmode": "require"
}

# --- Connexion à la base ---
def get_connection():
    """Crée une connexion PostgreSQL vers Supabase."""
    return psycopg.connect(**DB_CONFIG)

# --- Initialisation des tables ---
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            nom TEXT UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id SERIAL PRIMARY KEY,
            montant NUMERIC(10,2) NOT NULL,
            categorie_id INTEGER REFERENCES categories(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- Opérations de base ---
def add_category(nom):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING;", (nom,))
    conn.commit()
    cur.close()
    conn.close()

def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories ORDER BY nom;")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories

def add_depense(montant, categorie_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO depenses (montant, categorie_id) VALUES (%s, %s);", (montant, categorie_id))
    conn.commit()
    cur.close()
    conn.close()

def load_depenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, d.montant, c.nom, d.date
        FROM depenses d
        LEFT JOIN categories c ON d.categorie_id = c.id
        ORDER BY d.date DESC;
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data
