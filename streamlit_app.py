import streamlit as st
import requests

# Titre et configuration de la page
st.set_page_config(page_title="Prévision de la Demande", page_icon="📊", layout="centered")

st.title("Application de Prévision de la Demande")
st.markdown("Cette application permet d'estimer les ventes futures d'un article dans un magasin.")

st.divider()

# Formulaire d'entrée
st.subheader("Paramètres de la prévision")

col1, col2 = st.columns(2)

with col1:
    store = st.number_input("Numéro du magasin (Store)", min_value=1, max_value=50, value=1)
    item = st.number_input("Numéro de l'article (Item)", min_value=1, max_value=50, value=10)

with col2:
    date_prevision = st.date_input("Date de prévision")

st.subheader("Historique récent des ventes (30 derniers jours)")
st.info("Saisissez ou modifiez les ventes récents sous forme de valeurs séparées par des virgules.")

# Historique par défaut avec 30 jours de ventes
default_history = "18, 21, 20, 22, 25, 23, 24, 20, 19, 21, 22, 23, 25, 24, 26, 27, 25, 24, 23, 22, 21, 23, 25, 27, 28, 26, 24, 23, 25, 27"
history_input = st.text_area("Historique (30 jours)", value=default_history)

# Bouton d'action
if st.button(" Obtenir la prévision", use_container_width=True):
    try:
        # Conversion du texte en liste de nombres
        historique_ventes = [float(x.strip()) for x in history_input.split(",") if x.strip()]
        
        if len(historique_ventes) < 30:
            st.error("⚠️ L'historique doit contenir au moins 30 valeurs.")
        else:
            with st.spinner("Calcul de la prévision en cours..."):
                # URL de votre API déployée sur Render
                url = "https://prevision-demande-article.onrender.com/predict"
                
                payload = {
                    "store": int(store),
                    "item": int(item),
                    "date_prevision": str(date_prevision),
                    "historique_ventes": historique_ventes
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    resultat = response.json()
                    st.success("Prévision calculée avec succès !")
                    st.metric(
                        label="Demande prévue pour cet article", 
                        value=f"{resultat['demande_prevue']} unités"
                    )
                else:
                    st.error(f"Erreur de l'API (Code {response.status_code})")
                    st.json(response.json())
                    
    except ValueError:
        st.error("Veuillez saisir des nombres valides pour l'historique de ventes.")