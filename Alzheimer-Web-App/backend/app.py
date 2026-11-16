
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import pandas as pd
import joblib
import os
import numpy as np
import sqlite3
import re
from datetime import timedelta

# -----------------------------------
# 1. Initialize Flask application
# -----------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key-change-before-deployment"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_PATH="/",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)

# CORS configuration
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    },
    supports_credentials=True
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# -----------------------------------
# 2. Database configuration
# -----------------------------------

DATABASE = os.path.join(BASE_DIR, "users.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_users_table():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


create_users_table()


# -----------------------------------
# 3. Login protection decorator
# -----------------------------------

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "error": "Please log in to access this feature."
            }), 401

        return function(*args, **kwargs)

    return decorated_function


# -----------------------------------
# 4. Load trained ML models
# -----------------------------------

MODEL_PATH = os.path.join(BASE_DIR, "models")

models = joblib.load(
    os.path.join(MODEL_PATH, "all_models.joblib")
)

scaler = joblib.load(
    os.path.join(MODEL_PATH, "scaler.joblib")
)

FEATURES = joblib.load(
    os.path.join(MODEL_PATH, "features.joblib")
)


# -----------------------------------
# 5. Home route
# -----------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Alzheimer's Prediction API is running!",
        "status": "success"
    })


# -----------------------------------
# 6. User Signup
# -----------------------------------

@app.route("/signup", methods=["POST"])
def signup():

    try:

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "success": False,
                "message": "Invalid request data"
            }), 400

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not name or not email or not password:

            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        if len(name) > 100:

            return jsonify({
                "success": False,
                "message": "Name is too long"
            }), 400

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        ):

            return jsonify({
                "success": False,
                "message": "Enter a valid email address"
            }), 400

        if len(password) < 8:

            return jsonify({
                "success": False,
                "message": "Password must contain at least 8 characters"
            }), 400

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:

            connection.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return jsonify({
                "success": False,
                "message": "An account with this email already exists"
            }), 409

        connection.close()

        return jsonify({
            "success": True,
            "message": "Account created successfully. Please log in."
        }), 201

    except Exception as error:

        app.logger.exception("Signup error")

        return jsonify({
            "success": False,
            "message": "Unable to create account"
        }), 500


# -----------------------------------
# 7. User Login
# -----------------------------------

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "success": False,
                "message": "Invalid request data"
            }), 400

        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        connection = get_db_connection()

        user = connection.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,)).fetchone()

        connection.close()

        if user is None or not check_password_hash(
            user["password"], password
        ):

            return jsonify({
                "success": False,
                "message": "Incorrect email or password"
            }), 401

        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        session.permanent = True

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception:

        app.logger.exception("Login error")

        return jsonify({
            "success": False,
            "message": "Unable to log in"
        }), 500


# -----------------------------------
# 8. Check Login Status
# -----------------------------------

@app.route("/me", methods=["GET"])
def current_user():

    if "user_id" not in session:

        return jsonify({
            "authenticated": False,
            "message": "User is not logged in"
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": session["user_id"],
            "name": session["user_name"],
            "email": session["user_email"]
        }
    })


# -----------------------------------
# 9. User Logout
# -----------------------------------

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


# -----------------------------------
# 10. Protected Prediction Route
# -----------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "success": False,
                "error": "Invalid patient information"
            }), 400

        missing = [
            feature for feature in FEATURES
            if feature not in data
        ]

        if missing:

            return jsonify({
                "success": False,
                "error": "Missing input fields",
                "missing_fields": missing
            }), 400

        values = []

        for feature in FEATURES:

            value = float(data[feature])

            if not np.isfinite(value):

                raise ValueError(
                    f"Invalid value for {feature}"
                )

            values.append(value)

        patient = pd.DataFrame(
            [values],
            columns=FEATURES
        )

        results = {}

        # Run all five machine learning models
        for name, model in models.items():

            if name == "Logistic Regression":

                model_input = scaler.transform(patient)

            else:

                model_input = patient

            prediction = int(
                model.predict(model_input)[0]
            )

            probabilities = model.predict_proba(
                model_input
            )[0]

            positive_index = list(
                model.classes_
            ).index(1)

            positive_probability = float(
                probabilities[positive_index]
            )

            results[name] = {

                "prediction": prediction,

                "result": (
                    "Positive prediction"
                    if prediction == 1
                    else "Negative prediction"
                ),

                "positive_probability": round(
                    positive_probability * 100, 2
                )
            }

        return jsonify({

            "success": True,

            "predictions": results,

            "notice": (
                "Educational prediction only. "
                "This is not a medical diagnosis."
            )

        })

    except (ValueError, TypeError, KeyError) as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception:

        app.logger.exception("Prediction error")

        return jsonify({
            "success": False,
            "error": "Unable to generate predictions"
        }), 500


# -----------------------------------
# 11. Run Flask application
# -----------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
