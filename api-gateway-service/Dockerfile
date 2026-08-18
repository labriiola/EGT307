# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies.
# Done in this order (before copying the rest of the code) so Docker can reuse this step from cache if only main.py changes later, instead of reinstalling every package on every rebuild
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8080 for the gateway.
# Note: The real port mapping happens in docker-compose.yml and the Kubernetes deployment file
EXPOSE 8080

# Command to run the application: start uvicorn to run the "app" object inside main.py, accept connections from anywhere, on port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]