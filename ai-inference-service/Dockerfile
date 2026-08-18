# Start from official Python 3.10 image, instead of building Python and an operating system from scratch, "slim" keeps the image size down
FROM python:3.10-slim

# Set /app as the working folder inside the container, every command below this line runs from inside this folder
WORKDIR /app

# Copy ONLY the requirements file first, not the whole project yet.
# This is done on purpose: Docker caches this step, so if only change main.py later, it won't have to reinstall every package again, it only reinstalls when requirements.txt itself changes
COPY requirements.txt .

# Install every package listed in requirements.txt., --no-cache-dir keeps the image smaller by not storing pip's download cache
RUN pip install --no-cache-dir -r requirements.txt

# Now copy everything else, main.py, aqi_model.json, label_mapping.json, into the container. This happens after the install step for the caching reason explained above
COPY . .

# The command that actually runs when the container starts: launch uvicorn to run the "app" object found inside main.py, accept connections from any address (0.0.0.0), on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]