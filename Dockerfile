FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install netcat for wait-for-db.sh
RUN apt-get update && apt-get install -y netcat-openbsd

# Make the wait script executable
RUN chmod +x wait-for-db.sh

# Run the wait-for-db script then start the server
CMD ["./wait-for-db.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
