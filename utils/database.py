# utils/database.py
import psycopg
import streamlit as st

# --- Configuration de la base Supabase ---
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "port": st.secrets.get("DB_PORT", 5432),
    "sslmode": "require",
}


# ==========================================================
# === Connexion à la base ==================================
# ==========================================================
def get_connection():
    """Crée une connexion PostgreSQL vers Supabase."""
    return psycopg.connect(**DB_CONFIG)


# ==========================================================
# === Initialisation des tables ============================
# ==========================================================
def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = get_connection()
    cur = conn.cursor()

    # Table des catégories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            nom TEXT UNIQUE NOT NULL
        );
    """)

    # Table des dépenses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id SERIAL PRIMARY KEY,
            montant NUMERIC(10,2) NOT NULL,
            date DATE NOT NULL,
            categorie_id INTEGER REFERENCES categories(id),
            type_depense TEXT,
            commentaire TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ==========================================================
# === CRUD : Catégories ====================================
# ==========================================================
def add_category(nom):
    """Ajoute une nouvelle catégorie (si elle n'existe pas déjà)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING;", (nom,))
    conn.commit()
    cur.close()
    conn.close()


def get_categories():
    """Retourne la liste des catégories sous forme [(id, nom), ...]."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories ORDER BY nom ASC;")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories


# ==========================================================
# === CRUD : Dépenses ======================================
# ==========================================================
def add_depense(montant, date_dep, categorie_id, commentaire, type_depense):
    """Ajoute une nouvelle dépense."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO depenses (montant, date, categorie_id, commentaire, type_depense)
        VALUES (%s, %s, %s, %s, %s);
    """, (montant, date_dep, categorie_id, commentaire, type_depense))
    conn.commit()
    cur.close()
    conn.close()


def load_depenses():
    """Charge toutes les dépenses avec leurs catégories associées."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            d.id,
            d.montant,
            c.nom AS categorie,
            d.date,
            d.type_depense,
            d.commentaire
        FROM depenses d
        LEFT JOIN categories c ON d.categorie_id = c.id
        ORDER BY d.date DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Conversion en DataFrame compatible Streamlit
    if not rows:
        return pd.DataFrame(columns=["id", "montant", "categorie", "date", "type_depense", "commentaire"])

    import pandas as pd
    df = pd.DataFrame(rows, columns=["id", "montant", "categorie", "date", "type_depense", "commentaire"])
    return df


def update_depense(depense_id, montant, date_dep, categorie_id, type_depense, commentaire):
    """Met à jour une dépense existante."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE depenses
        SET montant = %s, date = %s, categorie_id = %s, type_depense = %s, commentaire = %s
        WHERE id = %s;
    """, (montant, date_dep, categorie_id, type_depense, commentaire, depense_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_depense(depense_id):
    """Supprime une dépense existante."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM depenses WHERE id = %s;", (depense_id,))
    conn.commit()
    cur.close()
    conn.close()
