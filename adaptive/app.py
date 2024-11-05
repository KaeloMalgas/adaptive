import logging
from flask import Flask, request, jsonify
from database import DatabaseManager
from ml_integration import IRTModel, MLModel
from question_selection import AdaptiveQuestionSelector
from utils import ProgressTracker
from config import Config

# Set up logging
logging.basicConfig(filename=Config.LOG_FILE, level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize components
db_manager = DatabaseManager(Config.DATABASE_URI)
irt_model = IRTModel(Config.IRT_NUM_QUESTIONS, Config.IRT_NUM_EXAMINEES)
ml_model = MLModel(Config.ML_MODEL_TYPE, Config.ML_HYPERPARAMETERS)
question_pool = db_manager.get_question_pool()
selector = AdaptiveQuestionSelector(irt_model, ml_model, question_pool)

app = Flask(__name__)

@app.route('/start_test', methods=['POST'])
def start_test():
    user_id = request.json.get('user_id')
    tracker = ProgressTracker(user_id, db_manager)
    session_id = tracker.start_session()
    return jsonify({'message': 'Test started', 'session_id': session_id})

@app.route('/get_question', methods=['POST'])
def get_question():
    user_id = request.json.get('user_id')
    session_id = request.json.get('session_id')
    current_ability = request.json.get('current_ability', 0)
    examinee_features = request.json.get('examinee_features', [])

    tracker = ProgressTracker(user_id, db_manager)
    next_question = selector.select_next_question(current_ability, examinee_features)

    if next_question is None:
        return jsonify({'status': 'complete'})

    return jsonify({
        'status': 'continue',
        'question': next_question
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_id = request.json.get('user_id')
    session_id = request.json.get('session_id')
    question_id = request.json.get('question_id')
    answer = request.json.get('answer')
    time_taken = request.json.get('time_taken')
    current_ability = request.json.get('current_ability')
    examinee_features = request.json.get('examinee_features', [])

    tracker = ProgressTracker(user_id, db_manager)
    question = next(q for q in question_pool if q['id'] == question_id)
    
    tracker.record_question(session_id, question_id, answer, time_taken, current_ability)
    
    responses = tracker.get_session_responses(session_id)
    updated_ability = selector.update_ability_estimate(responses, current_ability, examinee_features)

    return jsonify({
        'status': 'answer_recorded',
        'updated_ability': updated_ability
    })

@app.route('/end_test', methods=['POST'])
def end_test():
    user_id = request.json.get('user_id')
    session_id = request.json.get('session_id')
    final_ability = request.json.get('final_ability')

    tracker = ProgressTracker(user_id, db_manager)
    summary = tracker.end_session(session_id, final_ability)

    return jsonify({
        'status': 'test_completed',
        'summary': summary
    })

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
