FROM python:3.14.0-trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y --fix-missing \
    && apt-get install gcc build-essential nano vim bgpq4 python3-venv python3-pip -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m app && mkdir -p /app

RUN pip3 install --no-cache-dir flask uwsgi --break-system-package

COPY . /app

RUN chown -R app:app /app && rm -f /app/static/example-geofeed.yml

USER app

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt --break-system-package

EXPOSE 5000

CMD ["uwsgi","--ini","uwsgi.ini"]