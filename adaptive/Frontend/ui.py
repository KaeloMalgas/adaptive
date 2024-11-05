import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, session
from question_selection import initialize_selector, select_next_question, update_ability
from ml_integration import IRTModel, MLModel

def create_app(irt_model, ml_model, question_pool, config):
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

    selector = initialize_selector(irt_model, ml_model, question_pool, config)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/start_test', methods=['POST'])
    def start_test():
        session['current_ability'] = 0
        session['responses'] = []
        session['question_count'] = 0
        return jsonify({'status': 'Test started'})

    @app.route('/get_question', methods=['GET'])
    def get_question():
        if 'current_ability' not in session:
            return jsonify({'error': 'Test not started'}), 400

        examinee_features = request.args.get('features', '').split(',')
        examinee_features = [float(f) for f in examinee_features if f]

        next_question = select_next_question(selector, session['current_ability'], examinee_features)
        
        if next_question is None:
            return jsonify({'status': 'Test complete'})

        session['question_count'] += 1
        
        return jsonify({
            'question_id': next_question['id'],
            'question_text': f"This is question {next_question['id']}",  # Replace with actual question text
            'difficulty': next_question['difficulty']
        })

    @app.route('/submit_answer', methods=['POST'])
    def submit_answer():
        if 'current_ability' not in session:
            return jsonify({'error': 'Test not started'}), 400

        data = request.json
        question_id = data['question_id']
        answer = data['answer']
        examinee_features = data['features']

        # Retrieve the question from the pool
        question = next((q for q in question_pool if q['id'] == question_id), None)
        if question is None:
            return jsonify({'error': 'Invalid question ID'}), 400

        session['responses'].append((question, answer))
        
        session['current_ability'] = update_ability(
            selector, 
            session['responses'], 
            session['current_ability'], 
            examinee_features
        )

        return jsonify({
            'status': 'Answer submitted',
            'current_ability': session['current_ability']
        })

    @app.route('/end_test', methods=['POST'])
    def end_test():
        if 'current_ability' not in session:
            return jsonify({'error': 'Test not started'}), 400

        final_ability = session['current_ability']
        num_questions = session['question_count']

        session.clear()

        return jsonify({
            'status': 'Test completed',
            'final_ability': final_ability,
            'num_questions': num_questions
        })

    @app.route('/start_test')
    def start_test_template():
        return render_template('start_test.html')

    @app.route('/view_results')
    def view_results_template():
        return render_template('view_results.html')

    @app.route('/learn_more')
    def learn_more_template():
        return render_template('learn_more.html')

    @app.route('/about')
    def about_template():
        return render_template('about.html')

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

    app = create_app(irt_model, ml_model, question_pool, config)
    app.run(debug=True)
