"""
model4_goal_model.py
Goal Understanding Sub-Model — Model 4 (Purpose & Skill Alignment)
─────────────────────────────────────────────────────────────────────
Input  : goal_text (string)
Output :
    - goal_embedding   (384-dim numpy vector, SBERT all-MiniLM-L6-v2)
    - goal_type        (career / project / learning / vague)
    - embedding_string (JSON string for DB storage)
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Model singleton (loaded once) ────────────────────────────────────────────
_sbert_model = None

def _get_model():
    global _sbert_model
    if _sbert_model is None:
        print("[model4_goal_model] Loading SBERT model (all-MiniLM-L6-v2)...")
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[model4_goal_model] SBERT model loaded.")
    return _sbert_model


# ── Goal type classifier (rule-based) ────────────────────────────────────────
_CAREER_KEYWORDS   = ["become", "career", "job", "role", "engineer", "developer",
                      "analyst", "scientist", "architect", "designer", "transition into"]
_PROJECT_KEYWORDS  = ["build", "create", "develop", "implement", "complete",
                      "deploy", "launch", "project", "app", "system", "tool",
                      "dashboard", "api", "website", "game", "agent"]
_LEARNING_KEYWORDS = ["learn", "understand", "master", "study", "explore concepts",
                      "improve knowledge", "get better at", "practice"]
_VAGUE_THRESHOLD   = 8


def classify_goal_type(text: str) -> str:
    """Returns one of: 'career', 'project', 'learning', 'vague'"""
    t = text.lower()
    words = t.split()
    if len(words) < _VAGUE_THRESHOLD and not any(
        kw in t for kw in _CAREER_KEYWORDS + _PROJECT_KEYWORDS + _LEARNING_KEYWORDS
    ):
        return "vague"
    if any(kw in t for kw in _CAREER_KEYWORDS):
        return "career"
    if any(kw in t for kw in _PROJECT_KEYWORDS):
        return "project"
    if any(kw in t for kw in _LEARNING_KEYWORDS):
        return "learning"
    return "vague"


def encode_single_goal(goal_text: str) -> dict:
    """
    Encodes a single goal string. Used by the API service.
    Returns embedding as numpy array + JSON string + goal_type.
    """
    model = _get_model()
    embedding = model.encode([goal_text], show_progress_bar=False)[0]
    return {
        "embedding":        embedding,
        "goal_type":        classify_goal_type(goal_text),
        "embedding_string": json.dumps(embedding.tolist(), separators=(",", ":")),
    }
