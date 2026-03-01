import asyncio
import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask
from data.act1 import Act1
from systems.area_level import AreaLevelSystem, Area, DifficultyCalculator
from systems.loot import LootSystem
from systems.progression import ProgressionSystem
from utils.keyboards import get_dungeon_keyboard, get_battle_keyboard, get_haven_keyboard
from utils.helpers import format_dungeon_view, format_progress_bar

# ============= ОСНОВНОЙ ХЕНДЛЕР ПОДЗЕМЕЛЬЯ =============

class DungeonHandler:
    """Хендлер для управления подземельем"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self.loot_system = LootSystem()
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "enter_dungeon")
        async def enter_dungeon(callback: types.CallbackQuery, state: FSMContext):
            await self.enter_dungeon(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "next_step")
        async def next_step(callback: types.CallbackQuery, state: FSMContext):
            await self.next_step(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "return_to_haven")
        async def return_to_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.return_to_haven(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_map")
        async def show_map(callback: types.CallbackQuery, state: FSMContext):
            await self.show_map(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_progression")
        async def show_progression(callback: types.CallbackQuery, state: FSMContext):
            await self.show_progression(callback, state)
    
    async def enter_dungeon(self, callback: types.CallbackQuery, state: FSMContext):
        """Вход в подземелье из убежища"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Получаем текущую локацию
        location = Act1.get_location_by_id(player.current_location)
        
        # Генерируем события для локации, если их нет
        if 'dungeon_events' not in data or not data['dungeon_events']:
            events = Act1.generate_location_events(player.current_location)
            await state.update_data(dungeon_events=events)
        else:
            events = data['dungeon_events']
        
        # Сбрасываем позицию
        player.position_in_location = 0
        await state.update_data(player=player)
        
        await self.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def show_dungeon(self, message: types.Message, state: FSMContext):
        """Показывает текущее состояние подземелья"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        
        if not events:
            # Генерируем новые события
            events = Act1.generate_location_events(player.current_location)
            await state.update_data(dungeon_events=events)
        
        # Текущее событие
        current_index = player.position_in_location
        if current_index >= len(events):
            # Дошел до конца локации
            await self.show_location_complete(message, state)
            return
        
        current_event = events[current_index]
        
        # Получаем информацию о локации
        location = Act1.get_location_by_id(player.current_location)
        area = Area(player.current_location)
        
        # Прогресс-бар
        progress_bar = format_progress_bar(current_index, len(events), 
                                          [e.get("type") for e in events])
        
        # Информация о событии
        if current_event["type"] == "battle":
            event_info = self._format_battle_event(current_event)
        elif current_event["type"] == "chest":
            event_info = self._format_chest_event(current_event)
        elif current_event["type"] == "trap":
            event_info = self._format_trap_event(current_event)
        elif current_event["type"] == "rest":
            event_info = self._format_rest_event(current_event)
        elif current_event["type"] == "transition":
            event_info = self._format_transition_event(current_event)
        else:
            event_info = "❓ Неизвестное событие"
        
        # Формируем текст
        text = (
            f"🗺️ **{location['name']}**\n"
            f"📊 Уровень локации: {area.current_level}\n\n"
            f"{progress_bar}\n\n"
            f"📍 **Событие {current_index + 1}/{len(events)}**\n\n"
            f"{event_info}\n\n"
            f"👤 {player.hp}/{player.max_hp} ❤️ | Ур. {player.level}"
        )
        
        # Клавиатура
        keyboard = get_dungeon_keyboard(current_event, player)
        
        try:
            await message.edit_text(text, reply_markup=keyboard)
        except:
            await message.answer(text, reply_markup=keyboard)
    
    def _format_battle_event(self, event):
        """Форматирует информацию о битве"""
        monster = event["monster"]
        return (
            f"⚔️ **БИТВА**\n\n"
            f"{monster['emoji']} **{monster['name']}**\n"
            f"❤️ HP: {monster['base_hp']}\n"
            f"_{monster['description']}_"
        )
    
    def _format_chest_event(self, event):
        """Форматирует информацию о сундуке"""
        rarity_colors = {
            "common": "🟢 Обычный",
            "magic": "🟣 Магический",
            "rare": "🟡 Редкий"
        }
        rarity_name = rarity_colors.get(event["rarity"], "Обычный")
        
        return (
            f"📦 **СУНДУК**\n\n"
            f"{rarity_name} сундук\n"
            f"Нажми 'Открыть', чтобы узнать, что внутри!"
        )
    
    def _format_trap_event(self, event):
        """Форматирует информацию о ловушке"""
        return (
            f"⚠️ **ЛОВУШКА**\n\n"
            f"Ты чувствуешь опасность...\n"
            f"💥 Урон: {event.get('damage', 20)}"
        )
    
    def _format_rest_event(self, event):
        """Форматирует информацию о месте отдыха"""
        return (
            f"🔥 **МЕСТО ОТДЫХА**\n\n"
            f"Ты находишь безопасное место для отдыха.\n"
            f"❤️ Восстановление: {event.get('heal', 30)} HP"
        )
    
    def _format_transition_event(self, event):
        """Форматирует информацию о переходе"""
        next_loc_id = event.get("to_location")
        next_loc = Act1.get_location_by_id(next_loc_id)
        
        return (
            f"🚪 **ПЕРЕХОД**\n\n"
            f"{event.get('message', 'Ты нашел проход дальше...')}\n\n"
            f"➡️ Следующая локация: **{next_loc['name']}**"
        )
    
    async def next_step(self, callback: types.CallbackQuery, state: FSMContext):
        """Переход к следующему событию"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        
        player.position_in_location += 1
        await state.update_data(player=player)
        
        # Проверяем, не закончилась ли локация
        if player.position_in_location >= len(events):
            # Локация пройдена
            await self.show_location_complete(callback.message, state)
        else:
            await self.show_dungeon(callback.message, state)
        
        await callback.answer()
    
    async def show_location_complete(self, message: types.Message, state: FSMContext):
        """Показывает экран завершения локации"""
        data = await state.get_data()
        player = data['player']
        
        location = Act1.get_location_by_id(player.current_location)
        next_loc = Act1.get_location_by_id(location["next_location"]) if location["next_location"] else None
        
        text = (
            f"✅ **ЛОКАЦИЯ ПРОЙДЕНА!**\n\n"
            f"Ты успешно исследовал {location['name']}.\n\n"
        )
        
        buttons = []
        
        if next_loc:
            text += f"➡️ Впереди: **{next_loc['name']}**"
            buttons.append([InlineKeyboardButton(text="➡️ Идти дальше", callback_data="go_to_next_location")])
        else:
            text += "🏁 Это была последняя локация акта!"
            buttons.append([InlineKeyboardButton(text="🏁 Завершить акт", callback_data="complete_act")])
        
        buttons.append([InlineKeyboardButton(text="🔄 Остаться здесь", callback_data="show_dungeon")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.edit_text(text, reply_markup=keyboard)
    
    async def return_to_haven(self, callback: types.CallbackQuery, state: FSMContext):
        """Возврат в убежище"""
        data = await state.get_data()
        player = data['player']
        
        haven = Act1.get_location_by_id(2)  # Убежище всегда ID 2
        player.current_location = haven["id"]
        player.position_in_location = 0
        
        await state.update_data(player=player, dungeon_events=[])
        
        # Импортируем здесь, чтобы избежать циклического импорта
        from handlers.haven import show_haven
        
        await show_haven(callback.message, state)
        await callback.answer()
    
    async def show_map(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает карту акта"""
        data = await state.get_data()
        player = data['player']
        
        locations = Act1.get_locations_in_order()
        
        text = "🗺️ **КАРТА АКТА 1**\n\n"
        
        for loc in locations:
            if loc["id"] == player.current_location:
                text += f"👉 **{loc['name']}** (текущая)\n"
            elif loc["id"] < player.current_location:
                text += f"✅ {loc['name']}\n"
            else:
                text += f"⬜ {loc['name']}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_progression(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает прогрессию игрока"""
        data = await state.get_data()
        player = data['player']
        
        progression = ProgressionSystem(player)
        
        text = progression.get_progression_string()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Подробнее", callback_data="show_detailed_progression")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_detailed_progression(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает детальную прогрессию"""
        data = await state.get_data()
        player = data['player']
        
        progression = ProgressionSystem(player)
        
        text = progression.get_detailed_progression()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="show_progression")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


# ============= ФУНКЦИИ ДЛЯ ЭКСПОРТА =============

async def show_dungeon(message: types.Message, state: FSMContext):
    """Внешняя функция для показа подземелья"""
    data = await state.get_data()
    player = data.get('player')
    
    if not player:
        # Создаем нового игрока
        player = Player()
        await state.update_data(player=player)
    
    events = data.get('dungeon_events', [])
    
    if not events:
        # Генерируем события для текущей локации
        events = Act1.generate_location_events(player.current_location)
        await state.update_data(dungeon_events=events)
    
    # Текущее событие
    current_index = player.position_in_location
    
    if current_index >= len(events):
        # Локация пройдена
        await show_location_complete(message, state)
        return
    
    current_event = events[current_index]
    
    # Получаем информацию о локации
    location = Act1.get_location_by_id(player.current_location)
    area = Area(player.current_location)
    
    # Прогресс-бар
    progress_bar = format_progress_bar(current_index, len(events), 
                                      [e.get("type") for e in events])
    
    # Информация о событии
    if current_event["type"] == "battle":
        monster = current_event["monster"]
        event_info = (
            f"⚔️ **БИТВА**\n\n"
            f"{monster['emoji']} **{monster['name']}**\n"
            f"❤️ HP: {monster['base_hp']}\n"
            f"_{monster['description']}_"
        )
    elif current_event["type"] == "chest":
        rarity_colors = {
            "common": "🟢 Обычный",
            "magic": "🟣 Магический",
            "rare": "🟡 Редкий"
        }
        rarity_name = rarity_colors.get(current_event["rarity"], "Обычный")
        event_info = (
            f"📦 **СУНДУК**\n\n"
            f"{rarity_name} сундук\n"
            f"Нажми 'Открыть', чтобы узнать, что внутри!"
        )
    elif current_event["type"] == "trap":
        event_info = (
            f"⚠️ **ЛОВУШКА**\n\n"
            f"Ты чувствуешь опасность...\n"
            f"💥 Урон: {current_event.get('damage', 20)}"
        )
    elif current_event["type"] == "rest":
        event_info = (
            f"🔥 **МЕСТО ОТДЫХА**\n\n"
            f"Ты находишь безопасное место для отдыха.\n"
            f"❤️ Восстановление: {current_event.get('heal', 30)} HP"
        )
    elif current_event["type"] == "transition":
        next_loc_id = current_event.get("to_location")
        next_loc = Act1.get_location_by_id(next_loc_id)
        event_info = (
            f"🚪 **ПЕРЕХОД**\n\n"
            f"{current_event.get('message', 'Ты нашел проход дальше...')}\n\n"
            f"➡️ Следующая локация: **{next_loc['name']}**"
        )
    else:
        event_info = "❓ Неизвестное событие"
    
    # Формируем текст
    text = (
        f"🗺️ **{location['name']}**\n"
        f"📊 Уровень локации: {area.current_level}\n\n"
        f"{progress_bar}\n\n"
        f"📍 **Событие {current_index + 1}/{len(events)}**\n\n"
        f"{event_info}\n\n"
        f"👤 {player.hp}/{player.max_hp} ❤️ | Ур. {player.level}"
    )
    
    # Клавиатура
    keyboard = get_dungeon_keyboard(current_event, player)
    
    try:
        await message.edit_text(text, reply_markup=keyboard)
    except:
        await message.answer(text, reply_markup=keyboard)


async def show_location_complete(message: types.Message, state: FSMContext):
    """Показывает экран завершения локации"""
    data = await state.get_data()
    player = data['player']
    
    location = Act1.get_location_by_id(player.current_location)
    next_loc = Act1.get_location_by_id(location["next_location"]) if location["next_location"] else None
    
    # Начисляем бонус за прохождение локации
    area = Area(player.current_location)
    bonus_exp = area.current_level * 10
    bonus_gold = area.current_level * 20
    
    player.exp += bonus_exp
    player.gold += bonus_gold
    
    # Проверка на повышение уровня
    from systems.progression import LevelSystem
    level_system = LevelSystem(player)
    levels = level_system.add_exp(0)  # Просто проверяем уровень
    
    text = (
        f"✅ **ЛОКАЦИЯ ПРОЙДЕНА!**\n\n"
        f"Ты успешно исследовал {location['name']}.\n\n"
        f"💰 Награда: +{bonus_gold} золота\n"
        f"✨ Награда: +{bonus_exp} опыта\n\n"
    )
    
    buttons = []
    
    if next_loc:
        text += f"➡️ Впереди: **{next_loc['name']}**"
        buttons.append([InlineKeyboardButton(text="➡️ Идти дальше", callback_data="go_to_next_location")])
    else:
        text += "🏁 Это была последняя локация акта!"
        buttons.append([InlineKeyboardButton(text="🏁 Завершить акт", callback_data="complete_act")])
    
    buttons.append([InlineKeyboardButton(text="🏚️ Вернуться в убежище", callback_data="return_to_haven")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await state.update_data(player=player)
    await message.edit_text(text, reply_markup=keyboard)


async def go_to_next_location(callback: types.CallbackQuery, state: FSMContext):
    """Переход к следующей локации"""
    data = await state.get_data()
    player = data['player']
    
    location = Act1.get_location_by_id(player.current_location)
    next_loc_id = location["next_location"]
    
    if next_loc_id:
        player.current_location = next_loc_id
        player.position_in_location = 0
        
        # Генерируем события для новой локации
        events = Act1.generate_location_events(next_loc_id)
        await state.update_data(player=player, dungeon_events=events)
        
        await show_dungeon(callback.message, state)
    else:
        await callback.answer("Дальше пути нет!")
    
    await callback.answer()


async def complete_act(callback: types.CallbackQuery, state: FSMContext):
    """Завершение акта"""
    data = await state.get_data()
    player = data['player']
    
    # Начисляем бонус за акт
    bonus_exp = 500
    bonus_gold = 300
    
    player.exp += bonus_exp
    player.gold += bonus_gold
    
    # Переходим к следующему акту
    from systems.progression import ActSystem
    act_system = ActSystem(player)
    success, message = act_system.go_to_next_act()
    
    if success:
        text = (
            f"🎉 **АКТ 1 ПРОЙДЕН!**\n\n"
            f"{message}\n\n"
            f"💰 Бонус: +{bonus_gold} золота\n"
            f"✨ Бонус: +{bonus_exp} опыта\n\n"
            f"Ты отправляешься в новое приключение!"
        )
        
        # Сбрасываем события
        await state.update_data(player=player, dungeon_events=[])
        
        # Показываем новую локацию
        await show_dungeon(callback.message, state)
    else:
        text = message
    
    await callback.message.edit_text(text)
    await callback.answer()
