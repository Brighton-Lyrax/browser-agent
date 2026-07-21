FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends uvicorn && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app/main.py /app/main.py
EXPOSE 8788
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8788"]
