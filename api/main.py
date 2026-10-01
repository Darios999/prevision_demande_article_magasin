from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Chemin vers le dossier principal du projet
BASE_DIR = Path(__file__).resolve().parent.parent


# Chemin vers le modèle enregistré
CHEMIN_MODELE = (
    BASE_DIR
    / "models"
    / "modele_demande_random_forest.joblib"
)


# Chargement du modèle
try:
    modele = joblib.load(
        CHEMIN_MODELE,
        mmap_mode="r"
    )
except Exception as erreur:
    modele = None
    erreur_chargement = str(erreur)


# Création de l'application FastAPI
app = FastAPI(
    title="API de prévision de la demande",
    description=(
        "API permettant de prévoir la demande à partir "
        "d'un historique de ventes."
    ),
    version="1.0.0"
)


# Structure des données reçues par l'API
class DonneesPrediction(BaseModel):
    date_prevision: str
    historique_ventes: list[float]


# Création des variables nécessaires au modèle
def creer_variables(date_prevision, historique_ventes):
    """
    Prépare les variables utilisées par le modèle
    à partir de la date et de l'historique des ventes.
    """

    # Le modèle a besoin d'au moins 30 observations
    if len(historique_ventes) < 30:
        raise ValueError(
            "Au moins 30 valeurs de ventes sont nécessaires."
        )

    # Les ventes négatives ne sont pas acceptées
    if any(
        valeur < 0
        for valeur in historique_ventes
    ):
        raise ValueError(
            "Les valeurs de ventes ne peuvent pas être négatives."
        )

    # Conversion de la date reçue en date exploitable
    try:
        date = pd.to_datetime(
            date_prevision
        )
    except Exception:
        raise ValueError(
            "La date de prévision est invalide."
        )

    # On utilise l'historique dans l'ordre
    # ancienne valeur -> valeur la plus récente
    historique = pd.Series(
        historique_ventes,
        dtype="float64"
    )

    # La dernière valeur correspond donc à la vente
    # la plus récente disponible
    derniere_vente = historique.iloc[-1]

    # Création des variables demandées par le modèle
    variables = {
        "month": date.month,
        "day_of_week": date.dayofweek,

        "sales_lag_1": historique.iloc[-1],

        "sales_lag_7": historique.iloc[-7],

        "sales_lag_14": historique.iloc[-14],

        # Moyenne des 7 dernières ventes
        "rolling_mean_7": historique.tail(7).mean(),

        # Moyenne des 14 dernières ventes
        "rolling_mean_14": historique.tail(14).mean(),

        # Moyenne des 30 dernières ventes
        "rolling_mean_30": historique.tail(30).mean()
    }

    # Transformation en DataFrame pour le modèle
    donnees = pd.DataFrame(
        [variables]
    )

    return donnees


# Page d'accueil de l'API
@app.get("/")
def accueil():
    return {
        "message": "API de prévision de la demande",
        "statut": "fonctionnelle"
    }


# Vérification de l'état de l'API
@app.get("/health")
def health():
    if modele is None:
        return {
            "statut": "erreur",
            "modele_charge": False,
            "message": (
                "Le modèle n'a pas pu être chargé."
            )
        }

    return {
        "statut": "ok",
        "modele_charge": True
    }


# Endpoint permettant d'effectuer une prévision
@app.post("/predict")
def predire(donnees: DonneesPrediction):

    # Vérification du chargement du modèle
    if modele is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Le modèle n'est pas disponible sur le serveur."
            )
        )

    try:

        # Création des variables à partir
        # des données envoyées par Streamlit
        variables = creer_variables(
            donnees.date_prevision,
            donnees.historique_ventes
        )

        # Ordre exact des variables utilisées
        # lors de l'entraînement du modèle
        variables = variables[
            [
                "month",
                "day_of_week",
                "sales_lag_1",
                "sales_lag_7",
                "sales_lag_14",
                "rolling_mean_7",
                "rolling_mean_14",
                "rolling_mean_30"
            ]
        ]

        # Réalisation de la prévision
        prediction = modele.predict(
            variables
        )

        # Récupération de la valeur prédite
        demande_prevue = float(
            prediction[0]
        )

        # Une demande ne peut pas être négative
        demande_prevue = max(
            0,
            demande_prevue
        )

        # Réponse envoyée à Streamlit
        return {
            "date_prevision": donnees.date_prevision,
            "demande_prevue": demande_prevue
        }

    except ValueError as erreur:

        raise HTTPException(
            status_code=400,
            detail=str(erreur)
        )

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Erreur lors de la prévision : {erreur}"
            )
        )