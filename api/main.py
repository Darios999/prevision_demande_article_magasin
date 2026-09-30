from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Chemin du projet

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "modele_demande_random_forest.joblib"


# Chargement du modèle

try:
    model = joblib.load(MODEL_PATH, mmap_mode="r")
except Exception as erreur:
    model = None
    print("Erreur lors du chargement du modèle :", erreur)


# Création de l'application FastAPI

app = FastAPI(
    title="API de prévision de la demande",
    description=(
        "API permettant de prévoir la demande d'un article "
        "dans un magasin à partir de son historique de ventes."
    ),
    version="1.0.0"
)


# Structure des données reçues

class DonneesPrediction(BaseModel):
    store: int
    item: int
    date_prevision: str
    historique_ventes: list[float]


# Page d'accueil

@app.get("/")
def accueil():
    return {
        "message": "API de prévision de la demande",
        "documentation": "/docs",
        "statut": "active"
    }


# Vérification de l'API

@app.get("/health")
def health():
    if model is None:
        return {
            "status": "error",
            "message": "Le modèle n'a pas pu être chargé."
        }

    return {
        "status": "ok",
        "message": "API et modèle opérationnels."
    }


# Création des variables du modèle

def creer_variables(
    store: int,
    item: int,
    date_prevision: str,
    historique_ventes: list[float]
):

    # Vérification du magasin

    if store < 1 or store > 10:
        raise HTTPException(
            status_code=400,
            detail="Le magasin doit être compris entre 1 et 10."
        )

    # Vérification de l'article

    if item < 1 or item > 50:
        raise HTTPException(
            status_code=400,
            detail="L'article doit être compris entre 1 et 50."
        )

    # Vérification de l'historique

    if len(historique_ventes) < 30:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'historique doit contenir au moins "
                "30 jours de ventes."
            )
        )

    # Vérification des valeurs de ventes

    if any(vente < 0 for vente in historique_ventes):
        raise HTTPException(
            status_code=400,
            detail="Les valeurs de ventes ne peuvent pas être négatives."
        )

    # Conversion de la date

    try:
        date = pd.to_datetime(date_prevision)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="La date doit être au format YYYY-MM-DD."
        )

    # Conversion de l'historique en série pandas

    ventes = pd.Series(historique_ventes, dtype=float)

    # Création des variables

    variables = {
        "store": store,
        "item": item,
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "day_of_week": date.dayofweek,
        "week": int(date.isocalendar().week),

        "sales_lag_1": ventes.iloc[-1],
        "sales_lag_7": ventes.iloc[-7],
        "sales_lag_14": ventes.iloc[-14],

        "rolling_mean_7": ventes.iloc[-7:].mean(),
        "rolling_mean_14": ventes.iloc[-14:].mean(),
        "rolling_mean_30": ventes.iloc[-30:].mean()
    }

    return pd.DataFrame([variables])


# Prédiction

@app.post("/predict")
def predire(donnees: DonneesPrediction):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Le modèle n'est pas disponible."
        )

    # Création des variables

    donnees_modele = creer_variables(
        store=donnees.store,
        item=donnees.item,
        date_prevision=donnees.date_prevision,
        historique_ventes=donnees.historique_ventes
    )

    # Variables utilisées pendant l'entraînement

    features = [
        "store",
        "item",
        "year",
        "month",
        "day",
        "day_of_week",
        "week",
        "sales_lag_1",
        "sales_lag_7",
        "sales_lag_14",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_30"
    ]

    # Vérification de l'ordre des variables

    donnees_modele = donnees_modele[features]

    # Prédiction

    prediction = model.predict(donnees_modele)[0]

    # Une demande négative n'a pas de sens

    prediction = max(0, prediction)

    return {
        "store": donnees.store,
        "item": donnees.item,
        "date_prevision": donnees.date_prevision,
        "demande_prevue": round(float(prediction), 2)
    }