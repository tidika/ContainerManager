        FROM python:3.11
        WORKDIR /app
        COPY app.py /app
        EXPOSE 8000
        CMD ["python", "app.py"]"  