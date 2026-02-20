import textstat
from textblob import TextBlob


def analyze_reflection(text: str):
    if not text:
        return 0.0, 0.0

    # Sentiment polarity (-1 to +1)
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    # Reflection depth (readability-based proxy)
    word_count = len(text.split())
    depth_score = min(word_count / 100, 1.0) * 100

    return sentiment, depth_score