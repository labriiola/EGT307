# Start a Python 3.10 image
FROM python:3.10-slim

# Set /app as the working folder inside the container
WORKDIR /app

# Copy the requirements file first, so Docker can reuse this step from cache when only main.py changes later
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else,  main.py,  into the container
COPY . .

# Documents which port this container listens on. Mapping happens in docker-compose.yml and the Kubernetes deployment file
EXPOSE 8501

# The command that runs when the container starts:
# launch Streamlit specifically (not uvicorn, since this is a Streamlit app, not a FastAPI one), run main.py, listen on port 8501,
# and accept connections from any address so the dashboard is reachable from outside the container
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]