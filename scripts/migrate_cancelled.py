import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

def run_migration():
    with app.app_context():
        try:
            # Check if column exists first
            print("Adding is_cancelled column to events table...")
            db.session.execute(text("ALTER TABLE events ADD COLUMN is_cancelled BOOLEAN DEFAULT FALSE;"))
            db.session.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Error during migration (column might already exist): {e}")
            db.session.rollback()

if __name__ == '__main__':
    run_migration()
