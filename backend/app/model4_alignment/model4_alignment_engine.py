"""
model4_alignment_engine.py
Alignment Engine — Core of Model 4 (Purpose & Skill Alignment)
────────────────────────────────────────────────────────────────
Input  : goal_embedding (384-dim numpy vector)
Output :
    - alignment_score    (float 0–1, cosine similarity to best domain)
    - predicted_domain   (str)
    - all_domain_scores  (dict: domain → score, for UI transparency)

7 career domains: frontend, backend, ml, data_science, devops, mobile, cybersecurity
Career template vectors are encoded once at first call (singleton).
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

CAREER_TEMPLATES = {
    "frontend":      "HTML CSS JavaScript React TypeScript frontend web developer UI design",
    "backend":       "Node.js Express backend REST API databases MongoDB PostgreSQL server",
    "ml":            "Python machine learning deep learning neural networks model training",
    "data_science":  "Python data analysis pandas numpy statistics visualization data science",
    "devops":        "Docker Kubernetes CI/CD cloud deployment infrastructure automation DevOps",
    "mobile":        "React Native mobile app iOS Android cross-platform development",
    "cybersecurity": "cybersecurity network security ethical hacking penetration testing analyst",
}

_template_vectors: dict = {}


def _load_templates():
    global _template_vectors
    if _template_vectors:
        return
    from app.model4_alignment.model4_goal_model import _get_model
    model = _get_model()
    print("[model4_alignment_engine] Encoding career templates...")
    for domain, text in CAREER_TEMPLATES.items():
        _template_vectors[domain] = model.encode(text)
    print(f"[model4_alignment_engine] {len(_template_vectors)} domain templates ready.")


def compute_alignment(goal_embedding: np.ndarray) -> dict:
    """
    Computes cosine similarity between a goal embedding and all career templates.
    Returns the best domain, its score, and all 7 domain scores.
    """
    _load_templates()
    scores = {
        domain: round(float(cosine_similarity(
            goal_embedding.reshape(1, -1),
            vec.reshape(1, -1)
        )[0][0]), 6)
        for domain, vec in _template_vectors.items()
    }
    best_domain = max(scores, key=scores.get)
    return {
        "alignment_score":   scores[best_domain],
        "predicted_domain":  best_domain,
        "all_domain_scores": scores,
    }
