# app.py
import streamlit as st
import pandas as pd
from datetime import date
from utils.database import init_db, add_depense, load_depenses, get_categories, add_category

# --- Initialisation de la base ---
init_db()

# --- Configuration Streamlit ---
st.set_page_config(page_title="Budget Manager", layout="wide")
st.title("💰 Gestionnaire de budget personnel")

menu = st.sidebar.radio("Navigation", ["Ajouter une dépense", "Historique / Statistiques"])

# === PAGE 1 : AJOUT D’UNE DÉPENSE ===
if menu == "Ajouter une dépense":
    st.header("🧾 Nouvelle dépense")

    # --- Bloc pour ajouter une catégorie ---
    with st.expander("➕ Ajouter une nouvelle catégorie"):
        nouvelle_cat = st.text_input("Nom de la nouvelle catégorie")
        if st.button("Ajouter cette catégorie"):
            if nouvelle_cat.strip():
                add_category(nouvelle_cat.strip().capitalize())
                st.success(f"✅ Catégorie '{nouvelle_cat}' ajoutée avec succès !")
            else:
                st.warning("Veuillez saisir un nom valide.")

    # Liste mise à jour des catégories
    categories = get_categories()

    # --- Formulaire de dépense ---
    montant = st.number_input("Montant (€)", min_value=0.0, step=0.01)
    date_dep = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
    categorie = st.selectbox("Catégorie", categories)
    type_depense = st.selectbox("Type de dépense", ["Perso", "Commune", "Pour ma conjointe"])
    commentaire = st.text_input("Commentaire facultatif")

    if st.button("💾 Enregistrer la dépense"):
        add_depense(montant, date_dep.isoformat(), categorie, commentaire, type_depense)
        st.success("✅ Dépense enregistrée avec succès !")

# === PAGE 2 : HISTORIQUE / STATISTIQUES ===
elif menu == "Historique / Statistiques":
    st.header("📊 Historique et statistiques des dépenses")

    df = load_depenses()

    if df.empty:
        st.info("Aucune dépense enregistrée pour le moment.")
    else:
        # Conversion et formatage français
        df["date"] = pd.to_datetime(df["date"])
        df["date_affichee"] = df["date"].dt.strftime("%d/%m/%Y")

        # --- Filtres de période ---
        min_date, max_date = df["date"].min().date(), df["date"].max().date()
        start, end = st.date_input(
            "Période :",
            [min_date, max_date],
            help="Format : jour/mois/année"
        )

        # --- Récupération de toutes les catégories existantes dans la base ---
        all_categories = get_categories()
        categories = ["Global"] + all_categories
        cat_choisie = st.selectbox("Catégorie :", categories, index=0)

        # --- Sélecteur Type de dépense avec option Global ---
        types = ["Global", "Perso", "Commune", "Pour ma conjointe"]
        type_choisi = st.selectbox("Type de dépense :", types, index=0)

        # --- Application des filtres ---
        mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)

        if cat_choisie != "Global":
            mask &= (df["categorie"] == cat_choisie)

        if type_choisi != "Global":
            mask &= (df["type_depense"] == type_choisi)

        df_filtre = df[mask]

        # --- Tableau d'affichage ergonomique ---
        df_affiche = df_filtre.copy()
        df_affiche["Date"] = df_affiche["date_affichee"]
        df_affiche["Montant (€)"] = df_affiche["montant"].map(lambda x: f"{x:,.2f} €".replace(",", " ").replace(".", ","))
        df_affiche = df_affiche[["Date", "Montant (€)", "categorie", "type_depense", "commentaire"]]
        df_affiche.columns = ["Date", "Montant (€)", "Catégorie", "Type", "Commentaire"]

        # --- Si aucune dépense ne correspond ---
        if df_affiche.empty:
            st.warning("Aucune dépense ne correspond à ces critères.")
        else:
            st.dataframe(df_affiche, use_container_width=True, hide_index=True)

            # --- Totaux ---
            total = df_filtre["montant"].sum()
            titre_total = "Total des dépenses"

            if cat_choisie != "Global":
                titre_total += f" — {cat_choisie}"
            if type_choisi != "Global":
                titre_total += f" ({type_choisi})"

            st.metric(titre_total, f"{total:,.2f} €".replace(",", " ").replace(".", ","))

            # --- Graphiques de répartition ---
            if cat_choisie == "Global" and type_choisi == "Global":
                st.subheader("📊 Répartition des dépenses")
                col1, col2 = st.columns(2)

                with col1:
                    st.caption("Par catégorie")
                    total_par_cat = df_filtre.groupby("categorie")["montant"].sum().reindex(all_categories, fill_value=0)
                    st.bar_chart(total_par_cat)

                with col2:
                    st.caption("Par type de dépense")
                    total_par_type = df_filtre.groupby("type_depense")["montant"].sum().sort_values(ascending=False)
                    st.bar_chart(total_par_type)
