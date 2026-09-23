FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY web/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "web.main"]