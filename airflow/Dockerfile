FROM apache/airflow:2.7.1
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONPATH=/opt/
ENV DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}