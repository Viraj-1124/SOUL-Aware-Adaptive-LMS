import os
import pickle
import logging

logger = logging.getLogger(__name__)

# Try to mock SimpleBKT in case it's needed for unpickling
class SimpleBKT:
    def __init__(self):
        self.p_known = 0.5
        self.p_learned = 0.1
        self.p_guess = 0.2
        self.p_slip = 0.1

    def update(self, correct):
        pass

    def predict(self):
        return 0.5

# Ensure it's in the main module space if the pickle was saved from __main__
import sys
sys.modules['__main__'].SimpleBKT = SimpleBKT

class BKTPredictor:
    def __init__(self, model_path="app/ml/bkt_model.pkl"):
        self.model = None
        self.model_loaded = False
        try:
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.model_loaded = True
                logger.info("Successfully loaded BKT model.")
        except Exception as e:
            logger.warning(f"Failed to load BKT model: {e}. Using heuristic fallback.")

    def predict(self, correctness_history: list[int]) -> float:
        """
        Input: list of 1s (correct) and 0s (incorrect)
        Output: probability of next answer being correct
        """
        if self.model_loaded and hasattr(self.model, "predict_sequence"):
            try:
                return float(self.model.predict_sequence(correctness_history))
            except Exception as e:
                logger.error(f"Error predicting with BKT model: {e}")

        # Fallback Heuristic BKT
        # Start with default p_known
        p_known = 0.3
        p_learned = 0.15
        p_guess = 0.2
        p_slip = 0.1

        for correct in correctness_history:
            if correct:
                # P(L | correct) = P(correct | L) * P(L) / P(correct)
                p_correct = p_known * (1 - p_slip) + (1 - p_known) * p_guess
                p_known_given_correct = (p_known * (1 - p_slip)) / max(p_correct, 0.0001)
                p_known = p_known_given_correct + (1 - p_known_given_correct) * p_learned
            else:
                p_incorrect = p_known * p_slip + (1 - p_known) * (1 - p_guess)
                p_known_given_incorrect = (p_known * p_slip) / max(p_incorrect, 0.0001)
                p_known = p_known_given_incorrect + (1 - p_known_given_incorrect) * p_learned

        return min(max(p_known, 0.0), 1.0)

bkt_predictor = BKTPredictor()
