CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    station VARCHAR(50),
    reading_time TIMESTAMP DEFAULT NOW(),
    pm25 FLOAT
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    station VARCHAR(50),
    prediction_time TIMESTAMP DEFAULT NOW(),
    risk_level VARCHAR(20)
);