from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

def seed_admin():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                full_name='System Admin',
                username='admin',
                email='admin@example.com',
                role='admin',
                is_active=True
            )
            admin.set_password('adminpass123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            admin.set_password('adminpass123')
            db.session.commit()
            print("Admin password updated to 'adminpass123'")

if __name__ == '__main__':
    seed_admin()
