# utils/ui_stats.py
import streamlit as st
import pandas as pd
from .database import lire_depenses

def page_stats():
    st.header("📊 Historique et statistiques")
    
    df = lire_depenses()
    if df.empty:
        st.info("Aucune dépense enregistrée pour le moment.")
        return
    
    df["date"] = pd.to_datetime(df["date"])
    
    # Filtres
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    start, end = st.date_input("Période :", [min_date, max_date])
    categories = st.multiselect("Catégorie :", df["categorie"].unique())
    
    # Application des filtres
    mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
    if categories:
        mask &= df["categorie"].isin(categories)
    df_filtre = df[mask]
    
    st.dataframe(df_filtre, use_container_width=True)
    
    # Totaux
    total = df_filtre["montant"].sum()
    st.metric("Total sur la période", f"{total:.2f} €")
    
    total_cat = df_filtre.groupby("categorie")["montant"].sum().sort_values(ascending=False)
    st.bar_chart(total_cat)
    
    with st.expander("📥 Exporter les données filtrées"):
        csv = df_filtre.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger CSV", csv, "depenses_filtrees.csv", "text/csv")
