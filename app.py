import streamlit as st
import requests
import pandas as pd


# Configuration de la page

st.set_page_config(
    page_title="Prévision de la demande d’articles en magasin",
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


# Choix du mode de saisie

st.markdown(
    '<div class="section-title">Source des données</div>',
    unsafe_allow_html=True
)

mode_saisie = st.radio(
    "Choisissez une méthode",
    [
        "Charger un fichier CSV",
        "Saisir manuellement"
    ]
)


historique_ventes = None


# Mode 1 : chargement du fichier CSV

if mode_saisie == "Charger un fichier CSV":

    fichier = st.file_uploader(
        "Sélectionnez le fichier CSV",
        type=["csv"],
        help=(
            "Le fichier doit contenir les colonnes : "
            "date, store, item et sales."
        )
    )

    if fichier is not None:

        try:

            # Lecture du fichier CSV

            df = pd.read_csv(fichier)

            # Nettoyage des noms de colonnes

            df.columns = df.columns.str.strip()

            colonnes_requises = [
                "date",
                "store",
                "item",
                "sales"
            ]

            # Vérification des colonnes

            colonnes_manquantes = [
                colonne
                for colonne in colonnes_requises
                if colonne not in df.columns
            ]

            if colonnes_manquantes:

                st.error(
                    "Le fichier ne contient pas toutes les colonnes "
                    "nécessaires."
                )

                st.write(
                    "Colonnes manquantes : "
                    + ", ".join(colonnes_manquantes)
                )

                st.stop()

            # Conversion de la date

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

            # Conversion des identifiants

            df["store"] = pd.to_numeric(
                df["store"],
                errors="coerce"
            )

            df["item"] = pd.to_numeric(
                df["item"],
                errors="coerce"
            )

            # Conversion des ventes

            df["sales"] = pd.to_numeric(
                df["sales"],
                errors="coerce"
            )

            # Suppression des lignes invalides

            df = df.dropna(
                subset=[
                    "date",
                    "store",
                    "item",
                    "sales"
                ]
            )

            # Vérification des ventes négatives

            if (df["sales"] < 0).any():

                st.error(
                    "Le fichier contient des valeurs de ventes négatives."
                )

                st.stop()

            # Conversion des identifiants en entiers

            df["store"] = df["store"].astype(int)
            df["item"] = df["item"].astype(int)

            # Filtrage selon le magasin et l'article sélectionnés

            df_filtre = df[
                (df["store"] == int(store))
                &
                (df["item"] == int(item))
            ].copy()

            # Vérification de l'existence du couple magasin/article

            if df_filtre.empty:

                st.error(
                    f"Aucune donnée trouvée pour le magasin {int(store)} "
                    f"et l'article {int(item)}."
                )

                st.stop()

            # Tri des données par date

            df_filtre = df_filtre.sort_values(
                "date"
            )

            # Suppression des éventuels doublons

            df_filtre = df_filtre.drop_duplicates(
                subset=[
                    "date",
                    "store",
                    "item"
                ],
                keep="last"
            )

            # Conservation des 30 dernières observations

            df_30 = df_filtre.tail(30).copy()

            # Vérification du nombre d'observations

            if len(df_30) < 30:

                st.error(
                    f"Seulement {len(df_30)} observations sont disponibles "
                    "pour ce magasin et cet article. "
                    "Il faut au minimum 30 observations."
                )

                st.stop()

            # Création de l'historique des ventes

            historique_ventes = (
                df_30["sales"]
                .astype(float)
                .tolist()
            )

            st.success(
                "Les 30 dernières observations ont été récupérées "
                "avec succès."
            )

            # Informations sur les données utilisées

            col1, col2, col3 = st.columns(3)

            with col1:

                st.caption("Observations")

                st.write(len(historique_ventes))

            with col2:

                st.caption("Dernière date disponible")

                st.write(
                    df_30["date"].max().strftime("%d/%m/%Y")
                )

            with col3:

                st.caption("Magasin / Article")

                st.write(
                    f"{int(store)} / {int(item)}"
                )

            # Affichage de l'historique

            with st.expander(
                "Voir les 30 dernières ventes"
            ):

                historique_affichage = df_30[
                    [
                        "date",
                        "store",
                        "item",
                        "sales"
                    ]
                ].copy()

                historique_affichage["date"] = (
                    historique_affichage["date"]
                    .dt.strftime("%d/%m/%Y")
                )

                st.dataframe(
                    historique_affichage,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as erreur:

            st.error(
                f"Impossible de lire le fichier CSV : {erreur}"
            )


# Mode 2 : saisie manuelle

else:

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

    try:

        # Conversion du texte en liste de nombres

        historique_ventes = [
            float(x.strip())
            for x in history_input.split(",")
            if x.strip()
        ]

        # Vérification du nombre de valeurs

        if len(historique_ventes) != 30:

            st.warning(
                f"Vous avez actuellement {len(historique_ventes)} valeurs. "
                "L'historique doit contenir exactement 30 valeurs."
            )

            historique_ventes = None

        # Vérification des valeurs négatives

        elif any(
            vente < 0
            for vente in historique_ventes
        ):

            st.error(
                "Les valeurs de ventes ne peuvent pas être négatives."
            )

            historique_ventes = None

    except ValueError:

        st.error(
            "Les ventes doivent être saisies sous forme de nombres "
            "séparés par des virgules."
        )

        historique_ventes = None


# Bouton de prévision

st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "Calculer la prévision",
    use_container_width=True
):

    # Vérification de l'historique avant l'envoi à l'API

    if historique_ventes is None:

        st.error(
            "Veuillez fournir un historique valide de 30 ventes."
        )

        st.stop()

    try:

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

            demande_prevue = resultat[
                "demande_prevue"
            ]

            st.success(
                "Prévision calculée avec succès."
            )

            # Résultat principal

            st.markdown(
                '<div class="section-title">Résultat</div>',
                unsafe_allow_html=True
            )

            st.metric(
                label="Demande prévue pour le lendemain",
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

                st.write(
                    response.text
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

    except requests.exceptions.RequestException as erreur:

        st.error(
            f"Une erreur est survenue lors de l'appel à l'API : {erreur}"
        )

    except Exception as erreur:

        st.error(
            f"Une erreur inattendue est survenue : {erreur}"
        )