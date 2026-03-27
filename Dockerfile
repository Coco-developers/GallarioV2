FROM python:3.11-slim

WORKDIR /app

# Install the libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code
COPY src ./src/
COPY app.py .

# Expose the port and run the Flask Server
EXPOSE 8000
CMD ["python", "app.py", "--server", "--port", "8000"]