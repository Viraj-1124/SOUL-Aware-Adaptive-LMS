"""
model4_context_model.py
Context & Behavior Sub-Model — Model 4 (Purpose & Skill Alignment)
────────────────────────────────────────────────────────────────────
Input  : environment, engagement_score, integrity_score,
         consistency_score, anomaly_score
Output :
    - context_adjustment_score  (float 0–1)
    - learning_mode_hint        (str: 'theory' | 'practice' | 'project')
    - integrity_flag            (bool: True if anomaly detected)
    - scaffold_level            (str: 'low' | 'medium' | 'high')
    - behavior_summary          (str: human-readable)

Context awareness rules:
    online      → theory-first recommendations
    lab         → practice-first recommendations
    project     → project-based recommendations
    self-study  → theory + self-paced

Scaffold fading:
    high mastery (avg > 0.7) → reduce guidance
    low mastery  (avg < 0.4) → increase guidance
"""

import numpy as np

# ── Environment → learning mode mapping ──────────────────────────────────────
ENV_MODE_MAP = {
    "online":     "theory",
    "lab":        "practice",
    "project":    "project",
    "self-study": "theory",
}

# ── Thresholds ────────────────────────────────────────────────────────────────
ANOMALY_THRESHOLD   = 0.25
HIGH_MASTERY_CUTOFF = 0.70
LOW_MASTERY_CUTOFF  = 0.40


def compute_context_adjustment(
    engagement_score: float,
    consistency_score: float,
    integrity_score: float,
    anomaly_score: float,
    environment: str,
) -> float:
    """
    Context adjustment score (0–1).
    High engagement + high consistency + good environment → higher score.
    Anomaly penalises the score.
    """
    env_bonus = {
        "lab":        0.10,
        "project":    0.10,
        "online":     0.05,
        "self-study": 0.00,
    }
    base = (
        0.40 * engagement_score +
        0.30 * consistency_score +
        0.20 * integrity_score +
        0.10 * env_bonus.get(str(environment).lower(), 0.0)
    )
    anomaly_penalty = anomaly_score * 0.15
    score = np.clip(base - anomaly_penalty, 0.0, 1.0)
    return round(float(score), 4)


def get_learning_mode(environment: str) -> str:
    return ENV_MODE_MAP.get(str(environment).lower(), "theory")


def check_integrity_flag(anomaly_score: float) -> bool:
    return float(anomaly_score) > ANOMALY_THRESHOLD


def get_scaffold_level(avg_mastery: float) -> str:
    """
    Returns guidance level based on average mastery.
    Used by decision engine to adjust recommendation tone.
    """
    if avg_mastery >= HIGH_MASTERY_CUTOFF:
        return "low"
    elif avg_mastery <= LOW_MASTERY_CUTOFF:
        return "high"
    else:
        return "medium"


def build_behavior_summary(
    engagement_score: float,
    consistency_score: float,
    environment: str,
    scaffold_level: str,
    integrity_flag: bool,
) -> str:
    """Human-readable summary of student's learning behavior."""
    eng_label  = "high" if engagement_score  > 0.7 else ("moderate" if engagement_score  > 0.4 else "low")
    cons_label = "consistent" if consistency_score > 0.7 else ("moderate" if consistency_score > 0.4 else "inconsistent")

    summary = (
        f"Engagement: {eng_label} ({engagement_score:.2f}) | "
        f"Consistency: {cons_label} ({consistency_score:.2f}) | "
        f"Environment: {environment} | "
        f"Guidance needed: {scaffold_level}"
    )
    if integrity_flag:
        summary += " | ⚠️ Anomalous activity detected — confidence adjusted"
    return summary


def process_context(
    engagement_score: float,
    consistency_score: float,
    integrity_score: float,
    anomaly_score: float,
    environment: str,
    avg_mastery: float,
) -> dict:
    """
    Full context processing for one student.
    Returns all context outputs needed by the decision engine.
    """
    context_score    = compute_context_adjustment(
        engagement_score, consistency_score, integrity_score, anomaly_score, environment
    )
    learning_mode    = get_learning_mode(environment)
    integrity_flag   = check_integrity_flag(anomaly_score)
    scaffold_level   = get_scaffold_level(avg_mastery)
    behavior_summary = build_behavior_summary(
        engagement_score, consistency_score, environment, scaffold_level, integrity_flag
    )

    return {
        "context_adjustment_score": context_score,
        "learning_mode_hint":       learning_mode,
        "integrity_flag":           integrity_flag,
        "scaffold_level":           scaffold_level,
        "behavior_summary":         behavior_summary,
    }
