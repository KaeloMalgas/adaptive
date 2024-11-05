import os

class Config:
    # Database
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///adaptive_testing.db')

    # IRT Model
    IRT_NUM_QUESTIONS = 100
    IRT_NUM_EXAMINEES = 1000

    # ML Model
    ML_MODEL_TYPE = 'random_forest'
    ML_HYPERPARAMETERS = {
        'n_estimators': 100,
        'max_depth': 10
    }

    # Server
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    # Logging
    LOG_FILE = 'adaptive_testing.log'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'
