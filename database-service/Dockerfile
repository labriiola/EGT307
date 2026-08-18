# Start from the official Postgres image instead of installing a database engine from scratch
FROM postgres:15

# Set the default database name, username, and password for this container.
# Postgres's own image is built to specifically look for these exact environment variable names and use them to auto-create the database and user the very first time the container starts
ENV POSTGRES_DB=aqi_db
ENV POSTGRES_USER=aqi_user
ENV POSTGRES_PASSWORD=aqi_pass

# Copy SQL file into a special folder Postgres watches on startup.
# Any .sql file placed in /docker-entrypoint-initdb.d/ gets run automatically the very first time the container starts, this is how the two tables (readings, predictions) get created without manually connecting and typing CREATE TABLE ourselves
COPY init.sql /docker-entrypoint-initdb.d/