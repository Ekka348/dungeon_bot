import asyncio
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from data.act1 import Act1
from systems.progression import ProgressionSystem
from utils.keyboards import get_start_keyboard, get_help_keyboard
from utils.helpers import format_welcome_message, format_help_message

# ============= ОСНОВНОЙ ХЕНДЛЕР СТАРТА =============

class StartHandler:
    """Хендлер для команд старта и помощи"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.message(Command('start'))
        async def cmd_start(message: types.Message, state: FSMContext):
            await self.cmd_start(message, state)
        
        @self.dp.message(Command('help'))
        async def cmd_help(message: types.Message, state: FSMContext):
            await self.cmd_help(message, state)
        
        @self.dp.message(Command('stats'))
        async def cmd_stats(message: types.Message, state: FSMContext):
            await self.cmd_stats(message, state)
        
        @self.dp.message(Command('reset'))
        async def cmd_reset(message: types.Message, state: FSMContext):
            await self.cmd_reset(message, state)
        
        @self.dp.message(Command('info'))
        async def cmd_info(message: types.Message, state: FSMContext):
            await self.cmd_info(message, state)
        
        @self.dp.message(Command('donate'))
        async def cmd_donate(message: types.Message, state: FSMContext):
            await self.cmd_donate(message, state)
        
        @self.dp.callback_query(lambda c: c.data == "start_game")
        async def start_game(callback: types.CallbackQuery, state: FSMContext):
            await self.start_game(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_help")
        async def show_help(callback: types.CallbackQuery, state: FSMContext):
            await self.show_help(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_about")
        async def show_about(callback: types.CallbackQuery, state: FSMContext):
            await self.show_about(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_credits")
        async def show_credits(callback: types.CallbackQuery, state: FSMContext):
            await self.show_credits(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "confirm_reset")
        async def confirm_reset(callback: types.CallbackQuery, state: FSMContext):
            await self.confirm_reset(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "cancel_reset")
        async def cancel_reset(callback: types.CallbackQuery, state: FSMContext):
            await self.cancel_reset(callback, state)
    
    async def cmd_start(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /start"""
        # Получаем имя пользователя
        user_name = message.from_user.first_name or "Странник"
        
        # Формируем приветственное сообщение
        welcome_text = format_welcome_message(user_name)
        
        # Клавиатура
        keyboard = get_start_keyboard()
        
        # Отправляем приветствие
        await message.answer(welcome_text, reply_markup=keyboard)
        
        # Очищаем состояние (на случай, если был старый игрок)
        await state.clear()
    
    async def start_game(self, callback: types.CallbackQuery, state: FSMContext):
        """Начинает новую игру"""
        # Создаем нового игрока
        player = Player()
        
        # Получаем первую локацию
        first_location = Act1.get_first_location()
        
        # Генерируем события для первой локации
        from handlers.dungeon import show_dungeon
        
        # Сохраняем игрока в состояние
        await state.update_data(player=player)
        
        # Показываем подземелье
        await show_dungeon(callback.message, state)
        await callback.answer()
    
    async def cmd_help(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /help"""
        help_text = format_help_message()
        
        keyboard = get_help_keyboard()
        
        await message.answer(help_text, reply_markup=keyboard)
    
    async def show_help(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает справку"""
        help_text = format_help_message()
        
        keyboard = get_help_keyboard()
        
        await callback.message.edit_text(help_text, reply_markup=keyboard)
        await callback.answer()
    
    async def cmd_stats(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /stats"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ У тебя нет активного персонажа. Напиши /start чтобы начать игру.")
            return
        
        # Получаем прогрессию
        progression = ProgressionSystem(player)
        
        stats_text = progression.get_progression_string()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Подробнее", callback_data="show_detailed_progression")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
    
    async def cmd_reset(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /reset (сброс прогресса)"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ У тебя нет активного персонажа. Напиши /start чтобы начать игру.")
            return
        
        text = (
            "⚠️ **СБРОС ПРОГРЕССА**\n\n"
            "Ты действительно хочешь сбросить весь прогресс?\n"
            "Это действие нельзя отменить!\n\n"
            "Весь опыт, золото, предметы и квесты будут потеряны."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="confirm_reset")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_reset")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    async def confirm_reset(self, callback: types.CallbackQuery, state: FSMContext):
        """Подтверждает сброс прогресса"""
        # Очищаем состояние
        await state.clear()
        
        text = (
            "✅ **ПРОГРЕСС СБРОШЕН**\n\n"
            "Твой персонаж удален.\n"
            "Напиши /start чтобы начать новое приключение!"
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
    
    async def cancel_reset(self, callback: types.CallbackQuery, state: FSMContext):
        """Отменяет сброс прогресса"""
        from handlers.dungeon import show_dungeon
        
        await show_dungeon(callback.message, state)
        await callback.answer()
    
    async def cmd_info(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /info (информация об акте)"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ У тебя нет активного персонажа. Напиши /start чтобы начать игру.")
            return
        
        # Получаем информацию о текущей локации
        from systems.area_level import Area
        
        current_location = Act1.get_location_by_id(player.current_location)
        area = Area(player.current_location)
        
        # Получаем следующую локацию
        next_location = None
        if current_location["next_location"]:
            next_location = Act1.get_location_by_id(current_location["next_location"])
        
        text = (
            f"📌 **ИНФОРМАЦИЯ**\n\n"
            f"**Акт {player.act}: {Act1.LOCATIONS[1]['name_en']}**\n\n"
            f"**Текущая локация:**\n"
            f"{current_location['name']}\n"
            f"Уровень: {area.current_level} ({area.min_level}-{area.max_level})\n"
            f"{current_location['description']}\n\n"
        )
        
        if next_location:
            text += f"**Следующая локация:**\n{next_location['name']}\n\n"
        
        if current_location.get("has_boss"):
            text += f"⚠️ **В этой локации есть босс!**\n\n"
        
        text += f"**Прогресс:**\n"
        text += f"👤 Уровень: {player.level}\n"
        text += f"⚔️ Сила: {player.strength} | 🏹 Ловкость: {player.dexterity} | 📚 Интеллект: {player.intelligence}\n"
        text += f"💰 Золото: {player.gold} | ✨ Опыт: {player.exp}/{player.level * 100}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    async def cmd_donate(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /donate (поддержка автора)"""
        text = (
            "💝 **ПОДДЕРЖКА ПРОЕКТА**\n\n"
            "Если тебе нравится игра и ты хочешь поддержать разработку,\n"
            "ты можешь отправить донат:\n\n"
            "💰 **Bitcoin:**\n"
            "`bc1q...`\n\n"
            "💰 **Ethereum:**\n"
            "`0x...`\n\n"
            "💰 **TON:**\n"
            "`EQ...`\n\n"
            "Или просто поставь звездочку на GitHub! ⭐\n\n"
            "Спасибо за поддержку! 🙏"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_about")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    async def show_about(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает информацию об игре"""
        text = (
            "🎮 **ОБ ИГРЕ**\n\n"
            "**Dungeon Crawler** - это текстовая RPG в стиле Path of Exile,\n"
            "где ты исследуешь подземелья, сражаешься с монстрами,\n"
            "собираешь лут и выполняешь квесты.\n\n"
            "**Версия:** 1.0.0 Beta\n"
            "**Автор:** @username\n"
            "**GitHub:** github.com/...\n\n"
            "**Особенности:**\n"
            "• 7 уникальных локаций в первом акте\n"
            "• Более 50 видов монстров\n"
            "• Система лута как в Path of Exile\n"
            "• Квесты с прогрессией\n"
            "• Уровни локаций и сложность\n\n"
            "Напиши /help чтобы узнать команды."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📜 Помощь", callback_data="show_help")],
            [InlineKeyboardButton(text="👥 Авторы", callback_data="show_credits")],
            [InlineKeyboardButton(text="💝 Поддержать", callback_data="cmd_donate")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="start_game")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_credits(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает информацию об авторах"""
        text = (
            "👥 **АВТОРЫ**\n\n"
            "**Идея и разработка:**\n"
            "@username\n\n"
            "**Художники:**\n"
            "• Иван Иванов - спрайты монстров\n"
            "• Петр Петров - фоны локаций\n\n"
            "**Тестировщики:**\n"
            "• Сообщество Telegram\n\n"
            "**Библиотеки:**\n"
            "• aiogram 3.3.0\n"
            "• Python 3.10+\n\n"
            "Спасибо всем, кто помогал в разработке! 🙏"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_about")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def format_welcome_message(user_name):
    """Форматирует приветственное сообщение"""
    return (
        f"⚔️ **Добро пожаловать в Dungeon Crawler, {user_name}!** ⚔️\n\n"
        f"Ты был сброшен в темницу за преступления, которых не совершал.\n"
        f"Холодный камень встречает твое падение. Вокруг лишь тьма\n"
        f"и звуки капающей воды. Нужно найти выход...\n\n"
        f"🕷️ **Что тебя ждет:**\n"
        f"• Исследуй 7 уникальных локаций\n"
        f"• Сражайся с монстрами подземелья\n"
        f"• Собирай лут с аффиксами\n"
        f"• Выполняй квесты и прокачивайся\n"
        f"• Сразись с боссом акта\n\n"
        f"Напиши /help для списка команд или нажми кнопку ниже!"
    )


def format_help_message():
    """Форматирует сообщение помощи"""
    return (
        "📜 **ПОМОЩЬ ПО ИГРЕ**\n\n"
        "**Основные команды:**\n"
        "/start - начать игру\n"
        "/help - показать эту справку\n"
        "/stats - показать статистику\n"
        "/info - информация о текущей локации\n"
        "/reset - сбросить прогресс\n\n"
        
        "**Боевая система:**\n"
        "🔪 Атака (1 эн.) - обычная атака\n"
        "💪 Тяжелая (2 эн.) - больше урона\n"
        "⚡ Быстрая (1 эн.) - выше точность\n"
        "🛡️ Защита (1 эн.) - снижение урона\n"
        "💨 Уклон (1 эн.) - шанс избежать\n"
        "🧪 Фласка - лечение\n"
        "🏃 Побег - попытка сбежать\n\n"
        
        "**Система лута:**\n"
        "⚪ Обычные предметы - без аффиксов\n"
        "🔵 Магические - 1 аффикс\n"
        "🟡 Редкие - 2-4 аффикса\n"
        "🔴 Уникальные - особые свойства\n\n"
        
        "**Советы:**\n"
        "• Возвращайся в убежище, чтобы восстановить фласки\n"
        "• Выполняй квесты для получения наград\n"
        "• Следи за уровнем локации - монстры могут быть сильнее\n"
        "• Собирай лут и экипируй лучшее\n\n"
        
        "Удачи в приключении, странник! 🍀"
    )


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_formatting():
    """Тест форматирования сообщений"""
    print("=" * 50)
    print("ТЕСТ ФОРМАТИРОВАНИЯ СООБЩЕНИЙ")
    print("=" * 50)
    
    print("\n🔹 Приветственное сообщение:")
    print(format_welcome_message("Тестер"))
    
    print("\n🔹 Сообщение помощи:")
    print(format_help_message())
    
    print("\n🔹 Информация об игре:")
    print(
        "🎮 **ОБ ИГРЕ**\n\n"
        "**Dungeon Crawler** - это текстовая RPG в стиле Path of Exile,\n"
        "где ты исследуешь подземелья, сражаешься с монстрами,\n"
        "собираешь лут и выполняешь квесты.\n\n"
        "**Версия:** 1.0.0 Beta"
    )


if __name__ == "__main__":
    test_formatting()
