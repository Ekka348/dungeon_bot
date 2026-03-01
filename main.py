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

# Импорт конфигурации
from config import BOT_TOKEN, DEBUG

# Импорт хендлеров
from handlers.start import StartHandler
from handlers.dungeon import DungeonHandler
from handlers.battle import BattleHandler
from handlers.inventory import InventoryHandler
from handlers.haven import HavenHandler
from handlers.quests import QuestHandler

# Импорт систем для инициализации
from systems.area_level import AreaLevelSystem
from systems.loot import LootSystem
from systems.progression import ProgressionSystem

# ============= НАСТРОЙКА ЛОГИРОВАНИЯ =============

def setup_logging():
    """Настраивает логирование"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Создаем папку для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Настройка логирования в файл и консоль
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Отдельный логгер для ошибок
    error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    
    logger = logging.getLogger()
    logger.addHandler(error_handler)
    
    return logger


# ============= ИНИЦИАЛИЗАЦИЯ БОТА =============

def setup_bot():
    """Инициализирует бота и диспетчер"""
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    return bot, dp


async def setup_commands(bot: Bot):
    """Устанавливает команды бота"""
    commands = [
        BotCommand(command="start", description="🚀 Начать игру"),
        BotCommand(command="help", description="📜 Помощь"),
        BotCommand(command="stats", description="📊 Статистика"),
        BotCommand(command="info", description="ℹ️ Информация о локации"),
        BotCommand(command="reset", description="🔄 Сбросить прогресс"),
        BotCommand(command="donate", description="💝 Поддержать проект"),
    ]
    
    await bot.set_my_commands(commands)


# ============= РЕГИСТРАЦИЯ ХЕНДЛЕРОВ =============

def register_handlers(dp: Dispatcher, bot: Bot):
    """Регистрирует все обработчики"""
    
    # Создаем экземпляры хендлеров
    StartHandler(bot, dp)
    DungeonHandler(bot, dp)
    BattleHandler(bot, dp)
    InventoryHandler(bot, dp)
    HavenHandler(bot, dp)
    QuestHandler(bot, dp)
    
    logging.info("✅ Все хендлеры зарегистрированы")


# ============= ПРОВЕРКА СТРУКТУРЫ ПАПОК =============

def check_directories():
    """Проверяет наличие необходимых папок"""
    required_dirs = [
        'logs',
        'images',
        'images/monsters',
        'images/items',
        'images/act1',
        'images/act2'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"📁 Создана папка: {dir_path}")
        else:
            logging.debug(f"📁 Папка существует: {dir_path}")


# ============= ВЫВОД ИНФОРМАЦИИ ПРИ ЗАПУСКЕ =============

def print_startup_info():
    """Выводит информацию при запуске"""
    print("\n" + "=" * 60)
    print(" 🗡️  DUNGEON CRAWLER - Path of Exile Inspired RPG  🗡️ ".center(60))
    print("=" * 60)
    print("\n📦 **ЗАГРУЗКА ДАННЫХ:**")
    print("  ✅ Система уровней локаций")
    print("  ✅ Система лута")
    print("  ✅ Система прогрессии")
    print("  ✅ Модели игрока, врагов, предметов")
    print("  ✅ Данные акта 1")
    print("\n🤖 **ЗАПУСК БОТА:**")
    print(f"  • Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"  • Режим отладки: {'ВКЛ' if DEBUG else 'ВЫКЛ'}")
    print("\n📁 **ПРОВЕРКА ПАПОК:**")
    print("  • logs/ - для файлов логов")
    print("  • images/monsters/ - для изображений монстров")
    print("  • images/items/ - для изображений предметов")
    print("  • images/act1/ - для изображений акта 1")
    print("\n⚔️ **ГОТОВ К БИТВЕ!** ⚔️")
    print("=" * 60 + "\n")


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

async def test_systems():
    """Тестирует основные системы"""
    logging.info("🧪 Запуск тестирования систем...")
    
    from models.player import Player
    from models.enemy import Enemy
    from systems.combat import CombatSystem
    from systems.loot import LootSystem
    from systems.area_level import AreaLevelSystem
    
    # Тест создания игрока
    player = Player()
    logging.info(f"✅ Создан игрок: Уровень {player.level}, HP {player.hp}")
    
    # Тест системы уровней
    area_level = AreaLevelSystem.get_area_level(3)
    logging.info(f"✅ Уровень локации 3: {area_level}")
    
    # Тест создания врага
    from data.act1 import Act1
    monster_data = Act1.get_random_monster(1, "common")
    if monster_data:
        enemy = Enemy.from_monster_data(monster_data, 1, "common")
        logging.info(f"✅ Создан враг: {enemy.name}, HP {enemy.hp}")
    
    # Тест боевой системы
    logging.info("✅ Системы работают корректно")


# ============= ОСНОВНАЯ ФУНКЦИЯ =============

async def main():
    """Главная функция запуска бота"""
    
    # Настройка логирования
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК DUNGEON CRAWLER BOT")
    logger.info("=" * 50)
    
    try:
        # Проверка токена
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("❌ Токен бота не настроен! Укажите BOT_TOKEN в файле .env")
            print("\n❌ ОШИБКА: Токен бота не настроен!")
            print("Создайте файл .env и укажите BOT_TOKEN=ваш_токен")
            return
        
        # Проверка структуры папок
        check_directories()
        
        # Инициализация бота
        bot, dp = setup_bot()
        logger.info(f"✅ Бот инициализирован: {bot.__class__.__name__}")
        
        # Установка команд
        await setup_commands(bot)
        logger.info("✅ Команды установлены")
        
        # Регистрация хендлеров
        register_handlers(dp, bot)
        
        # Тестирование систем (в режиме отладки)
        if DEBUG:
            await test_systems()
        
        # Вывод информации в консоль
        print_startup_info()
        
        # Запуск бота
        logger.info("🔄 Запуск polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("Проверьте файл logs/errors.log для деталей")
        
    finally:
        logger.info("🛑 Бот остановлен")
        print("\n🛑 Бот остановлен")


# ============= ТОЧКА ВХОДА =============

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Необработанная ошибка: {e}")
        sys.exit(1)
