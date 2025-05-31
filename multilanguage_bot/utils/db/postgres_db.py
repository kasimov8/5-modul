import psycopg2
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class PSQL:
    def __init__(self):
        self.conn = psycopg2.connect(
                dbname=getenv("DB_NAME"),
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD"),
                host=getenv("DB_HOST"),
                port=getenv("DB_PORT")
        )

        self.curr = self.conn.cursor()

    def save(self, chat_id, lang):
        with self.conn:
            self.curr.execute("INSERT INTO users(chat_id, lang) VALUES (%s, %s)", (chat_id, lang))

    def  fetch_one(self, query):
        self.curr.execute(query)
        data = self.curr.fetchone()
        return data

    def get_chatid(self):
        self.curr.execute("""SELECT chat_id FROM users;""")
        datas = self.curr.fetchall()
        data = [row[0] for row in datas]
        return data

    def update(self, call_data, chat_id):
        with self.conn:
            self.curr.execute(
                "UPDATE users SET lang = %s WHERE chat_id = %s",
                (call_data, chat_id)
            )

    def get_lang(self, chat_id):
        query = f"""SELECT lang FROM users WHERE chat_id={chat_id};"""
        return self.fetch_one(query)[0] if self.fetch_one(query) else 'uz'



pg = PSQL()


