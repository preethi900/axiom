FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (e.g. for potential compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501
# Expose Mock Service port (if running internally)
EXPOSE 8000

# Set Python path to ensure src module is found
ENV PYTHONPATH=/app

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
