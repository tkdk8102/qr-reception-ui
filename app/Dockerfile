FROM python:3.8.7-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip \
    mysqlclient==2.0.3 flask==1.1.2 gunicorn==20.0.4

CMD while true; do gunicorn --bind 0.0.0.0:80 main:app; done
