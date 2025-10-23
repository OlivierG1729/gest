# utils/database.py
import psycopg
import pandas as pd

# Pour compatibilité avec l'ancien code psycopg2
connect = psycopg.connect


# --- Configuration Supabase ---
DB_CONFIG = {
    "host": "aws-1-eu-west-3.pooler.supabase.com",
    "port": 5432,
    "database": "postgres",
    "user": "postgres.rjwmpufueodmnbvnllst",
    "password": "Otaku1729#1729"  # 🔒 à remplacer par ton vrai mot de passe Supabase
}

def get_connection():
    """Crée une connexion PostgreSQL vers Supabase."""
    return psycopg2.connect(**DB_CONFIG)

# --- Initialisation des tables ---
def init_db():
    """Crée les tables si elles n'existent pas encore."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            nom TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id SERIAL PRIMARY KEY,
            montant REAL,
            date DATE,
            categorie TEXT REFERENCES categories(nom),
            commentaire TEXT,
            type_depense TEXT
        );
    """)

    # Insertion des catégories par défaut si vide
    cur.execute("SELECT COUNT(*) FROM categories;")
    if cur.fetchone()[0] == 0:
        categories_defaut = [
            ("Alimentation",), ("Logement",), ("Transport",),
            ("Loisirs",), ("Santé",), ("Autres",)
        ]
        cur.executemany("INSERT INTO categories (nom) VALUES (%s)", categories_defaut)

    conn.commit()
    conn.close()


def add_depense(montant, date, categorie, commentaire, type_depense):
    """Ajoute une dépense dans la base Supabase."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO depenses (montant, date, categorie, commentaire, type_depense)
        VALUES (%s, %s, %s, %s, %s);
    """, (montant, date, categorie, commentaire, type_depense))
    conn.commit()
    conn.close()


def load_depenses():
    """Charge toutes les dépenses sous forme de DataFrame pandas."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM depenses ORDER BY date DESC;", conn)
    conn.close()
    return df


def get_categories():
    """Retourne la liste des catégories existantes."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT nom FROM categories ORDER BY nom;")
    categories = [r[0] for r in cur.fetchall()]
    conn.close()
    return categories


def add_category(nouvelle_categorie):
    """Ajoute une catégorie si elle n'existe pas déjà."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO categories (nom) VALUES (%s);", (nouvelle_categorie,))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
    conn.close()
