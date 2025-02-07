FROM postgres:15

RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Copy the SQL template without a .sql extension to prevent auto-execution.
COPY init.template.sql /docker-entrypoint-initdb.d/init.template

# Copy the wrapper script as "01-init-wrapper.sh" so it runs in the proper order.
COPY init-wrapper.sh /docker-entrypoint-initdb.d/01-init-wrapper.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-init-wrapper.sh
