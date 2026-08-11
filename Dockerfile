FROM python:3.14-slim
LABEL maintainer="guihhb.zl@gmail.com"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#Garante que internamente o container sempre escute na 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]