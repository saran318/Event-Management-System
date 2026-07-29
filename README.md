# Event Management System

## Project Overview
The Event Management System is a robust, web-based platform designed for organizing, managing, and registering for events. Built from the ground up with Python, Flask, SQLAlchemy, and Bootstrap, this application streamlines event coordination for administrators while offering a highly responsive, seamless user experience for participants.

### Project Objectives
- Provide a secure and intuitive platform for event registration.
- Enable administrators to actively manage event lifecycle and track participant metrics.
- Deliver automated, reliable email notifications without interrupting the user experience.
- Maintain a clean, scalable architectural pattern for future enterprise deployment.

## Technology Stack

### Backend
- **Python**: Core programming language.
- **Flask**: Web framework providing routing and application state.
- **SQLAlchemy**: ORM for database modeling and query execution.
- **Flask-Login**: Session management and authentication.
- **Flask-WTF**: Form validation and Cross-Site Request Forgery (CSRF) protection.
- **Flask-Mailman**: Asynchronous email delivery integration.

### Database
- **PostgreSQL**: Production database (compatible with Supabase).
- **SQLite**: Memory-based database utilized exclusively for automated testing.

### Frontend
- **HTML5 & CSS3**: Core structural and styling languages.
- **Bootstrap 5**: Responsive layout framework and component library.
- **JavaScript**: Client-side logic for dynamic UI elements.

### Testing
- **Pytest**: Automated testing framework.
- **pytest-cov**: Test coverage reporting.

## Features
- **Authentication**: Secure user registration, login, logout, and active-session management.
- **Authorization (RBAC)**: Strict Role-Based Access Control enforcing `admin` and `user` privileges at both the UI and routing layers.
- **Event Management**: Full CRUD (Create, Read, Update, Delete) capabilities for administrators to govern events.
- **Registration Management**: Participants can browse events, register, view registration histories, and cancel bookings.
- **Participants Management**: Dedicated administrative dashboard tracking event capacity, user details, and registration dates.
- **Email Notifications**: Automated HTML/TXT email dispatch for registration confirmations, cancellations, event updates, and 24-hour reminders.
- **Responsive UI**: Fully mobile-responsive interface utilizing a polished Bootstrap 5 design.
- **CSRF Protection**: Comprehensive endpoint security via Flask-WTF preventing forged requests.
- **Automated Testing**: 100% passing integration suite with >80% coverage ensuring stability across services.

## Project Architecture
The repository adheres to strict software engineering design patterns to ensure maintainability:
- **Application Factory**: Configures and initializes the Flask application dynamically, allowing seamless switching between Testing and Production environments.
- **Blueprints**: Modules are split into logical routing components (`auth`, `events`, `registrations`, `dashboard`).
- **Service Layer**: Extracts heavy business logic, database transactions, and eager-loading optimizations out of the controllers to keep routes exclusively focused on HTTP responses.
- **Templates & Static Files**: Leverages Jinja2 for dynamic HTML generation paired with isolated CSS/JS assets.

## System Requirements
- Python 3.8+
- PostgreSQL 12+ (if deploying to production)
- pip (Python package installer)

## Quick Start & Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd event_management_system
   ```

2. **Create and activate a virtual environment**:
   - Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
The application relies on a `.env` file to securely load configuration variables. 

1. In the root directory, locate the `.env.example` file.
2. Rename or copy `.env.example` to a new file named `.env`:
   - Windows: `copy .env.example .env`
   - macOS/Linux: `cp .env.example .env`
3. Open the newly created `.env` file and replace the placeholder values with your actual credentials:
   ```env
   # Database Connection
   SUPABASE_DB_URL=postgresql://username:password@host:6543/postgres

   # Security
   SECRET_KEY=your_secure_random_secret_key

   # SMTP Configuration (For emails to work)
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   MAIL_DEFAULT_SENDER=noreply@example.com
   ```
*(Do not commit your `.env` file to version control. It is explicitly ignored in `.gitignore`.)*

## Database Setup & Running the Application

1. **Initialize the Database**:
   Run the database creation script to construct all required tables (utilizing the URI defined in your `.env`):
   ```bash
   python create_db.py
   ```

2. **Start the Application**:
   Launch the Flask development server:
   ```bash
   python run.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Running with Docker (Recommended)

The easiest way to run the application is using Docker. A pre-built image is available on Docker Hub.

1. **Create your `.env` file** (as described in the Environment Variables section).
2. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```
3. **Alternative - Run with Docker CLI**:
   ```bash
   docker run -d -p 5000:5000 --env-file .env saran318/eventverse-app:latest
   ```

The application will be accessible at `http://localhost:5000`.

## Testing

The project contains a comprehensive automated test suite utilizing `pytest`.

To run the tests and generate a coverage report:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

**Expected Output:**
You should see 40 tests pass with an aggregate coverage exceeding 80%, signifying fully verified structural integrity across all core components.

## Folder Structure
```text
event_management_system/
├── app/
│   ├── routes/             # Blueprint routing controllers
│   ├── services/           # Business logic and database transactions
│   ├── static/             # CSS, JS, and image assets
│   ├── templates/          # Jinja2 HTML templates
│   ├── __init__.py         # App factory configuration
│   ├── extensions.py       # Flask extensions initialization
│   ├── exceptions.py       # Custom service exceptions
│   ├── decorators.py       # RBAC wrappers
│   └── models.py           # SQLAlchemy database schemas
├── scripts/                # Historical or debugging utility scripts
├── tests/                  # Automated integration test suite
├── .env.example            # Environment configuration template
├── .gitignore              # Ignored files configuration
├── config.py               # Environment parsing
├── create_db.py            # Database initialization script
├── LICENSE                 # MIT License specification
├── README.md               # Project documentation
├── requirements.txt        # Frozen dependency map
└── run.py                  # Application entry point
```

## Screenshots
- **Home Page**: `![Home UI](link-to-home-image)`
- **Login**: `![Login UI](link-to-login-image)`
- **Register**: `![Register UI](link-to-register-image)`
- **Dashboard**: `![Dashboard UI](link-to-dashboard-image)`
- **Events List**: `![Events UI](link-to-events-image)`
- **Event Details**: `![Event Details UI](link-to-event-details-image)`
- **Participants**: `![Participants UI](link-to-participants-image)`
- **My Registrations**: `![My Registrations UI](link-to-registrations-image)`

## Known Limitations
- Background email processing currently depends heavily on the Flask-Mailman fault-tolerance wrapping. For extreme high-volume production loads (10,000+ emails), integration with Celery or Redis for dedicated asynchronous task queuing would be required.

## Future Enhancements
- **Password Reset**: Implement secure token-based email password recovery.
- **Event Images**: Allow organizers to upload event banners via AWS S3 or Supabase Storage.
- **Calendar Integration**: Provide `.ics` file generation and Google Calendar deep links for registered events.
- **REST API**: Decouple the backend to serve a standalone JSON API for mobile applications.
- **CI/CD**: Implement GitHub Actions for automated testing and deployment.

## License
This project is licensed under the MIT License. See the `LICENSE` file for full details.
