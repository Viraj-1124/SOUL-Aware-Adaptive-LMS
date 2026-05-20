"""
model4_alignment_engine.py
Alignment Engine — Core of Model 4 (Purpose & Skill Alignment)
────────────────────────────────────────────────────────────────
Input  : goal_embedding (384-dim), career templates
Output :
    - alignment_score       (float 0–1, cosine similarity)
    - predicted_domain      (str)
    - all_domain_scores     (dict: domain → score, for transparency)

Expanded to 7 domains:
    frontend, backend, ml, data_science, devops, mobile, cybersecurity

Career templates are encoded once at module load time.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ── Career domain templates ───────────────────────────────────────────────────
CAREER_TEMPLATES = {
    "frontend":      "HTML CSS JavaScript React TypeScript frontend web developer UI design",
    "backend":       "Node.js Express backend REST API databases MongoDB PostgreSQL server",
    "ml":            "Python machine learning deep learning neural networks model training",
    "data_science":  "Python data analysis pandas numpy statistics visualization data science",
    "devops":        "Docker Kubernetes CI/CD cloud deployment infrastructure automation DevOps",
    "mobile":        "React Native mobile app iOS Android cross-platform development",
    "cybersecurity": "cybersecurity network security ethical hacking penetration testing analyst",
}

# ── Singleton: encode templates once ─────────────────────────────────────────
_template_vectors: dict = {}
_sbert_model = None


def _load_templates():
    global _template_vectors, _sbert_model
    if _template_vectors:
        return  # already loaded

    from app.model4_alignment.model4_goal_model import _get_model
    _sbert_model = _get_model()

    print("[model4_alignment_engine] Encoding career templates...")
    for domain, text in CAREER_TEMPLATES.items():
        _template_vectors[domain] = _sbert_model.encode(text)
    print(f"[model4_alignment_engine] {len(_template_vectors)} domain templates ready.")


# ── Core alignment function ───────────────────────────────────────────────────

def compute_alignment(goal_embedding: np.ndarray) -> dict:
    """
    Computes cosine similarity between a goal embedding and all career templates.

    Returns:
        alignment_score    : float — highest similarity score
        predicted_domain   : str   — domain with highest score
        all_domain_scores  : dict  — {domain: score} for all domains
    """
    _load_templates()

    scores = {}
    for domain, template_vec in _template_vectors.items():
        sim = cosine_similarity(
            goal_embedding.reshape(1, -1),
            template_vec.reshape(1, -1)
        )[0][0]
        scores[domain] = round(float(sim), 6)

    best_domain = max(scores, key=scores.get)
    best_score  = scores[best_domain]

    return {
        "alignment_score":   round(best_score, 6),
        "predicted_domain":  best_domain,
        "all_domain_scores": scores,
    }


def batch_compute_alignment(embeddings: np.ndarray) -> list:
    """
    Runs compute_alignment for a batch of embeddings.
    Returns a list of result dicts (one per student).
    """
    _load_templates()
    return [compute_alignment(emb) for emb in embeddings]
