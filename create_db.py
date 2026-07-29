from app import create_app
from app.extensions import db
from app.models import User, Event, Registration # Ensure models are imported so they are registered with SQLAlchemy

app = create_app()

def init_db():
    with app.app_context():
        print("Dropping all existing database tables...")
        db.drop_all()
        print("Creating all database tables...")
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
