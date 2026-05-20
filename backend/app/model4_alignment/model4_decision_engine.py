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

Decision rules (5 layers):
    1. Two-stage alignment check  → goal_type + alignment_score
    2. Skill gap prioritisation   → weakest_topics sorted by gap
    3. Context awareness          → learning_mode_hint adjusts resources
    4. Scaffold fading            → scaffold_level adjusts tone
    5. Integrity adjustment       → integrity_flag reduces confidence
"""

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

# ── Thresholds ────────────────────────────────────────────────────────────────
LOW_ALIGNMENT_THRESHOLD  = 0.20
HIGH_ALIGNMENT_THRESHOLD = 0.45
HIGH_GAP_THRESHOLD       = 0.50
LOW_SPECIFICITY          = 0.35


def _get_resources(domain: str, learning_mode: str) -> list:
    domain_res = RESOURCES.get(domain, DEFAULT_RESOURCES)
    return domain_res.get(learning_mode, DEFAULT_RESOURCES.get(learning_mode, []))


def _build_learning_path(weakest_topics: list, learning_mode: str) -> list:
    """
    Constructs an ordered learning path from weakest topics.
    Prefixes each topic with a mode-appropriate action verb.
    """
    if not weakest_topics:
        return ["Continue current learning path"]

    verb_map = {
        "theory":   "Study",
        "practice": "Practice",
        "project":  "Build a project using",
    }
    verb = verb_map.get(learning_mode, "Learn")
    return [f"{verb} {topic}" for topic in weakest_topics]


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
) -> dict:
    """
    Applies all 5 decision layers and returns the full output dict.
    """

    # ── Layer 1: Two-stage alignment check ───────────────────────────────────
    if alignment_score < LOW_ALIGNMENT_THRESHOLD:
        if goal_type == "vague":
            recommendation = "Your goal is too vague — define a specific career or project target"
        else:
            recommendation = "Goal-domain mismatch detected — consider revising your goal statement"

    # ── Layer 2: Skill gap prioritisation ────────────────────────────────────
    elif skill_gap > HIGH_GAP_THRESHOLD:
        if weakest_topics:
            recommendation = f"Focus on building core skills: {', '.join(weakest_topics[:2])}"
        else:
            recommendation = "Focus on improving core skills for your target domain"

    # ── Layer 3: Goal specificity check ──────────────────────────────────────
    elif goal_specificity_score < LOW_SPECIFICITY:
        recommendation = "Make your goal more specific — add a timeline, tool, or project target"

    # ── Layer 4: Scaffold fading ──────────────────────────────────────────────
    elif scaffold_level == "low":
        recommendation = "You are well-prepared — take on advanced projects and contribute to open source"
    elif scaffold_level == "high":
        recommendation = "Start with fundamentals — build a strong base before moving to advanced topics"

    # ── Default: on track ────────────────────────────────────────────────────
    else:
        recommendation = "You are on the right track — keep building and stay consistent"

    # ── Layer 5: Integrity adjustment ────────────────────────────────────────
    confidence_score = round(alignment_score * (1 - 0.20 * int(integrity_flag)), 4)

    # ── Build learning path ───────────────────────────────────────────────────
    learning_path = _build_learning_path(weakest_topics, learning_mode_hint)

    # ── Resources ────────────────────────────────────────────────────────────
    resources = _get_resources(predicted_domain, learning_mode_hint)

    # ── Explanation ───────────────────────────────────────────────────────────
    gap_detail = (
        f"Skill gaps: {', '.join(weakest_topics)}" if weakest_topics
        else "No major skill gaps detected"
    )
    integrity_note = " (⚠️ confidence reduced due to anomalous activity)" if integrity_flag else ""
    collab_note = (
        " | Strong collaboration signals detected." if collaboration_score > 0.75
        else (" | Low collaboration — consider group learning." if collaboration_score < 0.40 else "")
    )

    explanation = (
        f"Goal: {goal_type.capitalize()} goal | "
        f"Domain: {predicted_domain.replace('_', ' ').title()} | "
        f"Alignment: {alignment_score:.2f} | "
        f"Skill gap: {skill_gap:.2f} | "
        f"{gap_detail} | "
        f"Learning mode: {learning_mode_hint}{integrity_note}{collab_note}"
    )

    return {
        "recommendation":   recommendation,
        "learning_path":    learning_path,
        "resources":        resources,
        "explanation":      explanation,
        "confidence_score": confidence_score,
    }
