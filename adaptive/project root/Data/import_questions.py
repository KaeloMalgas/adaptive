import json
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Question, Base
from config import Config

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)

def import_questions():
    # Read questions from JSON file
    with open('data/questions.json', 'r') as f:
        questions = json.load(f)

    # Create database engine and session
    engine = create_engine(Config.DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Import questions to database
    for q in questions:
        new_question = Question(
            question_text=q['question'],
            options=q['options'],
            correct_answer=q['correct_answer']
        )
        session.add(new_question)

    session.commit()
    session.close()

    print("Questions have been imported to the database.")

if __name__ == "__main__":
    import_questions()
