from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User, Question, TestSession, Response
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def add_user(self, username, email, password_hash):
        session = self.get_session()
        new_user = User(username=username, email=email, password_hash=password_hash)
        session.add(new_user)
        session.commit()
        user_id = new_user.id
        session.close()
        return user_id

    def add_question(self, content, difficulty, discrimination, guessing):
        session = self.get_session()
        new_question = Question(content=content, difficulty=difficulty, 
                                discrimination=discrimination, guessing=guessing)
        session.add(new_question)
        session.commit()
        question_id = new_question.id
        session.close()
        return question_id

    def start_test_session(self, user_id):
        session = self.get_session()
        new_test_session = TestSession(user_id=user_id)
        session.add(new_test_session)
        session.commit()
        test_session_id = new_test_session.id
        session.close()
        return test_session_id

    def add_response(self, test_session_id, question_id, answer, response_time, ability_estimate):
        session = self.get_session()
        new_response = Response(test_session_id=test_session_id, question_id=question_id,
                                answer=answer, response_time=response_time, 
                                ability_estimate=ability_estimate)
        session.add(new_response)
        session.commit()
        response_id = new_response.id
        session.close()
        return response_id

    def end_test_session(self, test_session_id, final_ability):
        session = self.get_session()
        test_session = session.query(TestSession).get(test_session_id)
        if test_session:
            test_session.end_time = datetime.utcnow()
            test_session.final_ability = final_ability
            session.commit()
        session.close()

    def get_user_test_history(self, user_id):
        session = self.get_session()
        user = session.query(User).get(user_id)
        if user:
            test_history = [
                {
                    'test_id': test.id,
                    'start_time': test.start_time,
                    'end_time': test.end_time,
                    'final_ability': test.final_ability,
                    'num_questions': len(test.responses)
                }
                for test in user.test_sessions
            ]
        else:
            test_history = []
        session.close()
        return test_history

    def get_question_pool(self):
        session = self.get_session()
        questions = session.query(Question).all()
        question_pool = [
            {
                'id': q.id,
                'content': q.content,
                'difficulty': q.difficulty,
                'discrimination': q.discrimination,
                'guessing': q.guessing
            }
            for q in questions
        ]
        session.close()
        return question_pool

# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager('sqlite:///adaptive_testing.db')

    # Add a user
    user_id = db_manager.add_user('testuser', 'test@example.com', 'hashed_password')

    # Add some questions
    for i in range(5):
        db_manager.add_question(f"Question {i+1}", 0.5, 1.0, 0.2)

    # Start a test session
    test_session_id = db_manager.start_test_session(user_id)

    # Add some responses
    db_manager.add_response(test_session_id, 1, True, 10.5, 0.6)
    db_manager.add_response(test_session_id, 2, False, 15.2, 0.4)

    # End the test session
    db_manager.end_test_session(test_session_id, 0.7)

    # Get user test history
    history = db_manager.get_user_test_history(user_id)
    print("User test history:", history)

    # Get question pool
    question_pool = db_manager.get_question_pool()
    print("Question pool:", question_pool)
