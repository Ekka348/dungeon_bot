from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.keyboards import get_quests_keyboard, get_quest_details_keyboard


class QuestHandler:
    """Хендлер для управления квестами"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "show_quests")
        async def show_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.show_quests(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("quest_details_"))
        async def quest_details(callback: types.CallbackQuery, state: FSMContext):
            await self.quest_details(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("accept_quest_"))
        async def accept_quest(callback: types.CallbackQuery, state: FSMContext):
            await self.accept_quest(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("complete_quest_"))
        async def complete_quest(callback: types.CallbackQuery, state: FSMContext):
            await self.complete_quest(callback, state)
    
    async def show_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает список квестов"""
        data = await state.get_data()
        quest_manager = data.get('quest_manager')
        
        if not quest_manager:
            await callback.answer("Система квестов не инициализирована")
            return
        
        active = quest_manager.get_active_quests()
        available = quest_manager.get_available_quests()
        completed = quest_manager.get_completed_quests()
        
        text = (
            f"📋 **ЖУРНАЛ КВЕСТОВ**\n\n"
            f"⚔️ Активные: {len(active)}\n"
            f"📜 Доступные: {len(available)}\n"
            f"✅ Завершенные: {len(completed)}\n\n"
        )
        
        if active:
            text += "**⚔️ АКТИВНЫЕ:**\n"
            for quest in active[:3]:
                text += f"  • {quest.get_progress_string()}\n"
            text += "\n"
        
        if available:
            text += "**📜 ДОСТУПНЫЕ:**\n"
            for quest in available[:3]:
                text += f"  • {quest.name}\n"
        
        keyboard = get_quests_keyboard(active, available, completed)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def quest_details(self, callback: types.CallbackQuery, state: FSMContext):
        """Детали квеста"""
        data = await state.get_data()
        quest_manager = data.get('quest_manager')
        
        quest_id = callback.data.split('_')[2]
        quest = quest_manager.get_quest_by_id(quest_id)
        
        if not quest:
            await callback.answer("Квест не найден")
            return
        
        text = quest.get_detailed_info()
        keyboard = get_quest_details_keyboard(quest)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def accept_quest(self, callback: types.CallbackQuery, state: FSMContext):
        """Принять квест"""
        data = await state.get_data()
        quest_manager = data.get('quest_manager')
        
        quest_id = callback.data.split('_')[2]
        success, message = quest_manager.accept_quest(quest_id)
        
        await callback.answer(message)
        
        if success:
            await self.quest_details(callback, state)
    
    async def complete_quest(self, callback: types.CallbackQuery, state: FSMContext):
        """Завершить квест"""
        data = await state.get_data()
        quest_manager = data.get('quest_manager')
        
        quest_id = callback.data.split('_')[2]
        success, result = quest_manager.complete_quest(quest_id)
        
        if not success:
            await callback.answer(result)
            return
        
        quest, rewards = result
        
        text = (
            f"✅ **КВЕСТ ВЫПОЛНЕН!**\n\n"
            f"**{quest.name}**\n\n"
            f"**Получено:**\n"
        )
        
        if rewards.exp > 0:
            text += f"✨ {rewards.exp} опыта\n"
        if rewards.gold > 0:
            text += f"💰 {rewards.gold} золота\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 К списку квестов", callback_data="show_quests")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="show_haven")]
        ])
        
        await state.update_data(player=quest_manager.player, quest_manager=quest_manager)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def check_quest_progress(self, state: FSMContext, objective_type, target, amount=1, location_id=None):
        """Проверяет прогресс квестов (для вызова из других хендлеров)"""
        data = await state.get_data()
        quest_manager = data.get('quest_manager')
        
        if not quest_manager:
            return []
        
        completed = quest_manager.update_progress(objective_type, target, amount, location_id)
        
        if completed:
            await state.update_data(quest_manager=quest_manager)
        
        return completed
