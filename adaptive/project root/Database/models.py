from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    test_sessions = relationship('TestSession', back_populates='user')

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    difficulty = Column(Float, nullable=False)
    discrimination = Column(Float, nullable=False)
    guessing = Column(Float, nullable=False)

    responses = relationship('Response', back_populates='question')

class TestSession(Base):
    __tablename__ = 'test_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    final_ability = Column(Float)

    user = relationship('User', back_populates='test_sessions')
    responses = relationship('Response', back_populates='test_session')

class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True)
    test_session_id = Column(Integer, ForeignKey('test_sessions.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer = Column(Boolean, nullable=False)
    response_time = Column(Float)  # in seconds
    ability_estimate = Column(Float)

    test_session = relationship('TestSession', back_populates='responses')
    question = relationship('Question', back_populates='responses')

def init_db(engine):
    Base.metadata.create_all(engine)
