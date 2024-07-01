import sqlite3
from models import User

class SQLiteDB:
    def __init__(self, db_name='db.sqlite3'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Define table creation SQL statements
        create_users_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT
            )
        '''

        # Execute table creation SQL statements
        self.cursor.execute(create_users_table)
        self.conn.commit()

        create_queue_table = '''
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY,
                number INTEGER,
                name TEXT,
                next_time TEXT,
                is_on BOOLEAN
            )
        '''
        self.cursor.execute(create_queue_table)
        self.conn.commit()
        
        create_subs_table = '''
            CREATE TABLE IF NOT EXISTS subscription (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                queue_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(queue_id) REFERENCES queue(id)
            )
        '''
        self.cursor.execute(create_subs_table)
        self.conn.commit()

    def create_queue(self, queue_query):
        self.cursor.execute(queue_query)
        self.conn.commit()

    def get_queues(self, ):
        self.cursor.execute('''
            SELECT id,number,name,next_time,is_on FROM queue
        ''')
        return self.cursor.fetchall()
    def update_queue(self, next_time, is_on, number):
        self.cursor.execute('''
            UPDATE queue 
            SET next_time = ?,
                is_on = ?
            WHERE
                number = ?
        ''', (next_time, is_on, number))
        self.conn.commit()

    def get_queue(self, queue_id):
        self.cursor.execute('''
            SELECT * FROM queue WHERE id = ?
        ''', (queue_id,))
        return self.cursor.fetchone()

    def close_connection(self):
        self.conn.close()

    def create_user(self, chat_id, username, first_name, last_name):
        user = User(chat_id, username, first_name, last_name)
        self.cursor.execute('''
            INSERT INTO users (chat_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user.chat_id, user.username, user.first_name, user.last_name))
        self.conn.commit()
    
    def get_user_by_username(self, username):
        self.cursor.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        return self.cursor.fetchone()

    def get_user_by_chat_id(self, chat_id):
        self.cursor.execute('''
            SELECT * FROM users WHERE chat_id = ?
        ''', (chat_id,))
        return self.cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        self.cursor.execute('''
            SELECT * FROM users WHERE id = ?
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def new_subscribe(self, queue_id, user_id):
        self.cursor.execute('''
            INSERT INTO subscription (queue_id, user_id)
            VALUES (?, ?)
        ''', (queue_id, user_id))
        self.conn.commit()

    def get_subs_by_user(self, user_id):
        self.cursor.execute('''
            SELECT * FROM subscription WHERE user_id = ?
        ''', (user_id))
        return self.cursor.fetchall()
    
    def get_subs(self, ):
        self.cursor.execute('''
            SELECT * FROM subscription
        ''')
        return self.cursor.fetchall()

    def get_sub_by_user_q(self, sub_id, queue_id):
        self.cursor.execute('''
            SELECT * FROM subscription WHERE user_id = ? AND queue_id = ?
        ''', (sub_id, queue_id))
        return self.cursor.fetchone()
    
    def get_sub(self, sub_id):
        self.cursor.execute('''
            SELECT * FROM subscription WHERE id = ?
        ''', (sub_id))
        return self.cursor.fetchone()
    
    def delete_sub(self, sub_id):
        self.cursor.execute('''
            DELETE FROM subscription WHERE id = ?
        ''', (sub_id))
        self.conn.commit()