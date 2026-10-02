import base64
import requests
import pandas as pd
from pathlib import Path
import streamlit as st
from datetime import date,timedelt


# Configuration de la page

st.set_page_config(
    page_title="Prévision de la demande",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Adresse de l'API

API_URL = "https://prevision-demande-article.onrender.com/predict"


# Chemin vers l'image de fond

DOSSIER_PROJET = Path(__file__).resolve().parent
CHEMIN_FOND = DOSSIER_PROJET / "assets" / "fond_magasin.jpg"


# Préparation de l'image de fond

if CHEMIN_FOND.exists():

    with open(CHEMIN_FOND, "rb") as fichier:
        image_base64 = base64.b64encode(
            fichier.read()
        ).decode()

    fond = f"url('data:image/jpeg;base64,{image_base64}')"

else:
    fond = "none"


# Style général de l'application

st.markdown(
    f"""
    <style>

    /* Fond général de l'application */
    .stApp {{
        background-image:
            linear-gradient(
                rgba(5, 18, 35, 0.82),
                rgba(5, 18, 35, 0.90)
            ),
            {fond};

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Zone principale */
    .block-container {{
        max-width: 1050px;
        padding-top: 45px;
        padding-bottom: 55px;
    }}

    /* Titre principal */
    .hero {{
        text-align: center;
        padding: 45px 20px 35px 20px;
    }}

    .hero h1 {{
        color: white;
        font-size: 48px;
        font-weight: 700;
        line-height: 1.15;
        margin-bottom: 15px;
    }}

    .hero h1 span {{
        color: #4da3ff;
    }}

    .hero p {{
        color: #d9e4ef;
        font-size: 18px;
        line-height: 1.6;
        max-width: 720px;
        margin: auto;
    }}

    /* Cartes */
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        background: rgba(8, 24, 42, 0.78) !important;
        border: 1px solid rgba(170, 200, 225, 0.25) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.20) !important;
        backdrop-filter: blur(8px) !important;
    }}

    /* Titres dans les cartes */
    [data-testid="stVerticalBlockBorderWrapper"] h3 {{
        color: white !important;
        font-size: 23px !important;
        font-weight: 650 !important;
        margin-bottom: 8px !important;
        padding: 0 !important;
    }}

    /* Paragraphes de description */
    .carte-desc {{
        color: #cbd8e5;
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 15px;
    }}

    /* Labels */
    label {{
        color: white !important;
        font-weight: 600 !important;
    }}

    /* Champs de texte et zones d'input */
    input,
    textarea {{
        background-color: rgba(18, 32, 50, 0.95) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(160, 190, 215, 0.35) !important;
    }}

    textarea {{
        min-height: 160px !important;
    }}

    /* Sélecteurs */
    div[data-baseweb="select"] > div {{
        background-color: rgba(18, 32, 50, 0.95) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(160, 190, 215, 0.35) !important;
    }}

    /* Focus */
    input:focus,
    textarea:focus,
    div[data-baseweb="select"] > div:focus-within {{
        border-color: #4da3ff !important;
        box-shadow: 0 0 0 1px #4da3ff !important;
    }}

    /* Boutons */
    .stButton > button {{
        width: 100%;
        min-height: 52px;
        border-radius: 12px;
        border: none;
        background-color: #2478c9;
        color: white;
        font-size: 17px;
        font-weight: 650;
        transition: 0.2s;
    }}

    .stButton > button:hover {{
        background-color: #328ce0;
        border: none;
        color: white;
    }}

    /* Bouton radio */
    div[role="radiogroup"] label {{
        color: white !important;
    }}

    /* Zone d'importation */
    [data-testid="stFileUploader"] {{
        background: rgba(15, 31, 49, 0.75);
        border: 1px solid rgba(170, 200, 225, 0.25);
        border-radius: 14px;
        padding: 10px;
    }}

    /* Messages */
    .message {{
        background: rgba(31, 111, 178, 0.18);
        border: 1px solid rgba(77, 163, 255, 0.45);
        border-left: 4px solid #4da3ff;
        border-radius: 10px;
        padding: 14px 17px;
        color: #dcecff;
        font-size: 14px;
        margin: 15px 0;
    }}

    /* Résultat */
    .resultat {{
        background: rgba(8, 24, 42, 0.88);
        border: 1px solid rgba(77, 163, 255, 0.45);
        border-radius: 20px;
        padding: 30px;
        margin-top: 25px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
    }}

    .resultat-titre {{
        color: #dcecff;
        font-size: 22px;
        font-weight: 650;
        margin-bottom: 12px;
    }}

    .resultat-valeur {{
        color: #4da3ff;
        font-size: 46px;
        font-weight: 750;
    }}

    .resultat-date {{
        color: #aebfd0;
        font-size: 15px;
        margin-top: 8px;
    }}

    /* Pied de page */
    .pied-page {{
        text-align: center;
        color: #9fb0c1;
        font-size: 13px;
        margin-top: 45px;
        padding-top: 20px;
        border-top: 1px solid rgba(200, 220, 240, 0.15);
    }}

    /* Responsive */
    @media (max-width: 768px) {{

        .block-container {{
            padding-left: 18px;
            padding-right: 18px;
            padding-top: 25px;
        }}

        .hero {{
            padding-top: 25px;
        }}

        .hero h1 {{
            font-size: 36px;
        }}

        .hero p {{
            font-size: 16px;
        }}

        .resultat-valeur {{
            font-size: 38px;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# Afficher un message

def afficher_message(message):

    st.markdown(
        f"""
        <div class="message">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# Vérifier l'historique des ventes

def verifier_historique(historique):

    # Vérifier le nombre de valeurs
    if len(historique) < 30:

        afficher_message(
            f"L'historique contient {len(historique)} valeurs. "
            "Au moins 30 jours de ventes sont nécessaires."
        )

        return False

    # Vérifier les valeurs négatives
    if any(valeur < 0 for valeur in historique):

        afficher_message(
            "Les valeurs de ventes ne peuvent pas être négatives."
        )

        return False

    return True


# Transformer le texte saisi en liste de nombres

def convertir_historique(texte):

    valeurs = []

    # Accepter également le point-virgule
    texte = texte.replace(";", ",")

    # Séparer les différentes valeurs
    for valeur in texte.split(","):

        valeur = valeur.strip()

        if valeur:
            valeurs.append(float(valeur))

    return valeurs


# Appeler l'API pour effectuer la prévision

def appeler_api(date_prevision, historique):

    donnees = {
        "date_prevision": str(date_prevision),
        "historique_ventes": historique
    }

    try:

        reponse = requests.post(
            API_URL,
            json=donnees,
            timeout=60
        )

        # Si l'API répond correctement
        if reponse.status_code == 200:

            return reponse.json()

        # Essayer de récupérer le message d'erreur de l'API
        try:

            detail = reponse.json().get(
                "detail",
                "Erreur lors de la prévision."
            )

        except Exception:

            detail = "L'API a retourné une réponse inattendue."

        afficher_message(
            f"Impossible d'effectuer la prévision : {detail}"
        )

        return None

    # Délai dépassé
    except requests.exceptions.Timeout:

        afficher_message(
            "Le délai de réponse de l'API est dépassé. "
            "Veuillez réessayer."
        )

        return None

    # API inaccessible
    except requests.exceptions.ConnectionError:

        afficher_message(
            "Impossible de joindre l'API. "
            "Vérifiez que le service est disponible."
        )

        return None

    # Autre erreur de communication
    except requests.exceptions.RequestException as erreur:

        afficher_message(
            f"Erreur de communication avec l'API : {erreur}"
        )

        return None


# Afficher le résultat de la prévision

def afficher_resultat(resultat):

    # Aucun résultat
    if resultat is None:
        return

    # Récupérer les informations retournées par l'API
    demande = resultat.get("demande_prevue")
    date_prevision = resultat.get("date_prevision")

    # Vérifier que la prévision existe
    if demande is None:

        afficher_message(
            "La réponse de l'API ne contient pas de prévision."
        )

        return

    # Afficher le résultat
    st.markdown(f"""
<div class="resultat">
    <div class="resultat-titre">📊 Résultat de la prévision</div>
    <div class="resultat-valeur">{int(float(demande))} unités</div>
    <div class="resultat-date">📅 Demande prévue pour le {date_prevision}</div>
</div>
""", unsafe_allow_html=True)


# Lire le fichier importé

def lire_fichier(fichier):

    # Lire un fichier CSV
    if fichier.name.lower().endswith(".csv"):

        return pd.read_csv(fichier)

    # Lire un fichier Excel
    return pd.read_excel(fichier)


# En-tête de l'application

st.markdown('<div class="hero"><h1>Prévision de la <span>demande</span></h1><p>Estimez la demande future à partir de l\'historique des ventes et accompagnez la prise de décision en magasin. Notez qu\'il s\'agit d\'une prévision à court terme </p></div>', unsafe_allow_html=True)

# Choix du mode de saisie

with st.container(border=True):

    st.markdown("### Données de prévision")

    st.markdown(
        '<div class="carte-desc">'
        'Choisissez comment fournir les données historiques '
        'nécessaires à la prévision.'
        '</div>',
        unsafe_allow_html=True
    )

    mode = st.radio(
        "Mode de saisie",
        [
            "Saisie manuelle",
            "Importer un fichier"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


# Mode de saisie manuelle

if mode == "Saisie manuelle":

    # Date choisie manuellement
    with st.container(border=True):

        st.markdown("### Date de prévision")

        st.markdown(
            '<div class="carte-desc">'
            'Sélectionnez la date pour laquelle vous souhaitez '
            'obtenir une estimation de la demande.'
            '</div>',
            unsafe_allow_html=True
        )

        date_prevision = st.date_input(
            "Date de prévision",
            value=date.today()+timedelta(days=1),
            label_visibility="collapsed"
        )

    # Historique saisi manuellement
    with st.container(border=True):

        st.markdown("### Historique des ventes")

        st.markdown(
            '<div class="carte-desc">'
            'Saisissez au minimum les 30 dernières ventes, '
            'de la plus ancienne à la plus récente.'
            '</div>',
            unsafe_allow_html=True
        )

        texte_historique = st.text_area(
            "Ventes historiques",
            value="25, 28, 31, 27, 30, 34, 29, 32, 35, 33, 31, 36, 38, 35, 37, 40, 39, 42, 41, 44, 43, 45, 47, 46, 49, 48, 51, 50, 53, 52",
            height=180,
            placeholder="Exemple : 25, 31, 28, 35, 30, ...",
            label_visibility="collapsed"
        )

    # Lancer la prévision
    if st.button("Calculer la prévision"):

        # Vérifier que l'utilisateur a saisi quelque chose
        if not texte_historique.strip():

            afficher_message(
                "Veuillez saisir l'historique des ventes."
            )

        else:

            try:

                # Transformer le texte en liste de nombres
                historique = convertir_historique(
                    texte_historique
                )

                # Vérifier l'historique
                if verifier_historique(historique):

                    # Garder les 30 dernières valeurs
                    historique = historique[-30:]

                    # Appeler l'API
                    resultat = appeler_api(
                        date_prevision,
                        historique
                    )

                    # Afficher le résultat
                    afficher_resultat(resultat)

            except ValueError:

                afficher_message(
                    "Veuillez saisir uniquement des nombres "
                    "séparés par des virgules."
                )


# Mode d'importation

else:

    # Zone d'importation
    with st.container(border=True):

        st.markdown("### Importer les données")

        st.markdown(
            '<div class="carte-desc">'
            'Importez un fichier CSV ou Excel contenant les dates '
            'et les ventes historiques.'
            '</div>',
            unsafe_allow_html=True
        )

        fichier = st.file_uploader(
            "Sélectionner un fichier",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed"
        )

    # Vérifier qu'un fichier a été sélectionné
    if fichier is not None:

        try:

            # Lire le fichier
            df = lire_fichier(fichier)

            # Vérifier si le fichier est vide
            if df.empty:

                afficher_message(
                    "Le fichier importé est vide."
                )

            else:

                # Récupérer les colonnes disponibles
                colonnes = list(df.columns)

                # Sélection des colonnes
                col1, col2 = st.columns(2)

                with col1:

                    colonne_date = st.selectbox(
                        "Colonne de date",
                        colonnes
                    )

                with col2:

                    colonne_ventes = st.selectbox(
                        "Colonne des ventes",
                        colonnes
                    )

                # Vérifier que les deux colonnes sont différentes
                if colonne_date == colonne_ventes:

                    afficher_message(
                        "La colonne de date et la colonne des ventes "
                        "doivent être différentes."
                    )

                else:

                    # Conserver uniquement les colonnes nécessaires
                    donnees = df[
                        [colonne_date, colonne_ventes]
                    ].copy()

                    # Convertir les dates
                    donnees[colonne_date] = pd.to_datetime(
                        donnees[colonne_date],
                        errors="coerce"
                    )

                    # Convertir les ventes en nombres
                    donnees[colonne_ventes] = pd.to_numeric(
                        donnees[colonne_ventes],
                        errors="coerce"
                    )

                    # Compter les dates invalides
                    dates_invalides = donnees[
                        colonne_date
                    ].isna().sum()

                    # Compter les ventes invalides
                    ventes_invalides = donnees[
                        colonne_ventes
                    ].isna().sum()

                    # Signaler les dates invalides
                    if dates_invalides > 0:

                        afficher_message(
                            f"Le fichier contient {dates_invalides} "
                            "date(s) invalide(s). "
                            "Veuillez vérifier la colonne de date."
                        )

                    # Signaler les ventes invalides
                    if ventes_invalides > 0:

                        afficher_message(
                            f"Le fichier contient {ventes_invalides} "
                            "valeur(s) de vente invalide(s). "
                            "Veuillez vérifier la colonne des ventes."
                        )

                    # Arrêter si les données contiennent des erreurs
                    if (
                        dates_invalides > 0
                        or ventes_invalides > 0
                    ):

                        st.stop()

                    # Vérifier les ventes négatives
                    if (
                        donnees[colonne_ventes] < 0
                    ).any():

                        afficher_message(
                            "Le fichier contient des valeurs de ventes "
                            "négatives. Les ventes doivent être supérieures "
                            "ou égales à zéro."
                        )

                        st.stop()

                    # Trier les données de la plus ancienne
                    # à la plus récente
                    donnees = donnees.sort_values(
                        colonne_date
                    )

                    # Vérifier qu'il existe suffisamment d'observations
                    if len(donnees) < 30:

                        afficher_message(
                            f"Le fichier contient seulement "
                            f"{len(donnees)} observations. "
                            "Au moins 30 observations de ventes "
                            "sont nécessaires."
                        )

                    else:

                        # Récupérer les 30 dernières ventes
                        historique = (
                            donnees[colonne_ventes]
                            .tail(30)
                            .astype(float)
                            .tolist()
                        )

                        # Déterminer la dernière date disponible
                        # dans le fichier
                        derniere_date = donnees[
                            colonne_date
                        ].iloc[-1]

                        # Calculer automatiquement la date de prévision
                        # comme étant le lendemain de la dernière date
                        date_prevision = (
                            derniere_date
                            + pd.Timedelta(days=1)
                        ).date()

                        # Afficher les informations détectées
                        afficher_message(
                            f"Dernière date disponible dans le fichier : "
                            f"<strong>"
                            f"{derniere_date.strftime('%d/%m/%Y')}"
                            f"</strong><br>"
                            f"Date de prévision : "
                            f"<strong>"
                            f"{date_prevision.strftime('%d/%m/%Y')}"
                            f"</strong>"
                        )

                        # Informer l'utilisateur de l'historique utilisé
                        afficher_message(
                            "Les 30 dernières observations du fichier "
                            "seront utilisées pour effectuer la prévision."
                        )

                        # Bouton de prévision
                        if st.button(
                            "Calculer la prévision",
                            key="bouton_import"
                        ):

                            # Vérifier l'historique
                            if verifier_historique(
                                historique
                            ):

                                # Appeler l'API
                                resultat = appeler_api(
                                    date_prevision,
                                    historique
                                )

                                # Afficher le résultat
                                afficher_resultat(
                                    resultat
                                )

        except Exception as erreur:

            # Gérer les erreurs de lecture du fichier
            afficher_message(
                f"Impossible de lire le fichier : {erreur}"
            )


# Pied de page

st.markdown(
    """
    <div class="pied-page">
        Application de prévision de la demande
    </div>
    """,
    unsafe_allow_html=True
)