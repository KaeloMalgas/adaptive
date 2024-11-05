from flask import Flask
from flask_restful import Api, Resource, reqparse
from question_selection import initialize_selector, select_next_question, update_ability
from ml_integration import IRTModel, MLModel

class TestSession(Resource):
    def __init__(self, selector, irt_model, ml_model):
        self.selector = selector
        self.irt_model = irt_model
        self.ml_model = ml_model
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('ability', type=float, required=True)
        self.parser.add_argument('features', type=list, location='json', required=True)
        self.parser.add_argument('question_id', type=int)
        self.parser.add_argument('answer', type=bool)

    def get(self):
        args = self.parser.parse_args()
        next_question = select_next_question(self.selector, args['ability'], args['features'])
        if next_question is None:
            return {'status': 'Test complete'}, 200
        return {
            'question_id': next_question['id'],
            'question_text': f"This is question {next_question['id']}",  # Replace with actual question text
            'difficulty': next_question['difficulty']
        }, 200

    def post(self):
        args = self.parser.parse_args()
        question = next((q for q in self.selector.question_pool if q['id'] == args['question_id']), None)
        if question is None:
            return {'error': 'Invalid question ID'}, 400

        responses = [(question, args['answer'])]
        updated_ability = update_ability(self.selector, responses, args['ability'], args['features'])
        return {'updated_ability': updated_ability}, 200

def create_api(irt_model, ml_model, question_pool, config):
    app = Flask(__name__)
    api = Api(app)

    selector = initialize_selector(irt_model, ml_model, question_pool, config)

    api.add_resource(TestSession, '/test_session', 
                     resource_class_kwargs={'selector': selector, 'irt_model': irt_model, 'ml_model': ml_model})

    return app

# This part is for testing the Flask app directly
if __name__ == '__main__':
    # Create mock models and question pool for testing
    irt_model = IRTModel(num_questions=100, num_examinees=1000)
    ml_model = MLModel(model_type='random_forest')
    question_pool = [
        {'id': i, 'difficulty': irt_model.difficulty[i], 
         'discrimination': irt_model.discrimination[i], 
         'guessing': irt_model.guessing[i]}
        for i in range(100)
    ]
    config = {'max_questions': 20, 'ability_estimation_method': 'EAP'}

    app = create_api(irt_model, ml_model, question_pool, config)
    app.run(debug=True)
