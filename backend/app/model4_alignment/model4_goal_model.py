"""
model4_goal_model.py
Goal Understanding Sub-Model — Model 4 (Purpose & Skill Alignment)
─────────────────────────────────────────────────────────────────────
Input  : goal_text (string)
Output :
    - goal_embedding        (384-dim numpy vector, SBERT all-MiniLM-L6-v2)
    - goal_type             (career / project / learning / vague)
    - goal_specificity_score (0–1 float, NLP-derived)

This module is stateless — call encode_goals() on a list of texts.
Embeddings are returned as numpy arrays AND serialised as JSON strings
so they can be stored in the DB.
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


# ── Goal type classifier (rule-based, no extra model needed) ─────────────────
_CAREER_KEYWORDS  = ["become", "career", "job", "role", "engineer", "developer",
                     "analyst", "scientist", "architect", "designer", "transition into"]
_PROJECT_KEYWORDS = ["build", "create", "develop", "implement", "complete",
                     "deploy", "launch", "project", "app", "system", "tool",
                     "dashboard", "api", "website", "game", "agent"]
_LEARNING_KEYWORDS= ["learn", "understand", "master", "study", "explore concepts",
                     "improve knowledge", "get better at", "practice"]
_VAGUE_THRESHOLD  = 8   # word count below this → likely vague


def classify_goal_type(text: str) -> str:
    """
    Returns one of: 'career', 'project', 'learning', 'vague'
    Priority: career > project > learning > vague
    """
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


# ── Main encoding function ────────────────────────────────────────────────────

def encode_goals(goal_texts: list) -> dict:
    """
    Encodes a list of goal strings.

    Returns a dict with keys:
        'embeddings'        : np.ndarray  shape (N, 384)
        'goal_types'        : list of str
        'embedding_strings' : list of JSON strings (for DB storage)
    """
    model = _get_model()

    embeddings = model.encode(goal_texts, show_progress_bar=False)

    goal_types = [classify_goal_type(t) for t in goal_texts]

    # Serialise embeddings as compact JSON strings for DB storage
    embedding_strings = [
        json.dumps(emb.tolist(), separators=(",", ":"))
        for emb in embeddings
    ]

    return {
        "embeddings": embeddings,                 # numpy array — used in-memory
        "goal_types": goal_types,
        "embedding_strings": embedding_strings,   # stored in DB
    }


def encode_single_goal(goal_text: str) -> dict:
    """
    Encodes a single goal string. Used by the API endpoint.
    Returns embedding as numpy array + JSON string + goal_type.
    """
    result = encode_goals([goal_text])
    return {
        "embedding": result["embeddings"][0],
        "goal_type": result["goal_types"][0],
        "embedding_string": result["embedding_strings"][0],
    }


def load_embedding_from_string(s: str) -> np.ndarray:
    """Deserialise a stored embedding JSON string back to numpy array."""
    return np.array(json.loads(s), dtype=np.float32)
