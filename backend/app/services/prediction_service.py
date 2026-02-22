import joblib
from app.services.feature_engineering import (
    compute_engagement_score
)

model = joblib.load("ml/burnout_model.pkl")

def predict_student(db, student_id):

    engagement = compute_engagement_score(db, student_id)

    # Add other features here
    features = [[engagement]]

    prediction = model.predict(features)[0]

    return prediction