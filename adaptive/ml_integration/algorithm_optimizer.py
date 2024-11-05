# ml_integration/algorithm_optimizer.py

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import pearsonr

class AlgorithmOptimizer:
    def __init__(self, data_collector, irt_model, ml_model):
        self.data_collector = data_collector
        self.irt_model = irt_model
        self.ml_model = ml_model
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

    def analyze_performance(self):
        data = self.data_collector.get_recent_data()
        metrics = {
            'avg_questions': np.mean([session['num_questions'] for session in data]),
            'avg_duration': np.mean([session['duration'] for session in data]),
            'completion_rate': sum([session['completed'] for session in data]) / len(data)
        }
        return metrics

    def validate_irt_parameters(self):
        data = self.data_collector.get_all_data()
        estimated_abilities = [session['estimated_ability'] for session in data]
        true_abilities = [session['true_ability'] for session in data]  # Assuming we have this for validation
        correlation, _ = pearsonr(estimated_abilities, true_abilities)
        return {'irt_ability_correlation': correlation}

    def train_ml_model(self):
        data = self.data_collector.get_all_data()
        X = np.array([session['features'] for session in data])
        y = np.array([session['estimated_ability'] for session in data])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.rf_model.fit(X_train, y_train)
        accuracy = self.rf_model.score(X_test, y_test)
        return {'ml_model_accuracy': accuracy}

    def optimize_algorithm(self):
        performance_metrics = self.analyze_performance()
        irt_validation = self.validate_irt_parameters()
        ml_performance = self.train_ml_model()

        # Update IRT model parameters based on validation results
        if irt_validation['irt_ability_correlation'] < 0.7:  # Threshold for acceptable correlation
            self.irt_model.recalibrate()

        # Update ML model if performance improved
        if ml_performance['ml_model_accuracy'] > self.ml_model.get_accuracy():
            self.ml_model.update(self.rf_model)

        return {**performance_metrics, **irt_validation, **ml_performance}

    def a_b_test(self, new_algorithm, test_size=0.1):
        data = self.data_collector.get_recent_data(limit=1000)  # Get last 1000 test sessions
        control_group = data[:int(len(data) * (1 - test_size))]
        test_group = data[int(len(data) * (1 - test_size)):]

        control_performance = self.evaluate_algorithm(self.irt_model, control_group)
        test_performance = self.evaluate_algorithm(new_algorithm, test_group)

        return {
            'control': control_performance,
            'test': test_performance,
            'improvement': test_performance['avg_questions'] < control_performance['avg_questions']
        }

    def evaluate_algorithm(self, algorithm, data):
        # Simulate running the algorithm on historical data
        avg_questions = np.mean([algorithm.simulate_test(session) for session in data])
        return {'avg_questions': avg_questions}

