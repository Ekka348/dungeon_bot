from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.quest import QuestManager
from systems.area_level import AreaRegistry
from systems.progression import ProgressionSystem
from utils.keyboards import get_start_keyboard, get_help_keyboard
from utils.helpers import format_welcome_message, format_help_message


class StartHandler:
    """Хендлер для команд старта"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
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
        
        @self.dp.callback_query(lambda c: c.data == "start_game")
        async def start_game(callback: types.CallbackQuery, state: FSMContext):
            await self.start_game(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_help")
        async def show_help(callback: types.CallbackQuery, state: FSMContext):
            await self.show_help(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_about")
        async def show_about(callback: types.CallbackQuery, state: FSMContext):
            await self.show_about(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "confirm_reset")
        async def confirm_reset(callback: types.CallbackQuery, state: FSMContext):
            await self.confirm_reset(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "cancel_reset")
        async def cancel_reset(callback: types.CallbackQuery, state: FSMContext):
            await self.cancel_reset(callback, state)
    
    async def cmd_start(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду /start"""
        user_name = message.from_user.first_name or "Странник"
        welcome_text = format_welcome_message(user_name)
        keyboard = get_start_keyboard()
        
        await message.answer(welcome_text, reply_markup=keyboard)
        await state.clear()
    
    async def start_game(self, callback: types.CallbackQuery, state: FSMContext):
        """Начинает новую игру"""
        player = Player()
        quest_manager = QuestManager(player)
        
        await state.update_data(
            player=player,
            quest_manager=quest_manager
        )
        
        await self.handlers.dungeon.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def cmd_help(self, message: types.Message, state: FSMContext):
        """Команда /help"""
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
        """Команда /stats"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ У тебя нет активного персонажа. Напиши /start чтобы начать игру.")
            return
        
        progression = ProgressionSystem(player)
        stats_text = progression.get_progression_string()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
    
    async def cmd_reset(self, message: types.Message, state: FSMContext):
        """Команда /reset"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ У тебя нет активного персонажа.")
            return
        
        text = (
            "⚠️ **СБРОС ПРОГРЕССА**\n\n"
            "Ты действительно хочешь сбросить весь прогресс?\n"
            "Это действие нельзя отменить!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="confirm_reset")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_reset")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    async def confirm_reset(self, callback: types.CallbackQuery, state: FSMContext):
        """Подтверждает сброс"""
        await state.clear()
        await callback.message.edit_text(
            "✅ **ПРОГРЕСС СБРОШЕН**\n\n"
            "Напиши /start чтобы начать новое приключение!"
        )
        await callback.answer()
    
    async def cancel_reset(self, callback: types.CallbackQuery, state: FSMContext):
        """Отменяет сброс"""
        await self.handlers.dungeon.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def show_about(self, callback: types.CallbackQuery, state: FSMContext):
        """Информация об игре"""
        text = (
            "🎮 **ОБ ИГРЕ**\n\n"
            "**Dungeon Crawler** - текстовая RPG в стиле Path of Exile.\n\n"
            "**Версия:** 1.0.0 Beta\n\n"
            "**Особенности:**\n"
            "• 7 уникальных локаций в первом акте\n"
            "• Более 50 видов монстров\n"
            "• Система лута с аффиксами\n"
            "• Квесты с прогрессией\n"
            "• Уровни локаций и сложность\n\n"
            "Напиши /help чтобы узнать команды."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📜 Помощь", callback_data="show_help")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="start_game")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
