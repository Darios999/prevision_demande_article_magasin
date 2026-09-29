import streamlit as st
import requests
from datetime import date

# 1. CONFIGURATION DE LA PAGE

st.set_page_config(
    page_title="Prévision de la demande",
    page_icon="📈",
    layout="wide"
)

# 2. CONFIGURATION DE L'API

API_URL = "http://127.0.0.1:8000"


# 3. TITRE DE L'APPLICATION

st.title("📈 Prévision de la demande")

st.write(
    """
    Cette application permet de prévoir la demande future d'un article
    à partir de son historique récent de ventes.
    
    Les données saisies sont transmises à une API FastAPI qui utilise
    un modèle de Machine Learning pour effectuer la prévision.
    """
)

st.divider()

# 4. INFORMATIONS DU PRODUIT

st.subheader("Informations du produit")

colonne1, colonne2 = st.columns(2)

with colonne1:
    magasin = st.number_input(
        "Identifiant du magasin",
        min_value=1,
        step=1,
        value=1,
        help="Entrez l'identifiant numérique du magasin."
    )

with colonne2:
    article = st.number_input(
        "Identifiant de l'article",
        min_value=1,
        step=1,
        value=1,
        help="Entrez l'identifiant numérique de l'article."
    )

# 5. DATE DE PRÉVISION

st.subheader("📅 Date de prévision")

date_prevision = st.date_input(
    "Sélectionnez la date à prévoir",
    value=date.today(),
    min_value=date.today(),
    help="Choisissez la date pour laquelle vous souhaitez prévoir la demande."
)

# 6. HISTORIQUE DES VENTES

st.subheader("Historique récent des ventes")

st.info(
    """
    **Important :** saisissez au minimum les 30 dernières ventes.
    
    Les valeurs doivent être renseignées **de la plus ancienne à la plus récente**.
    Par exemple, la dernière valeur correspond à la vente la plus récente.
    """
)


# Zone de saisie
historique_texte = st.text_area(
    "Ventes historiques",
    placeholder=(
        "Exemple :\n"
        "18, 21, 20, 24, 19, 25, 27, 22, 23, 26, "
        "24, 28, 30, 27, 25, 29, 31, 30, 28, 32, "
        "33, 29, 31, 35, 34, 36, 33, 37, 39, 40"
    ),
    height=180,
    help=(
        "Séparez les valeurs par des virgules. "
        "Vous pouvez fournir plus de 30 valeurs."
    )
)

# 7. FONCTION DE VALIDATION

def verifier_historique(texte):
    """
    Transforme le texte saisi en liste de ventes
    et vérifie que les valeurs sont valides.
    """

    if not texte.strip():
        return None, "Veuillez saisir l'historique des ventes."

    try:
        valeurs = texte.replace(";", ",").split(",")

        ventes = []

        for valeur in valeurs:

            valeur = valeur.strip()

            if valeur == "":
                continue

            nombre = float(valeur)

            if nombre < 0:
                return (
                    None,
                    "Les ventes ne peuvent pas être négatives."
                )

            ventes.append(nombre)

    except ValueError:
        return (
            None,
            "Certaines valeurs ne sont pas numériques. "
            "Utilisez uniquement des nombres séparés par des virgules."
        )

    if len(ventes) < 30:
        return (
            None,
            f"Vous avez saisi {len(ventes)} valeur(s). "
            "L'API nécessite au minimum 30 valeurs."
        )

    return ventes, None

# 8. BOUTON DE PRÉVISION

st.divider()

lancer_prediction = st.button(
    "🔮 Lancer la prévision",
    type="primary",
    use_container_width=True
)

# 9. TRAITEMENT DE LA PRÉVISION

if lancer_prediction:

    # Validation de l'historique

    historique, erreur = verifier_historique(historique_texte)

    if erreur:
        st.error(erreur)
        st.stop()

    # Préparation des données

    donnees = {
        "store": int(magasin),
        "item": int(article),
        "date_prevision": date_prevision.strftime("%Y-%m-%d"),
        "historique_ventes": historique
    }

    # Appel de l'API FastAPI

    with st.spinner("Calcul de la prévision en cours"):

        try:

            reponse = requests.post(
                f"{API_URL}/predict",
                json=donnees,
                timeout=30
            )


        except requests.exceptions.ConnectionError:

            st.error(
                "Impossible de contacter l'API FastAPI."
            )

            st.warning(
                """
                Vérifiez que votre serveur FastAPI est démarré
                à l'adresse :

                `http://127.0.0.1:8000`
                """
            )

            st.stop()


        except requests.exceptions.Timeout:

            st.error(
                "Le délai d'attente de l'API a été dépassé."
            )

            st.stop()


        except requests.exceptions.RequestException as erreur:

            st.error(
                f"Une erreur de communication avec l'API est survenue : {erreur}"
            )

            st.stop()


    # Traitement de la réponse

    if reponse.status_code == 200:

        resultat = reponse.json()

        demande_prevue = resultat["demande_prevue"]

        # Affichage du résultat

        st.success("Prévision réalisée avec succès.")

        st.subheader("Résultat de la prévision")

        colonne1, colonne2, colonne3 = st.columns(3)

        with colonne1:
            st.metric(
                "Magasin",
                resultat["store"]
            )

        with colonne2:
            st.metric(
                "Article",
                resultat["item"]
            )

        with colonne3:
            st.metric(
                "Demande prévue",
                f"{demande_prevue:.2f}"
            )


        st.info(
            f"""
            Pour l'article **{resultat['item']}**, dans le magasin
            **{resultat['store']}**, la demande prévue pour le
            **{resultat['date_prevision']}** est de :

            ###  {demande_prevue:.2f} unités
            """
        )


        # ----------------------------------------------------
        # Informations complémentaires
        # ----------------------------------------------------

        with st.expander(" Voir les données utilisées"):

            st.write(
                f"**Nombre de ventes historiques :** {len(historique)}"
            )

            st.write(
                f"**Première vente fournie :** {historique[0]}"
            )

            st.write(
                f"**Dernière vente fournie :** {historique[-1]}"
            )

            st.write(
                f"**Date de prévision :** "
                f"{resultat['date_prevision']}"
            )


    else:

        # Erreur retournée par FastAPI

        try:
            detail = reponse.json().get(
                "detail",
                "Une erreur inconnue est survenue."
            )

        except ValueError:
            detail = (
                "L'API a retourné une réponse inattendue."
            )

        st.error(
            f"La prévision n'a pas pu être réalisée.\n\n"
            f"**Détail :** {detail}"
        )