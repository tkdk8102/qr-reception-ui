FROM python:3.8.7-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip \
    mysqlclient==2.0.3 flask==1.1.2 gunicorn==20.0.4 \
    flask_login==0.5.0 flask-bcrypt==0.7.1 flask_sqlalchemy==2.5.1 \
    chardet==4.0.0 qrcode==7.3.1 Pillow==9.0.0

CMD while true; do gunicorn --bind 0.0.0.0:80 main:app; done
