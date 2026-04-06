# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install the libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code
COPY src ./src/
COPY app.py .

# Expose the port and run the Flask Server using Gunicorn
EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]