import json
from datetime import datetime

class ProgressTracker:
    def __init__(self, user_id, db_manager):
        self.user_id = user_id
        self.db_manager = db_manager
        self.current_session = None
        self.session_start_time = None
        self.question_history = []

    def start_session(self):
        self.current_session = self.db_manager.start_test_session(self.user_id)
        self.session_start_time = datetime.now()
        self.question_history = []

    def record_question(self, question_id, response, time_taken, ability_estimate):
        if self.current_session is None:
            raise ValueError("Session not started. Call start_session() first.")

        self.question_history.append({
            'question_id': question_id,
            'response': response,
            'time_taken': time_taken,
            'ability_estimate': ability_estimate
        })

        self.db_manager.add_response(
            self.current_session,
            question_id,
            response,
            time_taken,
            ability_estimate
        )

    def end_session(self, final_ability):
        if self.current_session is None:
            raise ValueError("No active session to end.")

        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        self.db_manager.end_test_session(self.current_session, final_ability)

        session_summary = {
            'session_id': self.current_session,
            'start_time': self.session_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': session_duration,
            'final_ability': final_ability,
            'questions_answered': len(self.question_history)
        }

        self.current_session = None
        self.session_start_time = None
        return session_summary

    def get_user_progress(self):
        user_history = self.db_manager.get_user_test_history(self.user_id)
        
        total_questions = sum(session['num_questions'] for session in user_history)
        total_time = sum((session['end_time'] - session['start_time']).total_seconds() for session in user_history)
        average_ability = sum(session['final_ability'] for session in user_history) / len(user_history) if user_history else 0

        return {
            'total_sessions': len(user_history),
            'total_questions': total_questions,
            'total_time': total_time,
            'average_ability': average_ability,
            'last_session': user_history[-1] if user_history else None
        }

    def get_ability_trend(self):
        user_history = self.db_manager.get_user_test_history(self.user_id)
        return [
            {
                'session_id': session['test_id'],
                'timestamp': session['end_time'].isoformat(),
                'ability': session['final_ability']
            }
            for session in user_history
        ]

    def export_session_data(self, session_id):
        session_data = self.db_manager.get_session_data(session_id)
        if session_data is None:
            raise ValueError(f"No session found with id {session_id}")

        export_data = {
            'session_id': session_id,
            'user_id': self.user_id,
            'start_time': session_data['start_time'].isoformat(),
            'end_time': session_data['end_time'].isoformat(),
            'final_ability': session_data['final_ability'],
            'questions': [
                {
                    'question_id': response['question_id'],
                    'response': response['answer'],
                    'time_taken': response['response_time'],
                    'ability_estimate': response['ability_estimate']
                }
                for response in session_data['responses']
            ]
        }

        return json.dumps(export_data, indent=2)

# Example usage
if __name__ == "__main__":
    from database import DatabaseManager

    db_manager = DatabaseManager('sqlite:///adaptive_testing.db')
    user_id = 1  # Assume this user exists

    tracker = ProgressTracker(user_id, db_manager)

    # Start a new session
    tracker.start_session()

    # Record some questions
    tracker.record_question(1, True, 10.5, 0.6)
    tracker.record_question(2, False, 15.2, 0.4)
    tracker.record_question(3, True, 8.7, 0.7)

    # End the session
    session_summary = tracker.end_session(0.7)
    print("Session summary:", session_summary)

    # Get user progress
    progress = tracker.get_user_progress()
    print("User progress:", progress)

    # Get ability trend
    trend = tracker.get_ability_trend()
    print("Ability trend:", trend)

    # Export session data
    session_data = tracker.export_session_data(session_summary['session_id'])
    print("Exported session data:", session_data)
