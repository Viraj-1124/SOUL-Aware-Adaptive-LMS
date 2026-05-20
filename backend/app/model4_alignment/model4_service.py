"""
model4_service.py
Orchestration Service — Model 4 (Purpose & Skill Alignment)
─────────────────────────────────────────────────────────────
Runs the full Model 4 pipeline for a single student request:
    1. Compute goal specificity + collaboration score from inputs
    2. Encode goal text → SBERT embedding + goal_type
    3. Compute alignment score + predicted_domain
    4. Compute skill gap vector + weakest topics
    5. Compute context adjustment + scaffold level
    6. Run decision engine → recommendation + learning_path + resources
    7. Persist result to DB (StudentGoalProfile table)
    8. Return full result dict

This service is called by the FastAPI router.
"""

import json
from sqlalchemy.orm import Session
from datetime import datetime

from app.model4_alignment.model4_data_utils import (
    compute_goal_specificity,
    compute_collaboration_score,
)
from app.model4_alignment.model4_goal_model import encode_single_goal
from app.model4_alignment.model4_alignment_engine import compute_alignment
from app.model4_alignment.model4_skill_model import process_student_skills
from app.model4_alignment.model4_context_model import process_context
from app.model4_alignment.model4_decision_engine import make_decision
from app.models.model4_goal_profile import StudentGoalProfile


def run_alignment_pipeline(
    db: Session,
    student_id: int,
    goal_text: str,
    html_mastery: float,
    css_mastery: float,
    js_mastery: float,
    react_mastery: float,
    python_mastery: float,
    ml_mastery: float,
    dsa_mastery: float,
    environment: str,
    engagement_score: float,
    consistency_score: float,
    integrity_score: float,
    anomaly_score: float,
) -> dict:
    """
    Full Model 4 pipeline for one student.
    Saves result to DB and returns the complete output dict.
    """

    # ── Step 1: Compute derived scores ───────────────────────────────────────
    goal_specificity_score = compute_goal_specificity(goal_text)
    collaboration_score = compute_collaboration_score(
        engagement_score, consistency_score, integrity_score, anomaly_score, environment
    )

    # ── Step 2: Goal model — embedding + goal_type ────────────────────────────
    goal_result = encode_single_goal(goal_text)
    embedding       = goal_result["embedding"]
    goal_type       = goal_result["goal_type"]
    embedding_str   = goal_result["embedding_string"]

    # ── Step 3: Alignment engine ──────────────────────────────────────────────
    alignment_result = compute_alignment(embedding)
    alignment_score  = alignment_result["alignment_score"]
    predicted_domain = alignment_result["predicted_domain"]
    all_domain_scores = alignment_result["all_domain_scores"]

    # ── Step 4: Skill model ───────────────────────────────────────────────────
    mastery_row = {
        "HTML_mastery":   html_mastery,
        "CSS_mastery":    css_mastery,
        "JS_mastery":     js_mastery,
        "React_mastery":  react_mastery,
        "Python_mastery": python_mastery,
        "ML_mastery":     ml_mastery,
        "DSA_mastery":    dsa_mastery,
    }
    skill_result   = process_student_skills(mastery_row, predicted_domain)
    skill_gap      = skill_result["skill_gap"]
    weakest_topics = skill_result["weakest_topics"]
    skill_gap_vector = skill_result["skill_gap_vector"]

    # Average mastery across all 7 skills (for scaffold level)
    avg_mastery = sum(mastery_row.values()) / len(mastery_row)

    # ── Step 5: Context model ─────────────────────────────────────────────────
    context_result = process_context(
        engagement_score, consistency_score, integrity_score,
        anomaly_score, environment, avg_mastery
    )
    context_adjustment_score = context_result["context_adjustment_score"]
    learning_mode_hint       = context_result["learning_mode_hint"]
    integrity_flag           = context_result["integrity_flag"]
    scaffold_level           = context_result["scaffold_level"]
    behavior_summary         = context_result["behavior_summary"]

    # ── Step 6: Decision engine ───────────────────────────────────────────────
    decision = make_decision(
        alignment_score        = alignment_score,
        predicted_domain       = predicted_domain,
        goal_type              = goal_type,
        goal_specificity_score = goal_specificity_score,
        skill_gap              = skill_gap,
        weakest_topics         = weakest_topics,
        learning_mode_hint     = learning_mode_hint,
        scaffold_level         = scaffold_level,
        integrity_flag         = integrity_flag,
        collaboration_score    = collaboration_score,
        # Extended context for ML bundle feature vector
        engagement_score       = engagement_score,
        consistency_score      = consistency_score,
        integrity_score        = integrity_score,
        context_adjustment_score = context_adjustment_score,
        skill_gap_vector       = skill_gap_vector,
    )

    # ── Step 7: Persist to DB ─────────────────────────────────────────────────
    # Upsert: update existing record if student already has a goal profile
    existing = db.query(StudentGoalProfile).filter(
        StudentGoalProfile.student_id == student_id
    ).first()

    record_data = dict(
        student_id               = student_id,
        goal_text                = goal_text,
        goal_type                = goal_type,
        goal_specificity_score   = goal_specificity_score,
        goal_embedding           = embedding_str,
        html_mastery             = html_mastery,
        css_mastery              = css_mastery,
        js_mastery               = js_mastery,
        react_mastery            = react_mastery,
        python_mastery           = python_mastery,
        ml_mastery               = ml_mastery,
        dsa_mastery              = dsa_mastery,
        environment              = environment,
        engagement_score         = engagement_score,
        consistency_score        = consistency_score,
        integrity_score          = integrity_score,
        anomaly_score            = anomaly_score,
        collaboration_score      = collaboration_score,
        alignment_score          = alignment_score,
        predicted_domain         = predicted_domain,
        all_domain_scores        = json.dumps(all_domain_scores),
        skill_gap                = skill_gap,
        skill_gap_vector         = json.dumps(skill_gap_vector),
        weakest_topics           = json.dumps(weakest_topics),
        context_adjustment_score = context_adjustment_score,
        learning_mode_hint       = learning_mode_hint,
        integrity_flag           = integrity_flag,
        scaffold_level           = scaffold_level,
        behavior_summary         = behavior_summary,
        recommendation           = decision["recommendation"],
        learning_path            = json.dumps(decision["learning_path"]),
        resources                = json.dumps(decision["resources"]),
        explanation              = decision["explanation"],
        confidence_score         = decision["confidence_score"],
        updated_at               = datetime.utcnow(),
    )

    if existing:
        for key, value in record_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
    else:
        profile = StudentGoalProfile(**record_data)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # ── Step 8: Return full result ────────────────────────────────────────────
    return {
        "student_id":               student_id,
        "goal_text":                goal_text,
        "goal_type":                goal_type,
        "goal_specificity_score":   goal_specificity_score,
        "collaboration_score":      collaboration_score,
        "alignment_score":          alignment_score,
        "predicted_domain":         predicted_domain,
        "all_domain_scores":        all_domain_scores,
        "skill_gap":                skill_gap,
        "skill_gap_vector":         skill_gap_vector,
        "weakest_topics":           weakest_topics,
        "context_adjustment_score": context_adjustment_score,
        "learning_mode_hint":       learning_mode_hint,
        "integrity_flag":           integrity_flag,
        "scaffold_level":           scaffold_level,
        "behavior_summary":         behavior_summary,
        "recommendation":           decision["recommendation"],
        "learning_path":            decision["learning_path"],
        "resources":                decision["resources"],
        "explanation":              decision["explanation"],
        "confidence_score":         decision["confidence_score"],
    }


def get_goal_profile(db: Session, student_id: int):
    """Fetch the stored goal profile for a student."""
    return db.query(StudentGoalProfile).filter(
        StudentGoalProfile.student_id == student_id
    ).first()


# ── Skill keyword mapping for topic-title → skill dimension ──────────────────
_SKILL_KEYWORDS = {
    "html_mastery":    ["html", "markup", "hypertext", "dom", "semantic"],
    "css_mastery":     ["css", "style", "stylesheet", "tailwind", "bootstrap", "flexbox", "grid", "sass", "scss"],
    "js_mastery":      ["javascript", "js", "typescript", "ts", "es6", "ecmascript", "async", "promise", "node"],
    "react_mastery":   ["react", "jsx", "tsx", "component", "hook", "redux", "next", "vue", "angular"],
    "python_mastery":  ["python", "django", "flask", "fastapi", "pandas", "numpy", "scipy"],
    "ml_mastery":      ["machine learning", "ml", "deep learning", "neural", "tensorflow", "pytorch",
                        "sklearn", "scikit", "nlp", "computer vision", "ai", "model", "classification",
                        "regression", "clustering"],
    "dsa_mastery":     ["data structure", "algorithm", "dsa", "sorting", "graph", "tree", "dynamic programming",
                        "recursion", "complexity", "leetcode", "binary search", "linked list", "stack", "queue"],
}


def derive_mastery_from_knowledge_states(enriched_states: list) -> dict:
    """
    Derives the 7 Model 4 skill mastery scores from knowledge tracing states.

    enriched_states: list of dicts with keys:
        - topic_title      (str)
        - bkt_probability  (float)
        - lstm_probability (float)

    Strategy:
        - For each topic, compute avg_prob = mean(bkt, lstm)
        - Match topic title to skill dimensions via keyword lookup
        - For each skill dimension, average all matched topic probabilities
        - Skills with no matching topics default to 0.3 (neutral prior)

    Returns a dict matching MasteryPrefillOut fields.
    """
    # Accumulate matched probabilities per skill
    skill_scores: dict = {skill: [] for skill in _SKILL_KEYWORDS}
    source_topics: dict = {skill: [] for skill in _SKILL_KEYWORDS}

    for state in enriched_states:
        title_lower = state["topic_title"].lower()
        avg_prob = (state["bkt_probability"] + state["lstm_probability"]) / 2.0

        for skill, keywords in _SKILL_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                skill_scores[skill].append(avg_prob)
                source_topics[skill].append(state["topic_title"])

    # Compute final mastery per skill; default 0.3 if no data
    DEFAULT_PRIOR = 0.3
    mastery = {}
    for skill, scores in skill_scores.items():
        if scores:
            mastery[skill] = round(float(sum(scores) / len(scores)), 4)
        else:
            mastery[skill] = DEFAULT_PRIOR

    has_data = any(len(v) > 0 for v in skill_scores.values())

    return {
        **mastery,
        "source_topics": source_topics,
        "has_data": has_data,
    }
