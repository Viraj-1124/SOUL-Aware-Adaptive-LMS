import joblib
from app.services.feature_engineering import build_feature_vector

model = joblib.load("ml/burnout_model.pkl")


def predict_student(db, student_id, course_id):

    features = build_feature_vector(db, student_id, course_id)

    prediction = model.predict([features])[0]

    return {
        "features": features,
        "risk_level": int(prediction)
    }