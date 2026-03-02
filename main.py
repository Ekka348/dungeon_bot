#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dungeon Crawler - Path of Exile Inspired Telegram RPG Bot
Главный файл запуска бота
"""

import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, DEBUG

# Импорт хендлеров
from handlers.start import StartHandler
from handlers.dungeon import DungeonHandler
from handlers.battle import BattleHandler
from handlers.inventory import InventoryHandler
from handlers.haven import HavenHandler
from handlers.quests import QuestHandler


# ============= НАСТРОЙКА ЛОГИРОВАНИЯ =============

def setup_logging():
    """Настраивает логирование"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Отдельный файл для ошибок
    error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    
    logger = logging.getLogger()
    logger.addHandler(error_handler)
    
    return logger


# ============= КЛАСС-КОНТЕЙНЕР ДЛЯ ХЕНДЛЕРОВ =============

class Handlers:
    """Контейнер для всех хендлеров, чтобы избежать циклических импортов"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        
        # Инициализация хендлеров
        self.start = StartHandler(bot, dp, self)
        self.dungeon = DungeonHandler(bot, dp, self)
        self.battle = BattleHandler(bot, dp, self)
        self.inventory = InventoryHandler(bot, dp, self)
        self.haven = HavenHandler(bot, dp, self)
        self.quest = QuestHandler(bot, dp, self)
        
        logging.info("✅ Все хендлеры зарегистрированы")


# ============= ПРОВЕРКА СТРУКТУРЫ =============

def check_directories():
    """Проверяет наличие необходимых папок"""
    required_dirs = [
        'logs', 'images', 'images/monsters', 
        'images/items', 'images/act1', 'images/act2'
    ]
    
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        logging.debug(f"📁 Папка: {dir_path}")


# ============= ОСНОВНАЯ ФУНКЦИЯ =============

async def main():
    """Главная функция запуска"""
    
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК DUNGEON CRAWLER BOT")
    logger.info("=" * 50)
    
    try:
        # Проверка токена
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
            print("\n❌ ОШИБКА: Токен бота не найден!")
            print("Создайте файл .env с BOT_TOKEN=ваш_токен")
            return
        
        # Проверка папок
        check_directories()
        
        # Инициализация бота
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Установка команд
        commands = [
            BotCommand(command="start", description="🚀 Начать игру"),
            BotCommand(command="help", description="📜 Помощь"),
            BotCommand(command="stats", description="📊 Статистика"),
            BotCommand(command="reset", description="🔄 Сбросить прогресс"),
        ]
        await bot.set_my_commands(commands)
        logger.info("✅ Команды установлены")
        
        # Создаем контейнер с хендлерами
        handlers = Handlers(bot, dp)
        
        # Вывод информации
        print("\n" + "=" * 60)
        print(" 🗡️  DUNGEON CRAWLER - Path of Exile Inspired RPG  🗡️ ".center(60))
        print("=" * 60)
        print(f"\n🤖 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
        print(f"🔧 Режим отладки: {'ВКЛ' if DEBUG else 'ВЫКЛ'}")
        print("\n⚔️ **ГОТОВ К БИТВЕ!** ⚔️")
        print("=" * 60 + "\n")
        
        # Запуск бота
        logger.info("🔄 Запуск polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        
    finally:
        logger.info("🛑 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Необработанная ошибка: {e}")
        sys.exit(1)
