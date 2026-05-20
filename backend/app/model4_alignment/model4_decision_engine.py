"""
model4_decision_engine.py
Decision Engine — Intelligence Layer of Model 4 (Purpose & Skill Alignment)
─────────────────────────────────────────────────────────────────────────────
Input  : alignment results + skill results + context results + goal metadata
Output :
    - recommendation        (str: primary action)
    - learning_path         (list: ordered topics to study)
    - resources             (list: suggested resource types)
    - explanation           (str: full human-readable explanation)
    - confidence_score      (float: how confident the system is)

Primary path  : ML bundle (model4_bundle.pkl)
    - RF Classifier  → recommendation label (20 classes)
    - GB Regressor   → refined confidence score
    - KMeans         → student cluster (7 career domains)
    - Label Encoder  → decode RF output to string

Fallback path : rule-based (5 layers) used if pkl unavailable
"""

import os
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ── Load ML bundle once ───────────────────────────────────────────────────────
_bundle = None
_bundle_loaded = False

def _get_bundle():
    global _bundle, _bundle_loaded
    if _bundle_loaded:
        return _bundle
    _bundle_loaded = True
    try:
        bundle_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "ml", "model4_bundle.pkl"
        )
        if os.path.exists(bundle_path):
            with open(bundle_path, "rb") as f:
                _bundle = pickle.load(f)
            logger.info("[model4_decision_engine] ML bundle loaded successfully.")
            print("[model4_decision_engine] ML bundle loaded (RF + GB + KMeans).")
        else:
            logger.warning("[model4_decision_engine] model4_bundle.pkl not found. Using rule-based fallback.")
    except Exception as e:
        logger.warning(f"[model4_decision_engine] Failed to load ML bundle: {e}. Using rule-based fallback.")
        _bundle = None
    return _bundle


# ── Resource suggestions per domain + learning mode ──────────────────────────
RESOURCES = {
    "frontend": {
        "theory":   ["MDN Web Docs", "CSS-Tricks", "JavaScript.info"],
        "practice": ["Frontend Mentor challenges", "CodePen exercises"],
        "project":  ["Build a portfolio site", "Clone a real website"],
    },
    "backend": {
        "theory":   ["Node.js official docs", "Express.js guide", "REST API design guide"],
        "practice": ["Build a CRUD API", "Database design exercises"],
        "project":  ["Build a REST API with auth", "Deploy on Railway/Render"],
    },
    "ml": {
        "theory":   ["fast.ai course", "Hands-On ML (Aurélien Géron)", "Kaggle Learn"],
        "practice": ["Kaggle competitions", "Implement algorithms from scratch"],
        "project":  ["End-to-end ML project on Kaggle", "Deploy a model with Flask"],
    },
    "data_science": {
        "theory":   ["Python for Data Analysis (Wes McKinney)", "Statistics fundamentals"],
        "practice": ["Pandas exercises", "EDA on real datasets"],
        "project":  ["Data analysis report", "Interactive dashboard with Plotly"],
    },
    "devops": {
        "theory":   ["Docker official docs", "Kubernetes basics", "CI/CD concepts"],
        "practice": ["Dockerise a Python app", "Set up GitHub Actions"],
        "project":  ["Deploy a full-stack app with Docker Compose"],
    },
    "mobile": {
        "theory":   ["React Native docs", "Expo documentation"],
        "practice": ["Build a to-do app in React Native"],
        "project":  ["Publish an app to Expo Go"],
    },
    "cybersecurity": {
        "theory":   ["TryHackMe beginner paths", "CompTIA Security+ study guide"],
        "practice": ["CTF challenges on PicoCTF", "Network scanning with Nmap"],
        "project":  ["Build a port scanner in Python"],
    },
}

DEFAULT_RESOURCES = {
    "theory":   ["Search official documentation", "YouTube tutorials"],
    "practice": ["LeetCode / HackerRank exercises"],
    "project":  ["Build a small end-to-end project"],
}

# ── Rule-based fallback thresholds ────────────────────────────────────────────
LOW_ALIGNMENT_THRESHOLD  = 0.20
HIGH_GAP_THRESHOLD       = 0.50
LOW_SPECIFICITY          = 0.35


def _get_resources(domain: str, learning_mode: str) -> list:
    domain_res = RESOURCES.get(domain, DEFAULT_RESOURCES)
    return domain_res.get(learning_mode, DEFAULT_RESOURCES.get(learning_mode, []))


def _build_learning_path(weakest_topics: list, learning_mode: str) -> list:
    if not weakest_topics:
        return ["Continue current learning path"]
    verb_map = {"theory": "Study", "practice": "Practice", "project": "Build a project using"}
    verb = verb_map.get(learning_mode, "Learn")
    return [f"{verb} {topic}" for topic in weakest_topics]


def _rule_based_recommendation(
    alignment_score, goal_type, skill_gap, goal_specificity_score,
    scaffold_level, weakest_topics
) -> str:
    """5-layer rule-based fallback."""
    if alignment_score < LOW_ALIGNMENT_THRESHOLD:
        return ("Your goal is too vague — define a specific career or project target"
                if goal_type == "vague"
                else "Goal-domain mismatch detected — consider revising your goal statement")
    if skill_gap > HIGH_GAP_THRESHOLD:
        return (f"Focus on building core skills: {', '.join(weakest_topics[:2])}"
                if weakest_topics
                else "Focus on improving core skills for your target domain")
    if goal_specificity_score < LOW_SPECIFICITY:
        return "Make your goal more specific — add a timeline, tool, or project target"
    if scaffold_level == "low":
        return "You are well-prepared — take on advanced projects and contribute to open source"
    if scaffold_level == "high":
        return "Start with fundamentals — build a strong base before moving to advanced topics"
    return "You are on the right track — keep building and stay consistent"


def _build_feature_vector(
    alignment_score, skill_gap, goal_specificity_score,
    context_adjustment_score, collaboration_score,
    engagement_score, integrity_score, consistency_score,
    confidence_score, skill_gap_vector
) -> list:
    """
    Build the 16-feature vector matching model4_bundle training schema exactly:
    [alignment_score, skill_gap, goal_specificity_score, context_adjustment_score,
     collaboration_score, engagement_score, integrity_score, consistency_score,
     confidence_score, gap_HTML, gap_CSS, gap_JS, gap_React, gap_Python, gap_DSA, gap_ML]
    """
    # skill_gap_vector keys come from model4_skill_model as e.g. "HTML_mastery"
    # map them to the training column names gap_HTML, gap_CSS, etc.
    def g(mastery_key, gap_key):
        return skill_gap_vector.get(mastery_key, skill_gap_vector.get(gap_key, 0.0))

    return [
        alignment_score,
        skill_gap,
        goal_specificity_score,
        context_adjustment_score,
        collaboration_score,
        engagement_score,
        integrity_score,
        consistency_score,
        confidence_score,
        g("HTML_mastery",   "gap_HTML"),
        g("CSS_mastery",    "gap_CSS"),
        g("JS_mastery",     "gap_JS"),
        g("React_mastery",  "gap_React"),
        g("Python_mastery", "gap_Python"),
        g("DSA_mastery",    "gap_DSA"),
        g("ML_mastery",     "gap_ML"),
    ]


def make_decision(
    alignment_score: float,
    predicted_domain: str,
    goal_type: str,
    goal_specificity_score: float,
    skill_gap: float,
    weakest_topics: list,
    learning_mode_hint: str,
    scaffold_level: str,
    integrity_flag: bool,
    collaboration_score: float,
    # Extended context passed from service
    engagement_score: float = 0.5,
    consistency_score: float = 0.5,
    integrity_score: float = 0.8,
    context_adjustment_score: float = 0.5,
    skill_gap_vector: dict = None,
) -> dict:
    """
    Runs the ML bundle (RF + GB + KMeans) to generate recommendation.
    Falls back to rule-based logic if bundle is unavailable.
    """
    if skill_gap_vector is None:
        skill_gap_vector = {}

    # Base confidence (integrity penalty applied regardless of path)
    base_confidence = round(alignment_score * (1 - 0.20 * int(integrity_flag)), 4)

    bundle = _get_bundle()

    recommendation = None
    confidence_score = base_confidence

    # ── ML path ──────────────────────────────────────────────────────────────
    if bundle is not None:
        try:
            rf = bundle["rf_classifier"]
            gb = bundle["gb_regressor"]
            le = bundle["label_encoder"]

            feat_16 = _build_feature_vector(
                alignment_score, skill_gap, goal_specificity_score,
                context_adjustment_score, collaboration_score,
                engagement_score, integrity_score, consistency_score,
                base_confidence, skill_gap_vector
            )

            # RF → recommendation label
            pred_class = rf.predict([feat_16])[0]
            recommendation = le.inverse_transform([pred_class])[0]

            # GB → refined confidence (uses 15 features, drop last gap_ML)
            feat_15 = feat_16[:15]
            gb_score = float(gb.predict([feat_15])[0])
            # Blend GB score with base confidence, clamp to [0,1]
            confidence_score = round(
                float(np.clip(0.6 * gb_score + 0.4 * base_confidence, 0.0, 1.0)), 4
            )

            logger.debug(f"[ML] recommendation='{recommendation}', confidence={confidence_score}")

        except Exception as e:
            logger.warning(f"[model4_decision_engine] ML prediction failed: {e}. Using rule-based fallback.")
            recommendation = None

    # ── Rule-based fallback ───────────────────────────────────────────────────
    if recommendation is None:
        recommendation = _rule_based_recommendation(
            alignment_score, goal_type, skill_gap,
            goal_specificity_score, scaffold_level, weakest_topics
        )

    # ── Learning path + resources (same for both paths) ───────────────────────
    learning_path = _build_learning_path(weakest_topics, learning_mode_hint)
    resources     = _get_resources(predicted_domain, learning_mode_hint)

    # ── Explanation ───────────────────────────────────────────────────────────
    gap_detail     = f"Skill gaps: {', '.join(weakest_topics)}" if weakest_topics else "No major skill gaps detected"
    integrity_note = " (⚠️ confidence reduced due to anomalous activity)" if integrity_flag else ""
    collab_note    = (
        " | Strong collaboration signals detected." if collaboration_score > 0.75
        else (" | Low collaboration — consider group learning." if collaboration_score < 0.40 else "")
    )
    ml_note = " [ML]" if bundle is not None else " [rule-based]"

    explanation = (
        f"Goal: {goal_type.capitalize()} goal | "
        f"Domain: {predicted_domain.replace('_', ' ').title()} | "
        f"Alignment: {alignment_score:.2f} | "
        f"Skill gap: {skill_gap:.2f} | "
        f"{gap_detail} | "
        f"Learning mode: {learning_mode_hint}"
        f"{integrity_note}{collab_note}{ml_note}"
    )

    return {
        "recommendation":   recommendation,
        "learning_path":    learning_path,
        "resources":        resources,
        "explanation":      explanation,
        "confidence_score": confidence_score,
    }
