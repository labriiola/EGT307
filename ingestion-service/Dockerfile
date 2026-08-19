# Start a small Python 3.10 image
FROM python:3.10-slim

# Set /app as the working folder inside the container
WORKDIR /app

# Copy only the requirements file first, so Docker can reuse this step from cache if only main.py changes later, avoids reinstalling packages on every single rebuild
COPY requirements.txt .

# Install every package listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else, main.py, cleaned_data.csv, into the container
COPY . .

# Run main.py directly (not through uvicorn, since ingestion has no web server, it only sends requests outward, never receives any).
# The "-u" flag runs Python unbuffered, meaning print() statements show up immediately in the logs instead of being held back, without this flag, the container looks silent even while it's actually working
CMD ["python", "-u", "main.py"]