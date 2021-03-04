import sqlite3

__connection = None

def get_connection():
    global __connection
    if __connection is None:
        __connection=sqlite3.connect('currency.db', check_same_thread=False)
    return __connection

def init_db(force: bool=False):
    '''Проверить что нужные таблицы существуют, иначе создать их

    Важно: миграции на такие таблицы вы должны производить самостоятельно!
    :param force: явно пересоздать все таблицы

    '''
    conn = get_connection()

    c = conn.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS recent_currency')
    c.execute('''CREATE TABLE IF NOT EXISTS recent_currency (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                currency_json_content   VARCHAR,
                request_time TEXT NOT NULL
            )
        '''
    )

    conn.commit()

def set_recent_request_data(user_id, currency_json, request_time):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO recent_currency (user_id, currency_json_content, request_time) VALUES(?, ?, ?)', (str(user_id), str(currency_json), str(request_time)))
    conn.commit()

def get_recent_request_data(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT  currency_json_content FROM recent_currency where user_id = ?', (user_id,))
    res = c.fetchone()
    return res

def get_recent_request_time(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT request_time FROM recent_currency WHERE user_id = ?', (user_id,))
    res = c.fetchone()
    return res