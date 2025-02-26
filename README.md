# SwatWorks

A Flask-based web application for managing student gigs and communications at Swarthmore College.

## Project Structure

```
swatworks/
├── app/                        # Main application package
│   ├── __init__.py             # Application factory and extensions
│   ├── auth/                   # Authentication module
│   │   ├── __init__.py         # Auth blueprint initialization
│   │   ├── routes.py           # Auth routes (login, register, etc.)
│   │   ├── models.py           # User model definition
│   │   ├── forms.py            # Login and registration forms
│   │   └── templates/auth/     # Auth-specific templates
│   │       ├── login.html      # Login page template
│   │       └── register.html   # Registration page template
│   ├── gigs/                   # Gigs module
│   │   ├── __init__.py         # Gigs blueprint initialization
│   │   ├── routes.py           # Gig-related routes
│   │   ├── models.py           # Gig model definition
│   │   ├── forms.py            # Gig creation/editing forms
│   │   └── templates/gigs/     # Gig-specific templates
│   │       ├── create_gig.html # Gig creation page
│   │       └── list_gigs.html  # Gigs listing page
│   ├── messages/               # Messaging module
│   │   ├── __init__.py         # Messages blueprint initialization
│   │   ├── routes.py           # Message-related routes
│   │   ├── models.py           # Message model definition
│   │   ├── forms.py            # Message composition forms
│   │   └── templates/messages/ # Message-specific templates
│   │       ├── inbox.html      # Message inbox page
│   │       └── message.html    # Individual message view
│   ├── templates/              # Global templates
│   │   └── base.html           # Base template for all pages
│   ├── static/                 # Static files
│   │   ├── css/                # CSS stylesheets
│   │   │   └── styles.css      # Main stylesheet
│   │   └── js/                 # JavaScript files
│   │       └── scripts.js      # Main JavaScript file
│   ├── models.py               # Global models
│   ├── forms.py                # Global forms
│   └── config.py               # App-specific configuration
├── migrations/                 # Database migrations directory
├── tests/                      # Test suite
│   ├── test_auth.py            # Authentication tests
│   ├── test_gigs.py            # Gigs functionality tests
│   └── test_messages.py        # Messaging tests
├── venv/                       # Virtual environment (not commit, in gitingnor)
├── .env                        # Environment variables
├── config.py                   # Configuration settings
├── requirements.txt            # Project dependencies
└── run.py                      # Application entry point
```

## Key Files Description

### Configuration Files
- `.env`: Environment variables for development
- `config.py`: Application configuration settings
- `requirements.txt`: Python package dependencies

### Core Application Files
- `run.py`: Application entry point
- `app/__init__.py`: Application factory pattern implementation

### Module Structure
Each module (auth, gigs, messages) follows a similar structure:
- `__init__.py`: Blueprint initialization
- `routes.py`: View functions and endpoints
- `models.py`: Database models
- `forms.py`: Form classes
- `templates/`: Module-specific templates

### Templates
- `base.html`: Base template with common layout
- Module-specific templates inherit from base.html

### Static Files
- `styles.css`: Main CSS stylesheet
- `scripts.js`: Main JavaScript file

### Testing
- Separate test files for each module
- Located in the `tests/` directory 