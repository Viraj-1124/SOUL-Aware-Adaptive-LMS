def get_recommendation(probability: float) -> tuple[str, str]:
    """
    Given a probability of correctly answering the next question (or overall mastery),
    return a recommendation level and an action item.
    """
    if probability > 0.7:
        return "Advanced", "Proceed to advanced topics or complex problem sets."
    elif probability < 0.3:
        return "Remediation", "Review prerequisite materials and fundamental concepts."
    else:
        return "Normal", "Continue with standard curriculum progression."

def determine_mastery_level(bkt_prob: float, lstm_prob: float) -> str:
    """
    Combine BKT and LSTM probabilities to determine a mastery level label.
    """
    # Simple average for now
    avg_prob = (bkt_prob + lstm_prob) / 2.0
    
    if avg_prob >= 0.8:
        return "Mastered"
    elif avg_prob >= 0.5:
        return "Intermediate"
    else:
        return "Beginner"
