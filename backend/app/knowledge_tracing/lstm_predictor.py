import os
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)

class LSTMPredictor:
    def __init__(self, model_path="app/ml/lstm_model.pkl"):
        self.model = None
        self.model_loaded = False
        try:
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.model_loaded = True
                logger.info("Successfully loaded LSTM model.")
        except Exception as e:
            logger.warning(f"Failed to load LSTM model: {e}. Using heuristic fallback.")

    def predict(self, interactions: list[list[int]]) -> float:
        """
        Input: list of up to 10 interactions. Each interaction: [topic_id, attempt_number, correct (1 or 0)]
        Output: next-answer probability
        """
        if self.model_loaded and hasattr(self.model, "predict"):
            try:
                # Assuming model expects shape (1, 10, 3)
                # Pad to 10 interactions if needed
                padded = interactions.copy()
                while len(padded) < 10:
                    padded.insert(0, [0, 0, 0]) # pad with zeros at the beginning
                if len(padded) > 10:
                    padded = padded[-10:]
                
                input_arr = np.array([padded])
                
                # Check if it's a keras/tf model or custom
                pred = self.model.predict(input_arr)
                if isinstance(pred, np.ndarray):
                    return float(pred[0][0])
                return float(pred)
            except Exception as e:
                logger.error(f"Error predicting with LSTM model: {e}")

        # Fallback Heuristic LSTM-like weighted recent average
        if not interactions:
            return 0.5
        
        # Give more weight to recent interactions
        weights = [i + 1 for i in range(len(interactions))]
        total_weight = sum(weights)
        
        weighted_sum = 0
        for i, inter in enumerate(interactions):
            # inter[2] is 'correct' (1 or 0)
            weighted_sum += (1.0 if inter[2] else 0.0) * weights[i]
            
        return min(max(weighted_sum / total_weight, 0.0), 1.0)

lstm_predictor = LSTMPredictor()
