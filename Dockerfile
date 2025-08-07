FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libmagic1 libmagic-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}
ENV HOST=${HOST}
ENV PORT=${PORT}

CMD ["python", "-m", "app.main"]

