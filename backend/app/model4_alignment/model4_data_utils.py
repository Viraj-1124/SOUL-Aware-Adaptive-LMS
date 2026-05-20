"""
model4_data_utils.py
Data utility functions for Model 4 — Purpose & Skill Alignment
────────────────────────────────────────────────────────────────
Provides:
  - compute_goal_specificity(text)   → NLP-based specificity score (0–1)
  - compute_collaboration_score(...) → behavior-derived collaboration score (0–1)

These are the same functions from data_generator.py, adapted for
use inside the FastAPI service (no CSV I/O needed here).
"""

import re
import numpy as np

# ── NLP-based goal specificity ────────────────────────────────────────────────
TECH_KEYWORDS = [
    "html", "css", "javascript", "js", "react", "node", "python", "ml",
    "machine learning", "deep learning", "dsa", "api", "backend", "frontend",
    "full-stack", "fullstack", "django", "flask", "sql", "mongodb", "aws",
    "docker", "kubernetes", "nlp", "data science", "typescript", "mern",
    "tensorflow", "pytorch", "opencv", "blockchain", "devops", "cloud",
    "cybersecurity", "mobile", "react native", "canvas", "d3", "reinforcement"
]

TIME_PATTERNS = [
    r"\d+\s*(day|week|month|year)s?",
    r"by end of",
    r"within \d+",
    r"in \d+",
    r"this semester",
    r"final year"
]

ACTION_KEYWORDS = [
    "build", "create", "develop", "implement", "complete", "master",
    "learn", "become", "land", "transition", "understand", "design",
    "deploy", "launch", "finish", "achieve"
]


def compute_goal_specificity(text: str) -> float:
    """
    Returns a 0–1 score for how specific a goal statement is.
    Combines word count, tech keyword presence, time mention, action verb.
    """
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)

    # 1. Length score (normalised, cap at 20 words → 1.0)
    length_score = min(word_count / 20.0, 1.0)

    # 2. Tech keyword score
    tech_hits = sum(1 for kw in TECH_KEYWORDS if kw in text_lower)
    tech_score = min(tech_hits / 3.0, 1.0)

    # 3. Time mention score
    time_score = 1.0 if any(re.search(p, text_lower) for p in TIME_PATTERNS) else 0.0

    # 4. Action verb score
    action_score = 1.0 if any(kw in text_lower for kw in ACTION_KEYWORDS) else 0.0

    specificity = (
        0.20 * length_score +
        0.40 * tech_score +
        0.25 * time_score +
        0.15 * action_score
    )
    return round(float(specificity), 4)


def compute_collaboration_score(
    engagement_score: float,
    consistency_score: float,
    integrity_score: float,
    anomaly_score: float,
    environment: str,
) -> float:
    """
    Derives collaboration_score from behavior signals.
    High engagement + high consistency + high integrity → high collaboration.
    Anomaly score reduces it.
    """
    base = (
        0.35 * engagement_score +
        0.35 * consistency_score +
        0.20 * integrity_score +
        0.10 * (1 - anomaly_score)
    )
    env_bonus = {"lab": 0.05, "project": 0.05, "online": 0.0, "self-study": -0.03}
    base += env_bonus.get(str(environment).lower(), 0.0)
    return round(float(np.clip(base, 0.0, 1.0)), 4)
