FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Define entrypoint using gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
