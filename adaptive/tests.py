import unittest
from app import app
from database import DatabaseManager
from config import TestingConfig

class AdaptiveTestingTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        self.db_manager = DatabaseManager(TestingConfig.DATABASE_URI)
        
        # Set up test data
        self.user_id = self.db_manager.add_user('testuser', 'test@example.com', 'password')
        for i in range(10):
            self.db_manager.add_question(f"Question {i}", 0.5, 1.0, 0.2)

    def test_start_test(self):
        response = self.client.post('/start_test', json={'user_id': self.user_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('session_id', response.json)

    def test_get_question(self):
        start_response = self.client.post('/start_test', json={'user_id': self.user_id})
        session_id = start_response.json['session_id']
        
        response = self.client.post('/get_question', json={
            'user_id': self.user_id,
            'session_id': session_id,
            'current_ability': 0,
            'examinee_features': [1, 0, 1, 0, 1]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('question', response.json)

    def test_submit_answer(self):
        start_response = self.client.post('/start_test', json={'user_id': self.user_id})
        session_id = start_response.json['session_id']
        
        question_response = self.client.post('/get_question', json={
            'user_id': self.user_id,
            'session_id': session_id,
            'current_ability': 0,
            'examinee_features': [1, 0, 1, 0, 1]
        })
        question_id = question_response.json['question']['id']
        
        response = self.client.post('/submit_answer', json={
            'user_id': self.user_id,
            'session_id': session_id,
            'question_id': question_id,
            'answer': True,
            'time_taken': 10.5,
            'current_ability': 0,
            'examinee_features': [1, 0, 1, 0, 1]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('updated_ability', response.json)

    def test_end_test(self):
        start_response = self.client.post('/start_test', json={'user_id': self.user_id})
        session_id = start_response.json['session_id']
        
        response = self.client.post('/end_test', json={
            'user_id': self.user_id,
            'session_id': session_id,
            'final_ability': 0.75
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('summary', response.json)

if __name__ == '__main__':
    unittest.main()
