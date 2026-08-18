-- Table 1: stores raw sensor readings coming in from ingestion
CREATE TABLE readings (
    id SERIAL PRIMARY KEY,          -- auto incrementing unique ID for each row
    station VARCHAR(50),            -- which monitoring station this reading came from
    reading_time TIMESTAMP DEFAULT NOW(),  -- automatically filled with the current time
    pm25 FLOAT                      -- the PM2.5 pollutant reading itself
);

-- Table 2: stores the AI model's predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,              -- auto incrementing unique ID for each row
    station VARCHAR(50),                -- which station this prediction is for
    prediction_time TIMESTAMP DEFAULT NOW(),  -- automatically filled with the current time
    risk_level VARCHAR(20)              -- the model's predicted risk category (e.g. "Hazardous")
);