import sqlite3
from energybot.db.models import User

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
        
        #update_queue_table = '''
        #    ALTER TABLE queue
        #        ADD current_state BOOLEAN
        #'''
        #self.cursor.execute(update_queue_table)
        #self.conn.commit()

        create_queue_table = '''
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY,
                number INTEGER,
                name TEXT,
                current_time TEXT,
                current_state BOOLEAN,
                next_time TEXT,
                next_state BOOLEAN
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

        create_global_table = '''
            CREATE TABLE IF NOT EXISTS global (
                id INTEGER PRIMARY KEY,
                name INTEGER,
                value TEXT
            )
        '''
        self.cursor.execute(create_global_table)
        self.conn.commit()


    def run_query(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def get_queues(self, ):
        self.cursor.execute('''
            SELECT id,number,name,next_time,next_state FROM queue
        ''')
        return self.cursor.fetchall()
    
    def update_queue(self, next_time, next_state, current_time, current_state, number):
        self.cursor.execute('''
            UPDATE queue 
            SET next_time = ?,
                next_state = ?,
                current_time = ?,
                current_state = ?
            WHERE
                number = ?
        ''', (next_time, next_state, current_time, current_state, number))
        self.conn.commit()

    def get_queue(self, queue_id):
        self.cursor.execute('''
            SELECT * FROM queue WHERE id = ?
        ''', (queue_id,))
        return self.cursor.fetchone()

    def get_global_info(self, name):
        self.cursor.execute('''
            SELECT * FROM global WHERE name = ?
        ''', (name,))
        return self.cursor.fetchone()
    
    def set_global_info(self, new_value, name):
        self.cursor.execute('''
            UPDATE global
            SET value = ?
            WHERE name = ?
        ''', (new_value, name,))
        self.conn.commit()

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