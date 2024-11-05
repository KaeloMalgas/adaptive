import logging
from flask import Flask, request, jsonify
from database import DatabaseManager
from Backend import create_api, LoadBalancer
from ml_integration import IRTModel, MLModel
from question_selection import initialize_selector
from utils import ProgressTracker
from config import Config

# Set up logging
logging.basicConfig(filename=Config.LOG_FILE, level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize database
db_manager = DatabaseManager(Config.DATABASE_URI)

# Initialize models
irt_model = IRTModel(Config.IRT_NUM_QUESTIONS, Config.IRT_NUM_EXAMINEES)
ml_model = MLModel(Config.ML_MODEL_TYPE, Config.ML_HYPERPARAMETERS)

# Get question pool
question_pool = db_manager.get_question_pool()

# Initialize question selector
selector = initialize_selector(irt_model, ml_model, question_pool, {
    'max_questions': Config.MAX_QUESTIONS_PER_TEST,
    'ability_estimation_method': Config.ABILITY_ESTIMATION_METHOD
})

# Create Flask app and API
app = create_api(irt_model, ml_model, question_pool, selector)

# Set up load balancing
load_balancer = LoadBalancer(Config.SERVERS)

@app.route('/start_test', methods=['POST'])
def start_test():
    user_id = request.json.get('user_id')
    tracker = ProgressTracker(user_id, db_manager)
    tracker.start_session()
    return jsonify({'message': 'Test started', 'session_id': tracker.current_session})

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_id = request.json.get('user_id')
    question_id = request.json.get('question_id')
    answer = request.json.get('answer')
    time_taken = request.json.get('time_taken')
    
    tracker = ProgressTracker(user_id, db_manager)
    
    # Get the next question from the selector
    next_question = selector.select_next_question(tracker.get_current_ability())
    
    # Record the answer and update ability estimate
    tracker.record_question(question_id, answer, time_taken, next_question['ability_estimate'])
    
    if next_question['status'] == 'continue':
        return jsonify({
            'status': 'continue',
            'next_question': next_question['question']
        })
    else:
        session_summary = tracker.end_session(next_question['final_ability'])
        return jsonify({
            'status': 'complete',
            'session_summary': session_summary
        })

@app.route('/get_progress', methods=['GET'])
def get_progress():
    user_id = request.args.get('user_id')
    tracker = ProgressTracker(user_id, db_manager)
    progress = tracker.get_user_progress()
    return jsonify(progress)

if __name__ == '__main__':
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG_MODE)
