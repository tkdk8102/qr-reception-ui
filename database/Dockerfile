FROM mariadb:10.6.5

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    locales-all \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

COPY init.sql /docker-entrypoint-initdb.d/
