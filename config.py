import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set. Please set it in the .env file.")
    # Read SUPABASE_DB_URL from .env file
    raw_db_url = os.environ.get('SUPABASE_DB_URL')
    if raw_db_url and raw_db_url.startswith('postgresql://'):
        raw_db_url = raw_db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mailman configuration
    MAIL_BACKEND = os.environ.get('MAIL_BACKEND', 'console')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("SUPABASE_DB_URL environment variable is not set. Please set it in the .env file.")
