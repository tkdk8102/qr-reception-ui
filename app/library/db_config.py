import os

users_db = { # DB接続設定
    'host'   : 'qr-db',
    'user'   : 'root',
    'passwd' : os.getenv('MYSQL_ROOT_PASSWORD'),
    'port'   : 3306,
    'charset': 'utf8',
    'db'     : 'users'
}
