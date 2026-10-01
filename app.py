import base64
import requests
import pandas as pd
from pathlib import Path
import streamlit as st


# Configuration de la page
st.set_page_config(
    page_title="Prévision de la demande",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Adresse de l'API
API_URL = "https://TON-LIEN-API.onrender.com/predict"


# Chemin vers l'image de fond
DOSSIER_PROJET = Path(__file__).resolve().parent
CHEMIN_FOND = DOSSIER_PROJET / "assets" / "fond_magasin.jpg"


# Préparation de l'image de fond
if CHEMIN_FOND.exists():
    with open(CHEMIN_FOND, "rb") as fichier:
        image_base64 = base64.b64encode(fichier.read()).decode()
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

    /* Styling des cartes natives Streamlit */
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
    input, textarea {{
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
    input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {{
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

    /* Message */
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
        .hero {{ padding-top: 25px; }}
        .hero h1 {{ font-size: 36px; }}
        .hero p {{ font-size: 16px; }}
        .resultat-valeur {{ font-size: 38px; }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# Affiche un message d'information
def afficher_message(message):
    st.markdown(
        f"""
        <div class="message">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# Vérifie l'historique des ventes
def verifier_historique(historique):
    if len(historique) < 30:
        afficher_message(
            f"L'historique contient {len(historique)} valeurs. "
            "Au moins 30 jours de ventes sont nécessaires."
        )
        return False

    if any(valeur < 0 for valeur in historique):
        afficher_message("Les valeurs de ventes ne peuvent pas être négatives.")
        return False

    return True


# Transforme le texte saisi en liste de nombres
def convertir_historique(texte):
    valeurs = []
    texte = texte.replace(";", ",")
    for valeur in texte.split(","):
        valeur = valeur.strip()
        if valeur:
            valeurs.append(float(valeur))
    return valeurs


# Appelle l'API pour effectuer la prévision
def appeler_api(date_prevision, historique):
    donnees = {
        "date_prevision": str(date_prevision),
        "historique_ventes": historique
    }

    try:
        reponse = requests.post(API_URL, json=donnees, timeout=60)

        if reponse.status_code == 200:
            return reponse.json()

        try:
            detail = reponse.json().get("detail", "Erreur lors de la prévision.")
        except Exception:
            detail = "L'API a retourné une réponse inattendue."

        afficher_message(f"Impossible d'effectuer la prévision : {detail}")
        return None

    except requests.exceptions.Timeout:
        afficher_message("Le délai de réponse de l'API est dépassé. Veuillez réessayer.")
        return None
    except requests.exceptions.ConnectionError:
        afficher_message("Impossible de joindre l'API. Vérifiez que le service est disponible.")
        return None
    except requests.exceptions.RequestException as erreur:
        afficher_message(f"Erreur de communication avec l'API : {erreur}")
        return None


# Affiche le résultat de la prévision
def afficher_resultat(resultat):
    if resultat is None:
        return

    demande = resultat.get("demande_prevue")
    date_prevision = resultat.get("date_prevision")

    if demande is None:
        afficher_message("La réponse de l'API ne contient pas de prévision.")
        return

    st.markdown(
        f"""
        <div class="resultat">
            <div class="resultat-titre">📊 Résultat de la prévision</div>
            <div class="resultat-valeur">{float(demande):.0f} unités</div>
            <div class="resultat-date">Demande prévue pour le {date_prevision}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Lit le fichier importé
def lire_fichier(fichier):
    if fichier.name.lower().endswith(".csv"):
        return pd.read_csv(fichier)
    return pd.read_excel(fichier)


# En-tête de l'application
st.markdown(
    """
    <div class="hero">
        <h1>Prévision de la <span>demande</span></h1>
        <p>Estimez la demande future à partir de l'historique des ventes et accompagnez la prise de décision en magasin.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# Choix du mode de saisie
with st.container(border=True):
    st.markdown("### Données de prévision")
    st.markdown('<div class="carte-desc">Choisissez comment fournir les données historiques nécessaires à la prévision.</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Mode de saisie",
        ["Saisie manuelle", "Importer un fichier"],
        horizontal=True,
        label_visibility="collapsed"
    )


# Mode de saisie manuelle
if mode == "Saisie manuelle":

    with st.container(border=True):
        st.markdown("### Date de prévision")
        st.markdown('<div class="carte-desc">Sélectionnez la date pour laquelle vous souhaitez obtenir une estimation de la demande.</div>', unsafe_allow_html=True)
        date_prevision = st.date_input("Date de prévision", label_visibility="collapsed")

    with st.container(border=True):
        st.markdown("### Historique des ventes")
        st.markdown('<div class="carte-desc">Saisissez au minimum les 30 dernières ventes, de la plus ancienne à la plus récente.</div>', unsafe_allow_html=True)
        texte_historique = st.text_area(
            "Ventes historiques",
            height=180,
            placeholder="Exemple : 25, 31, 28, 35, 30, ...",
            label_visibility="collapsed"
        )

    if st.button("Calculer la prévision"):
        if not texte_historique.strip():
            afficher_message("Veuillez saisir l'historique des ventes.")
        else:
            try:
                historique = convertir_historique(texte_historique)
                if verifier_historique(historique):
                    historique = historique[-30:]
                    resultat = appeler_api(date_prevision, historique)
                    afficher_resultat(resultat)
            except ValueError:
                afficher_message("Veuillez saisir uniquement des nombres séparés par des virgules.")


# Mode d'importation
else:

    with st.container(border=True):
        st.markdown("### Importer les données")
        st.markdown('<div class="carte-desc">Importez un fichier CSV ou Excel contenant les dates et les ventes historiques.</div>', unsafe_allow_html=True)
        fichier = st.file_uploader(
            "Sélectionner un fichier",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed"
        )

    if fichier is not None:
        try:
            df = lire_fichier(fichier)

            if df.empty:
                afficher_message("Le fichier importé est vide.")
            else:
                colonnes = list(df.columns)
                col1, col2 = st.columns(2)

                with col1:
                    colonne_date = st.selectbox("Colonne de date", colonnes)

                with col2:
                    colonne_ventes = st.selectbox("Colonne des ventes", colonnes)

                try:
                    donnees = df[[colonne_date, colonne_ventes]].copy()

                    donnees[colonne_date] = pd.to_datetime(donnees[colonne_date], errors="coerce")
                    donnees[colonne_ventes] = pd.to_numeric(donnees[colonne_ventes], errors="coerce")

                    donnees = donnees.dropna(subset=[colonne_date, colonne_ventes])
                    donnees = donnees.sort_values(colonne_date)

                    if len(donnees) < 30:
                        afficher_message("Le fichier doit contenir au moins 30 observations de ventes.")
                    else:
                        historique = donnees[colonne_ventes].tail(30).astype(float).tolist()

                        derniere_date = donnees[colonne_date].iloc[-1]
                        date_suggeree = (derniere_date + pd.Timedelta(days=1)).date()

                        date_prevision = st.date_input("Date de prévision", value=date_suggeree)

                        afficher_message("Les 30 dernières observations du fichier seront utilisées pour la prévision.")

                        if st.button("Calculer la prévision", key="bouton_import"):
                            if verifier_historique(historique):
                                resultat = appeler_api(date_prevision, historique)
                                afficher_resultat(resultat)

                except Exception:
                    afficher_message("Impossible d'interpréter les colonnes sélectionnées.")

        except Exception as erreur:
            afficher_message(f"Impossible de lire le fichier : {erreur}")


# Pied de page
st.markdown(
    """
    <div class="pied-page">
        Application de prévision de la demande
    </div>
    """,
    unsafe_allow_html=True
)