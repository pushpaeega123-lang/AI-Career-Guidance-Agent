import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hackathon-dev-secret-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # LLM Settings
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing Configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False

config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
