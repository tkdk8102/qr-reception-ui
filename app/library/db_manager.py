import MySQLdb

class Connector():
    def __init__(self):
        self.__host    = ''
        self.__user    = ''
        self.__passwd  = ''
        self.__port    = ''
        self.__charset = ''
        self.__db      = ''

        self._table    = ''
        self.__conn    = None

    def connect(self, host, user, passwd, db, table, port=3306, charset='utf8'):
        self.__host    = host
        self.__user    = user
        self.__passwd  = passwd
        self.__port    = port
        self.__charset = charset
        self.__db      = db
        self.__table   = table

        self.__conn = MySQLdb.connect(
            host    = self.__host,
            port    = self.__port,
            user    = self.__user,
            passwd  = self.__passwd,
            db      = self.__db,
            charset = self.__charset
        )

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def get_guest(self):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "SELECT * FROM {}".format(self.__table)
            cursor.execute(query)
            data = cursor.fetchall()
            return data

    def get_name(self, guest_id):
        guest_id = int(guest_id)
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "SELECT kanji_name FROM {} WHERE id = %s".format(self.__table)
            cursor.execute(query, (guest_id,))
            name = cursor.fetchone()
            return name[0]

    def edit_guest(self, guest_id, attendance, kanji_name, kana_name, relation, reward, note):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "UPDATE {} SET attendance = %s, kanji_name = %s, kana_name = %s, relation = %s, reward = %s, note = %s WHERE id = %s".format(self.__table)
            cursor.execute(query, (attendance, kanji_name, kana_name, relation, reward, note, guest_id,))
            self.__conn.commit()

    def add_guest(self, gid, kanji_name, kana_name, relation='', reward='', note=''):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "INSERT INTO {} (id, gid, kanji_name, kana_name, relation, reward, note) VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s, %s)".format(self.__table)
            cursor.execute(query, (gid, kanji_name, kana_name, relation, reward, note,))
            self.__conn.commit()
            cursor = self.__conn.cursor()
            cursor.execute('SELECT LAST_INSERT_ID()')
            last_id = cursor.fetchone()
            return last_id[0]

    def del_guest(self, guest_id):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "DELETE FROM {} WHERE id = %s".format(self.__table)
            cursor.execute(query, (guest_id,))
            self.__conn.commit()

    def add_host(self, account, password):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "INSERT INTO {} (account, password) VALUES (%s, %s) ON DUPLICATE KEY UPDATE password = %s".format(self.__table)
            cursor.execute(query, (account, password, password))
            self.__conn.commit()

    def del_host(self, account):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "DELETE FROM {} WHERE account = %s".format(self.__table)
            cursor.execute(query, (account,))
            self.__conn.commit()

    def update_attend(self, gid):
        if self.__conn:
            cursor = self.__conn.cursor()
            query = "SELECT kanji_name FROM {} WHERE gid = %s".format(self.__table)
            cursor.execute(query, (gid,))
            if cursor.rowcount:
                name = cursor.fetchone()
                cursor = self.__conn.cursor()
                query = "UPDATE {} SET attendance = %s WHERE gid = %s".format(self.__table)
                cursor.execute(query, (1, gid,))
                self.__conn.commit()
                return name[0]
            else:
                return ''