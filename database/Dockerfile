FROM mysql:8.0

ENV DEBCONF_NOWARNINGS=yes

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    locales-all \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

COPY init.sql /docker-entrypoint-initdb.d/
COPY mysql/my.cnf /etc/mysql/conf.d
