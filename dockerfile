FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Copy entrypoint script
COPY entrypoint.sh .

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command (for gunicorn container)
CMD ["gunicorn", "webhook.wsgi:application", "--bind", "0.0.0.0:8000"]
