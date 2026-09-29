import streamlit as st
import requests


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Prévision de la Demande",
    layout="centered"
)


# ============================================================
# TITRE
# ============================================================

st.title("Application de Prévision de la Demande")

st.markdown(
    "Cette application permet d'estimer les ventes futures "
    "d'un article dans un magasin."
)

st.divider()


# ============================================================
# PARAMÈTRES DE LA PRÉVISION
# ============================================================

st.subheader("Paramètres de la prévision")

col1, col2 = st.columns(2)


with col1:

    store = st.number_input(
        "Identifiant du magasin (Store ID)",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="Identifiant du magasin présent dans le jeu de données : de 1 à 10."
    )

    item = st.number_input(
        "Identifiant de l'article (Item ID)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="Identifiant de l'article présent dans le jeu de données."
    )


with col2:

    date_prevision = st.date_input(
        "Date de prévision"
    )


# ============================================================
# INFORMATION SUR LES IDENTIFIANTS
# ============================================================

st.info(
    "Le numéro du magasin et le numéro de l'article sont des "
    "identifiants présents dans les données. Ils ne représentent "
    "ni le nombre de magasins, ni la quantité d'articles."
)


# ============================================================
# HISTORIQUE DES VENTES
# ============================================================

st.subheader("Historique récent des ventes (30 derniers jours)")

st.info(
    "Saisissez les ventes des 30 derniers jours "
    "de la plus récente à la plus ancienne. "
    "La première valeur correspond donc à la vente la plus récente."
)


default_history = (
    "18, 21, 20, 22, 25, 23, 24, 20, 19, 21, "
    "22, 23, 25, 24, 26, 27, 25, 24, 23, 22, "
    "21, 23, 25, 27, 28, 26, 24, 23, 25, 27"
)


history_input = st.text_area(
    "Ventes : plus récente → plus ancienne",
    value=default_history,
    height=120
)


# ============================================================
# BOUTON DE PRÉVISION
# ============================================================

if st.button(
    "Obtenir la prévision",
    use_container_width=True
):

    try:

        # Conversion du texte en liste de nombres
        historique_ventes = [
            float(x.strip())
            for x in history_input.split(",")
            if x.strip()
        ]


        # Vérification du nombre de valeurs
        if len(historique_ventes) != 30:

            st.error(
                f"Vous avez saisi {len(historique_ventes)} valeurs. "
                "L'historique doit contenir exactement 30 valeurs."
            )

            st.stop()


        # Vérification des valeurs négatives
        if any(vente < 0 for vente in historique_ventes):

            st.error(
                "Les ventes ne peuvent pas être négatives."
            )

            st.stop()


        # Appel de l'API
        with st.spinner(
            "Calcul de la prévision en cours..."
        ):

            url = (
                "https://prevision-demande-article.onrender.com"
                "/predict"
            )


            payload = {
                "store": int(store),
                "item": int(item),
                "date_prevision": str(date_prevision),
                "historique_ventes": historique_ventes
            }


            response = requests.post(
                url,
                json=payload,
                timeout=60
            )


        # Traitement de la réponse
        if response.status_code == 200:

            resultat = response.json()

            st.success(
                "Prévision calculée avec succès."
            )

            st.metric(
                label="Demande prévue pour cet article",
                value=f"{resultat['demande_prevue']} unités"
            )

            st.caption(
                f"Magasin : {int(store)} | "
                f"Article : {int(item)} | "
                f"Date : {date_prevision}"
            )


        else:

            st.error(
                f"Erreur de l'API (code {response.status_code})"
            )

            try:
                st.json(response.json())

            except Exception:
                st.write(response.text)


    except ValueError:

        st.error(
            "Veuillez saisir uniquement des nombres valides "
            "séparés par des virgules."
        )


    except requests.exceptions.Timeout:

        st.error(
            "Le serveur met trop de temps à répondre. "
            "Veuillez réessayer dans quelques instants."
        )


    except requests.exceptions.ConnectionError:

        st.error(
            "Impossible de contacter l'API. "
            "Vérifiez que le service Render est disponible."
        )


    except Exception as e:

        st.error(
            f"Une erreur inattendue est survenue : {e}"
        )