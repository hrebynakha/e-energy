import os
from dotenv import load_dotenv


DEBUG = True if os.getenv('DEBUG') == 'True' else False
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
PROVIDER = os.getenv('PROVIDER')
PROVIDER_URL = os.getenv('PROVIDER_URL')
# NOTIFICATIONS
TIMEOUT = os.getenv('TIMEOUT')
TURN_ON_NOTIFY= bool(os.getenv('TURN_ON_NOTIFY'))
BOT_TOKEN = os.getenv('BOT_TOKEN')
