import joblib

from app.services.feature_engineering import build_feature_vector
from app.ai_engine.fatigue_detector import detect_moral_fatigue
from app.models.student_prediction import StudentPrediction
from app.models.moral_fatigue_record import MoralFatigueRecord


model = joblib.load("ml/burnout_model.pkl")


def run_behavioral_pipeline(db, student_id, course_id):

    # 1️⃣ Build feature vector
    features = build_feature_vector(db, student_id, course_id)

    # 2️⃣ Run ML Prediction
    prediction = model.predict([features])[0]
    try:
        prob = model.predict_proba([features])[0]
        burnout_prob = float(prob[2] if len(prob) > 2 else prob[-1])
    except Exception:
        burnout_prob = 0.85 if int(prediction) == 2 else (0.50 if int(prediction) == 1 else 0.15)

    prediction_record = StudentPrediction(
        student_id=student_id,
        course_id=course_id,
        academic_mastery=features[0],
        engagement_score=features[1],
        attendance_rate=features[2],
        engagement_trend=features[3],
        performance_trend=features[4],
        attendance_trend=features[5],
        risk_level=int(prediction),
        burnout_probability=burnout_prob
    )

    db.add(prediction_record)

    # 3️⃣ Run Moral Fatigue Detection
    fatigue_result = detect_moral_fatigue(db, student_id, course_id)

    fatigue_record = MoralFatigueRecord(
        student_id=student_id,
        course_id=course_id,
        fatigue_score=fatigue_result["fatigue_score"],
        fatigue_level=fatigue_result["fatigue_level"]
    )

    db.add(fatigue_record)

    db.commit()

    return {
        "risk_level": int(prediction),
        "fatigue_level": fatigue_result["fatigue_level"],
        "fatigue_score": fatigue_result["fatigue_score"]
    }