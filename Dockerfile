FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY *.py ./

EXPOSE 8000

CMD ["python", "main.py"]