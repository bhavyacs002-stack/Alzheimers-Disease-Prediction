
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

# Load dataset
df = pd.read_csv("alzheimers_disease_data.csv")

# Input features
FEATURES = [
    "Age", "Gender", "Ethnicity", "BMI", "Smoking",
    "AlcoholConsumption", "PhysicalActivity", "DietQuality",
    "FamilyHistoryAlzheimers", "CardiovascularDisease",
    "Diabetes", "Depression", "HeadInjury", "Hypertension",
    "MemoryComplaints", "BehavioralProblems", "Confusion",
    "Disorientation", "DifficultyCompletingTasks", "Forgetfulness"
]

TARGET = "Diagnosis"

# Prepare data
X = df[FEATURES].apply(pd.to_numeric, errors="raise")
y = df[TARGET]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Scale for Logistic Regression
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Class imbalance ratio
class_ratio = (
    (y_train == 0).sum() / (y_train == 1).sum()
)

# Create models
models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42
    ),

    "LightGBM": LGBMClassifier(
        class_weight="balanced",
        random_state=42,
        verbose=-1
    ),

    "XGBoost": XGBClassifier(
        eval_metric="logloss",
        random_state=42,
        scale_pos_weight=class_ratio
    ),

    "CatBoost": CatBoostClassifier(
        auto_class_weights="Balanced",
        random_state=42,
        verbose=0
    )
}

# Train and save models
os.makedirs("models", exist_ok=True)

for name, model in models.items():

    print(f"Training {name}...")

    if name == "Logistic Regression":
        model.fit(X_train_scaled, y_train)
    else:
        model.fit(X_train, y_train)

    print(f"{name} completed!")

# Save all trained models
joblib.dump(models, "models/all_models.joblib")

# Save scaler
joblib.dump(scaler, "models/scaler.joblib")

# Save feature names
joblib.dump(FEATURES, "models/features.joblib")

print("\nAll five models trained and saved!")
