# utils/database.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/depenses.db")

def init_db():
    """Initialise la base de données et les tables si elles n'existent pas, 
    et ajoute les colonnes manquantes si besoin."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- Création de la table depenses si elle n'existe pas ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            montant REAL,
            date TEXT,
            categorie TEXT,
            commentaire TEXT,
            type_depense TEXT
        )
    """)
    conn.commit()

    # --- Vérification des colonnes existantes ---
    c.execute("PRAGMA table_info(depenses)")
    existing_cols = [col[1] for col in c.fetchall()]

    expected_cols = {
        "montant": "REAL",
        "date": "TEXT",
        "categorie": "TEXT",
        "commentaire": "TEXT",
        "type_depense": "TEXT"
    }

    # --- Ajout automatique des colonnes manquantes ---
    for col, col_type in expected_cols.items():
        if col not in existing_cols:
            print(f"⚙️ Ajout de la colonne manquante '{col}' ({col_type}) à la table depenses...")
            c.execute(f"ALTER TABLE depenses ADD COLUMN {col} {col_type}")
            conn.commit()

    # --- Table des catégories ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE
        )
    """)

    # --- Insertion des catégories par défaut si vide ---
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        categories_defaut = [
            ("Alimentation",), ("Logement",), ("Transport",),
            ("Loisirs",), ("Santé",), ("Autres",)
        ]
        c.executemany("INSERT INTO categories (nom) VALUES (?)", categories_defaut)
        conn.commit()

    conn.close()


def add_depense(montant, date, categorie, commentaire, type_depense):
    """Ajoute une dépense dans la base."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO depenses (montant, date, categorie, commentaire, type_depense) VALUES (?, ?, ?, ?, ?)",
        (montant, date, categorie, commentaire, type_depense)
    )
    conn.commit()
    conn.close()


def load_depenses():
    """Charge toutes les dépenses sous forme de DataFrame pandas."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM depenses", conn)
    conn.close()
    return df


def get_categories():
    """Retourne la liste des catégories existantes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nom FROM categories ORDER BY nom")
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories


def add_category(nouvelle_categorie):
    """Ajoute une nouvelle catégorie si elle n'existe pas déjà."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (nom) VALUES (?)", (nouvelle_categorie,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # ignore si la catégorie existe déjà
    conn.close()
