"""
model4_skill_model.py
Skill Mastery Sub-Model — Model 4 (Purpose & Skill Alignment)
───────────────────────────────────────────────────────────────
Input  : mastery dict {skill_col: value} + predicted domain
Output :
    - topic_mastery_vector  (dict: topic → mastery score)
    - skill_gap_vector      (dict: topic → gap for predicted domain)
    - skill_gap_scalar      (float: mean gap, for backward compat)
    - weakest_topics        (list: top-3 topics with highest gap, sorted)

Supports 7 career domains (expanded from original 3).
"""

import numpy as np

# ── Skill columns present in the dataset ─────────────────────────────────────
SKILL_COLS = [
    "HTML_mastery", "CSS_mastery", "JS_mastery", "React_mastery",
    "Python_mastery", "ML_mastery", "DSA_mastery"
]

# Short display names for each skill column
SKILL_DISPLAY = {
    "HTML_mastery":   "HTML",
    "CSS_mastery":    "CSS",
    "JS_mastery":     "JavaScript",
    "React_mastery":  "React",
    "Python_mastery": "Python",
    "ML_mastery":     "Machine Learning",
    "DSA_mastery":    "DSA",
}

# ── Required skills per domain ────────────────────────────────────────────────
DOMAIN_REQUIRED_SKILLS = {
    "frontend":     ["HTML_mastery", "CSS_mastery", "JS_mastery", "React_mastery"],
    "backend":      ["JS_mastery", "Python_mastery"],
    "ml":           ["Python_mastery", "ML_mastery", "DSA_mastery"],
    "data_science": ["Python_mastery", "ML_mastery", "DSA_mastery"],
    "devops":       ["Python_mastery", "JS_mastery"],
    "mobile":       ["React_mastery", "JS_mastery"],
    "cybersecurity":["Python_mastery", "DSA_mastery"],
}


def get_mastery_vector(row: dict) -> dict:
    """Returns {skill_name: mastery_score} for all skills."""
    return {col: float(row.get(col, 0.0)) for col in SKILL_COLS}


def compute_skill_gap_vector(mastery_vector: dict, domain: str) -> dict:
    """
    Computes per-skill gap for the required skills of a domain.
    gap = max(0, 1.0 - current_mastery)
    Returns {skill_col: gap_value} only for domain-relevant skills.
    """
    required = DOMAIN_REQUIRED_SKILLS.get(domain, list(mastery_vector.keys()))
    gap_vector = {}
    for skill in required:
        current = mastery_vector.get(skill, 0.0)
        gap_vector[skill] = round(max(0.0, 1.0 - current), 4)
    return gap_vector


def compute_skill_gap_scalar(gap_vector: dict) -> float:
    """Mean of all gap values — single number for quick comparison."""
    if not gap_vector:
        return 0.0
    return round(float(np.mean(list(gap_vector.values()))), 4)


def get_weakest_topics(gap_vector: dict, top_n: int = 3) -> list:
    """
    Returns top_n skill display names sorted by gap (largest first).
    Used for generating specific learning path recommendations.
    """
    sorted_gaps = sorted(gap_vector.items(), key=lambda x: x[1], reverse=True)
    return [SKILL_DISPLAY[skill] for skill, gap in sorted_gaps[:top_n] if gap > 0]


def process_student_skills(row: dict, domain: str) -> dict:
    """
    Full skill processing for one student.
    row: dict with skill mastery keys (HTML_mastery, etc.)
    Returns all skill outputs needed by the alignment engine.
    """
    mastery_vector  = get_mastery_vector(row)
    gap_vector      = compute_skill_gap_vector(mastery_vector, domain)
    gap_scalar      = compute_skill_gap_scalar(gap_vector)
    weakest_topics  = get_weakest_topics(gap_vector)

    return {
        "topic_mastery_vector": mastery_vector,
        "skill_gap_vector":     gap_vector,
        "skill_gap":            gap_scalar,
        "weakest_topics":       weakest_topics,
    }
