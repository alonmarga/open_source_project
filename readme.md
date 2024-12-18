```
project-root/
│
├── docker-compose.yml          # Docker Compose file to define services
├── .env                        # Environment variables for the project
├── README.md                   # Project description and setup instructions
│
├── app/                        # FastAPI app
│   ├── Dockerfile              # Dockerfile for FastAPI
│   ├── requirements.txt        # Python dependencies for FastAPI
│   ├── main.py                 # Entry point for FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── __init__.py             # Marks the app as a Python package
│   ├── routers/                # API route definitions
│   │   ├── __init__.py         # Marks routers as a Python package
│   │   ├── users.py            # User-related routes
│   │   ├── items.py            # Item-related routes
│   │   └── routers.py          # Centralized router configuration
│   ├── db/                     # Database utilities
│   │   ├── base.py             # SQLAlchemy Base definition
│   │   ├── connection.py       # Database connection setup
│   │   ├── db.py               # Database initialization utilities
│   │   └── __init__.py         # Marks db as a Python package
│
├── bot/                        # Telegram bot
│   ├── Dockerfile              # Dockerfile for Telegram bot
│   ├── requirements.txt        # Python dependencies for Telegram bot
│   ├── main.py                 # Entry point for the Telegram bot
│
├── postgres/                   # PostgreSQL-related files
│   ├── init.sql                # SQL initialization script for the database
│   ├── data/                   # Directory to store database data (volume mapping)
```