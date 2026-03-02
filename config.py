import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота - теперь ТОЛЬКО из переменных окружения!
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения! Создайте файл .env с BOT_TOKEN=ваш_токен")

# Настройки
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
IMAGES_PATH = "images"
MONSTERS_PATH = f"{IMAGES_PATH}/monsters"
ITEMS_PATH = f"{IMAGES_PATH}/items"

# Константы для игровой логики
MAX_FLASKS = 3
BASE_FLASK_CHARGES = 3
DODGE_BASE_CHANCE = 5
CRIT_BASE_MULTIPLIER = 150
