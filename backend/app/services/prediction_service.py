import joblib
import os
from app.services.feature_engineering import build_feature_vector



BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "burnout_model.pkl")
model = joblib.load(MODEL_PATH)


def predict_student(db, student_id, course_id):

    features = build_feature_vector(db, student_id, course_id)

    prediction = model.predict([features])[0]

    return {
        "features": features,
        "risk_level": int(prediction)
    }