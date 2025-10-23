# utils/ui_saisie.py
import streamlit as st
from datetime import date
from .database import ajouter_depense

def page_saisie():
    st.header("🧾 Nouvelle dépense")
    
    montant = st.number_input("Montant (€)", min_value=0.0, step=0.01)
    date_dep = st.date_input("Date", value=date.today())
    categorie = st.selectbox(
        "Catégorie",
        ["Alimentation", "Logement", "Transport", "Loisirs", "Santé", "Autres"]
    )
    commentaire = st.text_input("Commentaire facultatif")
    
    if st.button("💾 Enregistrer la dépense"):
        ajouter_depense(montant, date_dep.isoformat(), categorie, commentaire)
        st.success("✅ Dépense enregistrée avec succès !")
