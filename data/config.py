from os import getenv
from dotenv import load_dotenv

load_dotenv()

db_user = getenv('DB_USER')
password = getenv('DB_PASSWORD')
host = getenv('DB_HOST')
db_name = getenv('DB_NAME')
