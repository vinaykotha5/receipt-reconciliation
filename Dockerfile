FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project structure
COPY . .

# Switch to the environment directory so uvicorn can resolve api.main imports
WORKDIR /app/receipt-reconciliation

# HF Spaces uses port 7860
EXPOSE 7860

# Environment defaults (override via HF Spaces secrets)
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Start the API server — api/main.py uses sys.path to find environment/
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
