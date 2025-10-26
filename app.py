# app.py
import streamlit as st
import pandas as pd
from datetime import date
from utils.database import (
    init_db,
    add_depense,
    load_depenses,
    get_categories,
    add_category,
    update_depense,
    delete_depense,
)

# --- Initialisation de la base ---
init_db()

# --- Configuration Streamlit ---
import streamlit as st


# icone de l'application
st.set_page_config(
    page_title="Budget Manager",
    page_icon="favicon.png",  
    layout="wide"
)

st.set_page_config(page_title="Budget Manager", layout="wide")
st.title("💰 Gestionnaire de budget personnel")

# --- Menu latéral ---
menu = st.sidebar.radio(
    "Navigation",
    [
        "Ajouter une dépense",
        "Modifier ou supprimer une dépense",
        "Afficher l'historique et les statistiques",
    ],
)

# ==========================================================
# === PAGE 1 : AJOUT D’UNE DÉPENSE =========================
# ==========================================================
if menu == "Ajouter une dépense":
    st.header("🧾 Nouvelle dépense")

    # --- Bloc pour ajouter une catégorie ---
    with st.expander("➕ Ajouter une nouvelle catégorie"):
        nouvelle_cat = st.text_input("Nom de la nouvelle catégorie")
        if st.button("Ajouter cette catégorie"):
            if nouvelle_cat.strip():
                add_category(nouvelle_cat.strip().capitalize())
                st.success(f"✅ Catégorie '{nouvelle_cat}' ajoutée avec succès !")
                st.rerun()
            else:
                st.warning("Veuillez saisir un nom valide.")

    # Liste mise à jour des catégories
    categories = get_categories()
    category_names = [c[1] for c in categories]

    # --- Formulaire de dépense ---
    montant = st.number_input("Montant (€)", min_value=0.0, step=0.01)
    date_dep = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
    categorie_nom = st.selectbox("Catégorie", category_names)
    type_depense = st.selectbox("Type de dépense", ["Perso", "Commune", "Pour ma conjointe"])
    commentaire = st.text_input("Commentaire facultatif")

    categorie_id = next((c[0] for c in categories if c[1] == categorie_nom), None)

    if st.button("💾 Enregistrer la dépense"):
        if categorie_id is not None:
            add_depense(montant, date_dep.isoformat(), categorie_id, commentaire, type_depense)
            st.success("✅ Dépense enregistrée avec succès !")
            st.rerun()
        else:
            st.error("❌ Erreur : catégorie introuvable.")


# ==========================================================
# === PAGE 2 : MODIFIER / SUPPRIMER ========================
# ==========================================================
elif menu == "Modifier ou supprimer une dépense":
    st.header("✏️ Modifier ou supprimer une dépense")

    df = load_depenses()

    if df.empty:
        st.info("Aucune dépense enregistrée pour le moment.")
    else:
        # Conversion et formatage
        df["date"] = pd.to_datetime(df["date"])
        df["date_affichee"] = df["date"].dt.strftime("%d/%m/%Y")

        # Sélecteur d'une dépense
        df["description"] = df.apply(
            lambda x: f"{x['date_affichee']} — {x['categorie']} — {x['montant']:.2f} €", axis=1
        )
        depense_selectionnee = st.selectbox("Choisissez une dépense :", df["description"])

        depense_id = df.loc[df["description"] == depense_selectionnee, "id"].values[0]
        dep = df[df["id"] == depense_id].iloc[0]

        # --- Formulaire d’édition ---
        categories = get_categories()
        all_categories = [c[1] for c in categories]

        new_montant = st.number_input("Montant (€)", value=float(dep["montant"]), step=0.01)
        new_date = st.date_input("Date", value=pd.to_datetime(dep["date"]).date())
        new_cat = st.selectbox("Catégorie", all_categories, index=all_categories.index(dep["categorie"]))
        new_type = st.selectbox("Type de dépense", ["Perso", "Commune", "Pour ma conjointe"],
                                index=["Perso", "Commune", "Pour ma conjointe"].index(dep["type_depense"]))
        new_commentaire = st.text_input("Commentaire", value=dep["commentaire"] or "")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Enregistrer les modifications"):
                cat_id = next((c[0] for c in categories if c[1] == new_cat), None)
                if cat_id:
                    update_depense(depense_id, new_montant, new_date.isoformat(), cat_id, new_type, new_commentaire)
                    st.success("✅ Dépense mise à jour avec succès !")
                    st.rerun()

        with col2:
            if st.button("🗑️ Supprimer cette dépense"):
                delete_depense(depense_id)
                st.warning("🗑️ Dépense supprimée.")
                st.rerun()


# ==========================================================
# === PAGE 3 : HISTORIQUE / STATISTIQUES ===================
# ==========================================================
elif menu == "Afficher l'historique et les statistiques":
    st.header("📊 Historique et statistiques des dépenses")

    df = load_depenses()

    if df.empty:
        st.info("Aucune dépense enregistrée pour le moment.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        df["date_affichee"] = df["date"].dt.strftime("%d/%m/%Y")

        # --- Filtres ---
        min_date, max_date = df["date"].min().date(), df["date"].max().date()
        start, end = st.date_input("Période :", [min_date, max_date])

        all_categories = [c[1] for c in get_categories()]
        categories = ["Global"] + all_categories
        cat_choisie = st.selectbox("Catégorie :", categories, index=0)

        types = ["Global", "Perso", "Commune", "Pour ma conjointe"]
        type_choisi = st.selectbox("Type de dépense :", types, index=0)

        mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)

        if cat_choisie != "Global":
            mask &= df["categorie"] == cat_choisie
        if type_choisi != "Global":
            mask &= df["type_depense"] == type_choisi

        df_filtre = df[mask]

        df_affiche = df_filtre.copy()
        df_affiche["Date"] = df_affiche["date_affichee"]
        df_affiche["Montant (€)"] = df_affiche["montant"].map(lambda x: f"{x:,.2f} €".replace(",", " ").replace(".", ","))
        df_affiche = df_affiche[["Date", "Montant (€)", "categorie", "type_depense", "commentaire"]]
        df_affiche.columns = ["Date", "Montant (€)", "Catégorie", "Type", "Commentaire"]

        if df_affiche.empty:
            st.warning("Aucune dépense ne correspond à ces critères.")
        else:
            st.dataframe(df_affiche, use_container_width=True, hide_index=True)

            total = df_filtre["montant"].sum()
            titre_total = "Total des dépenses"
            if cat_choisie != "Global":
                titre_total += f" — {cat_choisie}"
            if type_choisi != "Global":
                titre_total += f" ({type_choisi})"
            st.metric(titre_total, f"{total:,.2f} €".replace(",", " ").replace(".", ","))

            # Graphiques
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
