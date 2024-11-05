from .irt_model import IRTModel
from .ml_model import MLModel
import numpy as np

class IntegratedModel:
    def __init__(self, num_questions, num_examinees):
        self.irt_model = IRTModel(num_questions, num_examinees)
        self.ml_model = MLModel()

    def fit(self, responses, features):
        self.irt_model.fit(responses)
        
        # Combine IRT parameters with features for ML model
        X = np.column_stack([
            self.irt_model.difficulty,
            self.irt_model.discrimination,
            self.irt_model.guessing,
            features
        ])
        y = responses.flatten()
        
        return self.ml_model.train(X, y)

    def estimate_ability(self, responses, features):
        irt_ability = self.irt_model.estimate_ability(responses)
        
        X = np.column_stack([
            self.irt_model.difficulty,
            self.irt_model.discrimination,
            self.irt_model.guessing,
            features
        ])
        ml_prob = self.ml_model.predict_proba(X)
        
        # Combine IRT and ML predictions (you can adjust this combination method)
        combined_ability = 0.7 * irt_ability + 0.3 * ml_prob
        
        return combined_ability

# Export the integrated model
__all__ = ['IntegratedModel']

# Version of the ml_integration package
__version__ = '0.1.0'
