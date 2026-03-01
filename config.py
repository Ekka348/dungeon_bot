import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8404262144:AAFhLqVbU4FpIrM6KWfU6u9L1l5Qh-FYLWk')

# Настройки
DEBUG = True
IMAGES_PATH = "images"
MONSTERS_PATH = f"{IMAGES_PATH}/monsters"
ITEMS_PATH = f"{IMAGES_PATH}/items"
