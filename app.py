import streamlit as st
import requests


# Configuration de la page

st.set_page_config(
    page_title="Prévision de la demande d'articles en magasin",
    layout="centered"
)


# Style général

st.markdown(
    """
    <style>
        .block-container {
            max-width: 900px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        .description {
            font-size: 1rem;
            opacity: 0.75;
            margin-top: -0.5rem;
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }

        div.stButton > button {
            width: 100%;
            min-height: 3rem;
            font-size: 1rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# En-tête

st.title("Prévision de la demande")

st.markdown(
    """
    <div class="description">
        Estimation de la demande future d'un article
        à partir de son historique récent de ventes.
    </div>
    """,
    unsafe_allow_html=True
)


# Paramètres de prévision

st.markdown(
    '<div class="section-title">Paramètres de prévision</div>',
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
            "Le modèle actuel utilise les magasins "
            "identifiés de 1 à 10."
        )
    )

    item = st.number_input(
        "Identifiant de l'article",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help=(
            "Le modèle actuel utilise les articles "
            "identifiés de 1 à 50."
        )
    )


with col2:

    date_prevision = st.date_input(
        "Date de prévision"
    )


st.caption(
    "Périmètre actuel du modèle : 10 magasins et 50 articles."
)


# Historique des ventes

st.markdown(
    '<div class="section-title">Historique des ventes</div>',
    unsafe_allow_html=True
)

st.info(
    "Saisissez exactement 30 valeurs de ventes, "
    "de la plus ancienne à la plus récente. "
    "La dernière valeur correspond à la vente la plus récente."
)


default_history = (
    "27, 25, 23, 24, 26, 28, 27, 25, 23, 21, "
    "22, 23, 24, 25, 27, 26, 24, 23, 22, 21, "
    "23, 25, 27, 28, 26, 25, 24, 20, 21, 22"
)


history_input = st.text_area(
    "Ventes des 30 derniers jours",
    value=default_history,
    height=130,
    placeholder="Exemple : 20, 22, 18, 25, ...",
    help=(
        "Séparez les valeurs par des virgules. "
        "La dernière valeur doit être la plus récente."
    )
)


# Bouton de prévision

st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "Calculer la prévision",
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
                "Les valeurs de ventes ne peuvent pas être négatives."
            )

            st.stop()


        # Adresse de l'API

        url = (
            "https://prevision-demande-article.onrender.com"
            "/predict"
        )


        # Données envoyées à l'API

        payload = {
            "store": int(store),
            "item": int(item),
            "date_prevision": str(date_prevision),
            "historique_ventes": historique_ventes
        }


        # Appel de l'API

        with st.spinner(
            "Calcul de la prévision en cours..."
        ):

            response = requests.post(
                url,
                json=payload,
                timeout=60
            )


        # Traitement de la réponse

        if response.status_code == 200:

            resultat = response.json()

            demande_prevue = resultat["demande_prevue"]


            st.success(
                "Prévision calculée avec succès."
            )


            # Résultat principal

            st.markdown(
                '<div class="section-title">Résultat</div>',
                unsafe_allow_html=True
            )

            st.metric(
                label="Demande prévue",
                value=f"{demande_prevue} unités"
            )


            # Informations de la prévision

            col1, col2, col3 = st.columns(3)


            with col1:

                st.caption("Magasin")

                st.write(
                    resultat["store"]
                )


            with col2:

                st.caption("Article")

                st.write(
                    resultat["item"]
                )


            with col3:

                st.caption("Date de prévision")

                st.write(
                    resultat["date_prevision"]
                )


        else:

            st.error(
                f"Erreur lors de la communication avec l'API "
                f"(code {response.status_code})."
            )

            try:

                erreur = response.json()

                if isinstance(erreur, dict):

                    if "detail" in erreur:

                        st.warning(
                            erreur["detail"]
                        )

                    else:

                        st.json(erreur)

                else:

                    st.write(erreur)

            except Exception:

                st.write(response.text)


    except ValueError:

        st.error(
            "Les ventes doivent être saisies sous forme de nombres "
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