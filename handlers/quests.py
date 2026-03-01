import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.quest import QuestManager, QuestStatus, QuestType
from data.act1 import Act1
from utils.keyboards import get_quests_keyboard, get_quest_details_keyboard
from utils.helpers import format_quest_progress, format_quest_rewards

# ============= ОСНОВНОЙ ХЕНДЛЕР КВЕСТОВ =============

class QuestHandler:
    """Хендлер для управления квестами"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "show_quests")
        async def show_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.show_quests(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("quest_"))
        async def quest_action(callback: types.CallbackQuery, state: FSMContext):
            await self.quest_action(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("accept_quest_"))
        async def accept_quest(callback: types.CallbackQuery, state: FSMContext):
            await self.accept_quest(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("abandon_quest_"))
        async def abandon_quest(callback: types.CallbackQuery, state: FSMContext):
            await self.abandon_quest(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_active_quests")
        async def show_active_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.show_active_quests(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_completed_quests")
        async def show_completed_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.show_completed_quests(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_available_quests")
        async def show_available_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.show_available_quests(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("quest_details_"))
        async def quest_details(callback: types.CallbackQuery, state: FSMContext):
            await self.quest_details(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "update_quests")
        async def update_quests(callback: types.CallbackQuery, state: FSMContext):
            await self.update_quests(callback, state)
    
    async def show_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает список квестов"""
        data = await state.get_data()
        player = data['player']
        
        # Создаем менеджер квестов, если его нет
        if 'quest_manager' not in data:
            quest_manager = QuestManager(player)
            await state.update_data(quest_manager=quest_manager)
        else:
            quest_manager = data['quest_manager']
        
        # Получаем статистику
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
                progress = self._get_quest_progress_string(quest)
                text += f"  • {quest.name} {progress}\n"
            text += "\n"
        
        if available:
            text += "**📜 ДОСТУПНЫЕ:**\n"
            for quest in available[:3]:
                text += f"  • {quest.name}\n"
            text += "\n"
        
        if completed:
            text += "**✅ НЕДАВНО ЗАВЕРШЕННЫЕ:**\n"
            for quest in completed[-3:]:
                text += f"  • {quest.name}\n"
        
        keyboard = get_quests_keyboard(active, available, completed)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _get_quest_progress_string(self, quest):
        """Возвращает строку прогресса квеста"""
        if not quest.objectives:
            return ""
        
        completed = sum(1 for obj in quest.objectives if obj.is_completed())
        total = len(quest.objectives)
        
        if completed == total:
            return "✅"
        else:
            return f"({completed}/{total})"
    
    async def show_active_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает активные квесты"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        active = quest_manager.get_active_quests()
        
        if not active:
            text = "📋 **АКТИВНЫЕ КВЕСТЫ**\n\nУ тебя нет активных квестов."
        else:
            text = "📋 **АКТИВНЫЕ КВЕСТЫ**\n\n"
            for i, quest in enumerate(active, 1):
                progress = self._get_quest_progress_string(quest)
                text += f"{i}. {quest.name} {progress}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_quests")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_completed_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает выполненные квесты"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        completed = quest_manager.get_completed_quests()
        
        if not completed:
            text = "📋 **ЗАВЕРШЕННЫЕ КВЕСТЫ**\n\nУ тебя еще нет завершенных квестов."
        else:
            text = "📋 **ЗАВЕРШЕННЫЕ КВЕСТЫ**\n\n"
            for i, quest in enumerate(completed[-10:], 1):
                text += f"{i}. ✅ {quest.name}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_quests")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_available_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает доступные квесты"""
        data = await state.get_data()
        player = data['player']
        quest_manager = data['quest_manager']
        
        available = quest_manager.get_available_quests()
        
        if not available:
            text = "📋 **ДОСТУПНЫЕ КВЕСТЫ**\n\nСейчас нет доступных квестов."
        else:
            text = "📋 **ДОСТУПНЫЕ КВЕСТЫ**\n\n"
            for i, quest in enumerate(available, 1):
                giver = self._get_quest_giver_name(quest.giver_id)
                text += f"{i}. **{quest.name}**\n"
                text += f"   👤 {giver} | Ур. {quest.min_level}+\n"
                text += f"   {quest.description[:50]}...\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_quests")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _get_quest_giver_name(self, giver_id):
        """Возвращает имя NPC по ID"""
        npcs = {
            "morley": "Старик Морли",
            "ellie": "Безумная Элли",
            "greg": "Торговец Грег"
        }
        return npcs.get(giver_id, "Неизвестно")
    
    async def quest_details(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает детали квеста"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        quest_id = callback.data.split('_')[2]
        quest = quest_manager.get_quest_by_id(quest_id)
        
        if not quest:
            await callback.answer("Квест не найден")
            return
        
        text = quest.get_detailed_info()
        
        # Добавляем информацию о наградах
        reward_str = quest.rewards.get_reward_string()
        if reward_str:
            text += f"\n\n**Награды:** {reward_str}"
        
        keyboard = get_quest_details_keyboard(quest)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def quest_action(self, callback: types.CallbackQuery, state: FSMContext):
        """Обрабатывает действие с квестом"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        action = parts[1]
        quest_id = parts[2] if len(parts) > 2 else None
        
        if action == "accept":
            await self.accept_quest(callback, state, quest_id)
        elif action == "abandon":
            await self.abandon_quest(callback, state, quest_id)
        elif action == "complete":
            await self.complete_quest(callback, state, quest_id)
        else:
            await callback.answer("Неизвестное действие")
    
    async def accept_quest(self, callback: types.CallbackQuery, state: FSMContext, quest_id=None):
        """Принимает квест"""
        if not quest_id:
            quest_id = callback.data.split('_')[2]
        
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        success, message = quest_manager.accept_quest(quest_id)
        
        if success:
            await callback.answer(message)
            # Обновляем отображение
            await self.quest_details(callback, state)
        else:
            await callback.answer(f"❌ {message}")
    
    async def abandon_quest(self, callback: types.CallbackQuery, state: FSMContext, quest_id=None):
        """Отказывается от квеста"""
        if not quest_id:
            quest_id = callback.data.split('_')[2]
        
        # Спрашиваем подтверждение
        text = f"❓ **Отказаться от квеста?**\n\nКвест будет удален из журнала."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, отказаться", callback_data=f"confirm_abandon_{quest_id}")],
            [InlineKeyboardButton(text="❌ Нет, оставить", callback_data=f"quest_details_{quest_id}")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def confirm_abandon(self, callback: types.CallbackQuery, state: FSMContext):
        """Подтверждает отказ от квеста"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        quest_id = callback.data.split('_')[2]
        quest = quest_manager.get_quest_by_id(quest_id)
        
        if not quest:
            await callback.answer("Квест не найден")
            return
        
        # Временно просто меняем статус на доступный
        # В реальности нужно реализовать отказ в QuestManager
        if quest_id in quest_manager.quests:
            quest_manager.quests[quest_id].status = QuestStatus.AVAILABLE
        
        await callback.answer(f"❌ Отказ от квеста: {quest.name}")
        
        # Возвращаемся к списку квестов
        await self.show_quests(callback, state)
    
    async def complete_quest(self, callback: types.CallbackQuery, state: FSMContext, quest_id=None):
        """Завершает квест"""
        if not quest_id:
            quest_id = callback.data.split('_')[2]
        
        data = await state.get_data()
        player = data['player']
        quest_manager = data['quest_manager']
        
        # Завершаем квест
        success, result = quest_manager.complete_quest(quest_id)
        
        if not success:
            await callback.answer(f"❌ {result}")
            return
        
        quest, rewards = result
        
        # Формируем сообщение о завершении
        text = (
            f"✅ **КВЕСТ ВЫПОЛНЕН!**\n\n"
            f"**{quest.name}**\n\n"
            f"**Получено:**\n"
        )
        
        if rewards.exp > 0:
            text += f"✨ {rewards.exp} опыта\n"
        if rewards.gold > 0:
            text += f"💰 {rewards.gold} золота\n"
        if rewards.item:
            text += f"🎁 Особый предмет\n"
        
        text += f"\nОтправляйся к {quest.giver} за новой историей!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 К списку квестов", callback_data="show_quests")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="show_haven")]
        ])
        
        await state.update_data(player=player, quest_manager=quest_manager)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def update_quests(self, callback: types.CallbackQuery, state: FSMContext):
        """Обновляет прогресс квестов"""
        data = await state.get_data()
        quest_manager = data['quest_manager']
        
        # Здесь должна быть логика проверки прогресса
        # Например, проверка убийств монстров
        
        await callback.answer("✅ Квесты обновлены")
        await self.show_quests(callback, state)
    
    # ============= МЕТОДЫ ДЛЯ ИНТЕГРАЦИИ С ДРУГИМИ СИСТЕМАМИ =============
    
    async def check_quest_progress(self, state: FSMContext, objective_type, target, amount=1, location_id=None):
        """Проверяет прогресс квестов (вызывается из других хендлеров)"""
        data = await state.get_data()
        
        if 'quest_manager' not in data:
            return []
        
        quest_manager = data['quest_manager']
        
        # Обновляем прогресс
        completed_quests = quest_manager.update_quest_progress(
            objective_type, target, amount, location_id
        )
        
        if completed_quests:
            # Сохраняем изменения
            await state.update_data(quest_manager=quest_manager)
            
            # Уведомляем игрока
            for quest in completed_quests:
                await self.notify_quest_completed(state, quest)
        
        return completed_quests
    
    async def notify_quest_completed(self, state: FSMContext, quest):
        """Уведомляет игрока о выполнении квеста"""
        # Здесь можно отправить уведомление
        # Например, через callback или отдельное сообщение
        pass


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

async def show_quests(callback: types.CallbackQuery, state: FSMContext):
    """Внешняя функция для показа квестов"""
    handler = QuestHandler(callback.bot, None)
    await handler.show_quests(callback, state)


async def check_quest_progress(state: FSMContext, objective_type, target, amount=1, location_id=None):
    """Внешняя функция для проверки прогресса квестов"""
    data = await state.get_data()
    
    if 'quest_manager' not in data:
        return []
    
    quest_manager = data['quest_manager']
    
    # Обновляем прогресс
    completed_quests = quest_manager.update_quest_progress(
        objective_type, target, amount, location_id
    )
    
    if completed_quests:
        await state.update_data(quest_manager=quest_manager)
    
    return completed_quests


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_quest_system():
    """Тест системы квестов"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМЫ КВЕСТОВ")
    print("=" * 50)
    
    from models.player import Player
    from models.quest import QuestManager
    
    player = Player()
    quest_manager = QuestManager(player)
    
    # Тест доступных квестов
    print("\n🔹 Доступные квесты:")
    available = quest_manager.get_available_quests()
    for quest in available:
        print(f"  - {quest.name} (от {quest.giver})")
        print(f"    {quest.description}")
    
    # Тест принятия квеста
    print("\n🔸 Принимаем квест 'Потерянный амулет':")
    success, message = quest_manager.accept_quest("quest1")
    print(f"  {message}")
    
    # Тест активных квестов
    print("\n🔹 Активные квесты:")
    active = quest_manager.get_active_quests()
    for quest in active:
        print(f"  {quest.get_detailed_info()}")
        print()
    
    # Тест обновления прогресса
    print("\n🔸 Обновляем прогресс (найден амулет):")
    completed = quest_manager.update_quest_progress("find_item", "amulet", location_id=3)
    if completed:
        for quest in completed:
            print(f"  Квест '{quest.name}' выполнен!")
    
    # Тест завершения квеста
    if completed:
        print("\n🔸 Завершаем квест:")
        success, result = quest_manager.complete_quest("quest1")
        if success:
            quest, rewards = result
            print(f"  Квест '{quest.name}' завершен!")
            print(f"  Награды: {rewards.get_reward_string()}")


if __name__ == "__main__":
    test_quest_system()
