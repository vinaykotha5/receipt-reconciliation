FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project structure
COPY . .

# HF Spaces uses port 7860
EXPOSE 7860

# Environment defaults (override via HF Spaces secrets)
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV ENABLE_WEB_INTERFACE=true

# Start the API server from receipt-reconciliation subfolder
CMD ["python", "-m", "uvicorn", "receipt-reconciliation.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
