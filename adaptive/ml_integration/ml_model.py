import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

class MLModel:
    def __init__(self, n_estimators=100, max_depth=10):
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'auc_score': auc_score
        }

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]

# Example usage
if __name__ == "__main__":
    # Generate some dummy data
    np.random.seed(42)
    X = np.random.rand(1000, 5)
    y = (X[:, 0] + X[:, 1] > 1).astype(int)

    # Create and train the model
    ml_model = MLModel()
    results = ml_model.train(X, y)

    print("Training results:", results)

    # Make predictions
    X_new = np.random.rand(10, 5)
    predictions = ml_model.predict(X_new)
    probabilities = ml_model.predict_proba(X_new)

    print("Predictions:", predictions)
    print("Probabilities:", probabilities)
