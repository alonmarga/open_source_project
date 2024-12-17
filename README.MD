project/
├── docker-compose.yml       # Main orchestration file
├── .env                     # Environment variables for services
├── airflow/                 # Airflow services (scheduler, webserver, worker)
│   ├── Dockerfile           # Custom Dockerfile for Airflow
│   └── requirements.txt     # Python dependencies for Airflow
├── postgres/                # Postgres initialization scripts
│   └── init_scripts/
│       ├── 01_create_airflow_schema.sql  # Create 'airflow' schema
│       └── 02_create_raw_schema.sql      # Create 'raw' schema and sample table
├── spark/                   # Spark cluster
│   ├── master/
│   │   └── Dockerfile       # Spark Master Dockerfile
│   └── worker/
│       └── Dockerfile       # Spark Worker Dockerfile
├── fastapi_app/             # FastAPI service
│   ├── Dockerfile           # FastAPI Dockerfile
│   ├── requirements.txt     # Python dependencies for FastAPI
│   ├── fastapi_app/         # Actual FastAPI app folder
│   │   ├── main.py          # Main FastAPI application entry point
│   │   ├── api/             # API module
│   │   │   ├── __init__.py
│   │   │   ├── routes/      # Routes module
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_routes.py        # User-related endpoints
│   │   │   │   └── data_routes.py        # Data-related endpoints
│   │   └── models/          # Pydantic models
│   │       ├── __init__.py
│   │       └── user_model.py             # User data model
└── telegram_bot/            # Telegram bot service
    ├── Dockerfile           # Telegram Bot Dockerfile
    ├── requirements.txt     # Python dependencies for the bot
    └── bot/
        └── bot.py           # Telegram bot implementation
