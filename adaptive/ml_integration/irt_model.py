import numpy as np
from scipy import optimize

class IRTModel:
    def __init__(self, num_questions, num_examinees):
        self.num_questions = num_questions
        self.num_examinees = num_examinees
        self.difficulty = np.random.randn(num_questions)
        self.discrimination = np.abs(np.random.randn(num_questions))
        self.guessing = np.random.uniform(0, 0.5, num_questions)
        self.ability = np.random.randn(num_examinees)

    def probability(self, ability, difficulty, discrimination, guessing):
        return guessing + (1 - guessing) / (1 + np.exp(-discrimination * (ability - difficulty)))

    def log_likelihood(self, params, responses):
        difficulty, discrimination, guessing, ability = self._unpack_params(params)
        prob = self.probability(ability[:, np.newaxis], difficulty, discrimination, guessing)
        log_likelihood = np.sum(responses * np.log(prob) + (1 - responses) * np.log(1 - prob))
        return -log_likelihood

    def fit(self, responses, max_iter=1000):
        initial_params = np.concatenate([
            self.difficulty,
            self.discrimination,
            self.guessing,
            self.ability
        ])

        result = optimize.minimize(
            self.log_likelihood,
            initial_params,
            args=(responses,),
            method='L-BFGS-B',
            options={'maxiter': max_iter}
        )

        self.difficulty, self.discrimination, self.guessing, self.ability = self._unpack_params(result.x)

    def _unpack_params(self, params):
        difficulty = params[:self.num_questions]
        discrimination = params[self.num_questions:2*self.num_questions]
        guessing = params[2*self.num_questions:3*self.num_questions]
        ability = params[3*self.num_questions:]
        return difficulty, discrimination, guessing, ability

    def estimate_ability(self, responses):
        initial_ability = np.mean(self.ability)
        result = optimize.minimize_scalar(
            lambda a: -np.sum(responses * np.log(self.probability(a, self.difficulty, self.discrimination, self.guessing)) + 
                              (1 - responses) * np.log(1 - self.probability(a, self.difficulty, self.discrimination, self.guessing))),
            method='brent'
        )
        return result.x

# Example usage
if __name__ == "__main__":
    num_questions = 20
    num_examinees = 100
    
    # Generate random response data
    responses = np.random.randint(2, size=(num_examinees, num_questions))
    
    # Create and fit the IRT model
    irt_model = IRTModel(num_questions, num_examinees)
    irt_model.fit(responses)
    
    print("Estimated difficulties:", irt_model.difficulty)
    print("Estimated discriminations:", irt_model.discrimination)
    print("Estimated guessing parameters:", irt_model.guessing)
    print("Estimated abilities:", irt_model.ability)

    # Estimate ability for a new examinee
    new_responses = np.random.randint(2, size=num_questions)
    estimated_ability = irt_model.estimate_ability(new_responses)
    print("Estimated ability for new examinee:", estimated_ability)
