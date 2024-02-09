FROM python:3.10

RUN mkdir -p /usr/src/bot/logs
WORKDIR /usr/src/bot
COPY requirements.txt /usr/src/bot
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]