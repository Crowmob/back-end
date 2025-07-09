FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}
ENV HOST=${HOST}
ENV PORT=${PORT}

CMD "uvicorn" "app.main:app" "--host" $HOST "--port" $PORT "--reload"

