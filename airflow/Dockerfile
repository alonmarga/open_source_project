FROM apache/airflow:2.7.1-python3.9

USER root

# Install OpenJDK
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Switch back to airflow user for pip installations
USER airflow

# Copy requirements and install Python dependencies
COPY --chown=airflow:root requirements.txt .
RUN pip install --user -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/opt/
ENV DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}