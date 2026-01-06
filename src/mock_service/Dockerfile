FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
# If no requirements.txt exists yet, we install manually for the mock service
RUN pip install fastapi uvicorn pydantic

COPY src/mock_service /app/src/mock_service

# Expose the port
EXPOSE 8000

CMD ["uvicorn", "src.mock_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
