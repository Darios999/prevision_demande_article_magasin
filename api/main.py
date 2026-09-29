from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ============================================================
# 1. CHEMIN DU PROJET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "modele_demande_random_forest.joblib"


# ============================================================
# 2. CHARGEMENT DU MODÈLE
# ============================================================

try:
    model = joblib.load(MODEL_PATH)
except Exception as erreur:
    model = None
    print("Erreur lors du chargement du modèle :", erreur)


# ============================================================
# 3. CRÉATION DE L'APPLICATION FASTAPI
# ============================================================

app = FastAPI(
    title="API de prévision de la demande",
    description=(
        "API permettant de prévoir la demande d'un article "
        "dans un magasin à partir de son historique de ventes."
    ),
    version="1.0.0"
)


# ============================================================
# 4. STRUCTURE DES DONNÉES REÇUES
# ============================================================

class DonneesPrediction(BaseModel):
    store: int
    item: int
    date_prevision: str
    historique_ventes: list[float]


# ============================================================
# 5. PAGE D'ACCUEIL
# ============================================================

@app.get("/")
def accueil():
    return {
        "message": "API de prévision de la demande",
        "documentation": "/docs",
        "statut": "active"
    }


# ============================================================
# 6. VÉRIFICATION DE L'API
# ============================================================

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


# ============================================================
# 7. CRÉATION DES VARIABLES DU MODÈLE
# ============================================================

def creer_variables(
    store: int,
    item: int,
    date_prevision: str,
    historique_ventes: list[float]
):

    # Vérification de l'historique
    if len(historique_ventes) < 30:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'historique doit contenir au moins "
                "30 valeurs de ventes."
            )
        )

    # Conversion de la date
    try:
        date = pd.to_datetime(date_prevision)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="La date doit être au format YYYY-MM-DD."
        )

    # Les ventes doivent être dans l'ordre chronologique
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

        # Dernières ventes
        "sales_lag_1": ventes.iloc[-1],
        "sales_lag_7": ventes.iloc[-7],
        "sales_lag_14": ventes.iloc[-14],

        # Moyennes mobiles
        "rolling_mean_7": ventes.iloc[-7:].mean(),
        "rolling_mean_14": ventes.iloc[-14:].mean(),
        "rolling_mean_30": ventes.iloc[-30:].mean()
    }

    return pd.DataFrame([variables])


# ============================================================
# 8. PRÉDICTION
# ============================================================

@app.post("/predict")
def predire(donnees: DonneesPrediction):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Le modèle n'est pas disponible."
        )

    # Création des 13 variables
    donnees_modele = creer_variables(
        store=donnees.store,
        item=donnees.item,
        date_prevision=donnees.date_prevision,
        historique_ventes=donnees.historique_ventes
    )

    # Ordre exact des variables utilisées pendant l'entraînement
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

    # Vérification
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