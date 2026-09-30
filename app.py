import streamlit as st
import requests


# Configuration de la page

st.set_page_config(
    page_title="Prévision de la demande",
    page_icon=None,
    layout="centered"
)


# Style de l'interface

st.markdown(
    """
    <style>

    .main {
        max-width: 900px;
        margin: auto;
    }

    .header {
        padding: 25px 30px;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #e1e5ea;
        margin-bottom: 25px;
    }

    .header h1 {
        margin-bottom: 8px;
        font-size: 30px;
    }

    .header p {
        margin-bottom: 0;
        color: #5f6368;
        font-size: 16px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .info-box {
        padding: 15px 18px;
        border-radius: 8px;
        background-color: #f8f9fa;
        border: 1px solid #e1e5ea;
        margin: 15px 0;
        color: #4a4a4a;
    }

    .result-box {
        padding: 25px;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #d9dee5;
        text-align: center;
        margin-top: 25px;
    }

    .result-title {
        font-size: 15px;
        color: #5f6368;
        margin-bottom: 8px;
    }

    .result-value {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .result-details {
        color: #5f6368;
        font-size: 14px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# En-tête

st.markdown(
    """
    <div class="header">
        <h1>Prévision de la demande</h1>
        <p>
            Application de prévision des ventes d'articles
            à partir de l'historique des ventes.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# Paramètres de la prévision

st.markdown(
    '<div class="section-title">Paramètres de la prévision</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


with col1:

    store = st.number_input(
        "Identifiant du magasin",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help=(
            "Les magasins disponibles dans le modèle "
            "sont numérotés de 1 à 10."
        )
    )

    item = st.number_input(
        "Identifiant de l'article",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help=(
            "Les articles disponibles dans le modèle "
            "sont numérotés de 1 à 50."
        )
    )


with col2:

    date_prevision = st.date_input(
        "Date de prévision"
    )


# Informations

st.markdown(
    """
    <div class="info-box">
        <strong>Informations sur les données</strong><br><br>
        Le modèle a été entraîné avec 10 magasins
        et 50 articles.<br>
        Les identifiants acceptés sont donc :
        magasins de 1 à 10 et articles de 1 à 50.
    </div>
    """,
    unsafe_allow_html=True
)


# Historique des ventes

st.markdown(
    '<div class="section-title">Historique des ventes</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
        Saisissez les ventes des 30 derniers jours
        <strong>de la plus ancienne à la plus récente</strong>.<br><br>
        La dernière valeur saisie correspond à la vente
        la plus récente.
    </div>
    """,
    unsafe_allow_html=True
)


default_history = (
    "27, 25, 23, 24, 26, 28, 27, 25, 23, 21, "
    "22, 23, 24, 25, 27, 26, 24, 23, 22, 21, "
    "23, 25, 27, 28, 26, 25, 24, 20, 21, 22"
)


history_input = st.text_area(
    "Ventes : plus ancienne → plus récente",
    value=default_history,
    height=130,
    help=(
        "Saisissez exactement 30 valeurs séparées par des virgules. "
        "La dernière valeur doit être la plus récente."
    )
)


# Bouton de prévision

st.markdown("<br>", unsafe_allow_html=True)

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

            demande_prevue = resultat["demande_prevue"]

            st.markdown(
                f"""
                <div class="result-box">
                    <div class="result-title">
                        Demande prévue
                    </div>

                    <div class="result-value">
                        {demande_prevue} unités
                    </div>

                    <div class="result-details">
                        Magasin : {resultat["store"]}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        Article : {resultat["item"]}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        Date : {resultat["date_prevision"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        else:

            st.error(
                f"Erreur de l'API (code {response.status_code})"
            )

            try:

                erreur = response.json()

                if isinstance(erreur, dict) and "detail" in erreur:

                    st.warning(
                        erreur["detail"]
                    )

                else:

                    st.json(erreur)

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


    except Exception as erreur:

        st.error(
            f"Une erreur inattendue est survenue : {erreur}"
        )