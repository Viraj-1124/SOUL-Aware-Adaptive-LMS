def classify_risk(health_index: float):
    if health_index >= 75:
        return 0  # Optimal
    elif health_index >= 50:
        return 1  # Disengaged
    else:
        return 2  # Burnout Risk