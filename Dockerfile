FROM python:3.12.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y supervisor  \
    && rm -rf /var/lib/apt/lists/*

COPY . .
COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]