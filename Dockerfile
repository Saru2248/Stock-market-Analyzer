# Use an official, lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout for rapid log ingestion natively
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establish our working application root inside the container
WORKDIR /app

# Copy system dependencies list exclusively to heavily cache this Docker layer efficiently 
COPY requirements.txt .

# Install dependencies (updating pip first securely)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sync the entire structured Python backend application over (including local sqlite logic)
COPY . .

# Explicitly expose the FastAPI downstream port structurally natively over Docker networks
EXPOSE 8000

# Execute the local web-server interface mapping Uvicorn optimally
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
