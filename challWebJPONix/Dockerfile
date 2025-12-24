FROM python:3.12-bookworm
WORKDIR /app
COPY app/ /app
EXPOSE 8080
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
