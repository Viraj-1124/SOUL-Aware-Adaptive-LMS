import re
import textstat
from textblob import TextBlob
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download("punkt")


def analyze_reflection_advanced(text: str):

    if not text or len(text.strip()) == 0:
        return None

    blob = TextBlob(text)

    # 1️⃣ Sentiment
    sentiment_polarity = blob.sentiment.polarity
    sentiment_intensity = abs(sentiment_polarity)

    # 2️⃣ Lexical Diversity
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha()]
    total_words = len(words)
    unique_words = len(set(words))

    lexical_diversity = unique_words / total_words if total_words > 0 else 0

    # 3️⃣ Self Reference Ratio
    self_words = ["i", "me", "my", "mine", "myself"]
    self_count = sum(1 for w in words if w in self_words)
    self_reference_ratio = self_count / total_words if total_words > 0 else 0

    # 4️⃣ Cognitive Complexity (Sentence Length Proxy)
    sentences = sent_tokenize(text)
    sentence_lengths = [len(word_tokenize(s)) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

    cognitive_complexity = min(avg_sentence_length / 30, 1)  # normalize

    # 5️⃣ Reflection Depth Score (Enhanced)
    readability = textstat.flesch_reading_ease(text)
    depth_score = min((total_words / 150), 1)

    reflection_depth_score = (depth_score * 0.6) + ((1 - readability/100) * 0.4)

    return {
        "sentiment_polarity": sentiment_polarity,
        "sentiment_intensity": sentiment_intensity,
        "lexical_diversity": lexical_diversity,
        "self_reference_ratio": self_reference_ratio,
        "cognitive_complexity": cognitive_complexity,
        "reflection_depth_score": reflection_depth_score
    }