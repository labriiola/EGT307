FROM postgres:15

ENV POSTGRES_DB=aqi_db
ENV POSTGRES_USER=aqi_user
ENV POSTGRES_PASSWORD=aqi_pass

COPY init.sql /docker-entrypoint-initdb.d/