import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.enemy import Enemy
from systems.area_level import AreaRegistry, MonsterLevelSystem
from systems.loot import LootSystem
from utils.keyboards import get_dungeon_keyboard
from utils.helpers import format_progress_bar, format_dungeon_view
from data.act1 import Act1  # Для монстров и событий (пока оставляем)


class DungeonHandler:
    """Хендлер для управления подземельем"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
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
        
        @self.dp.callback_query(lambda c: c.data == "back_to_dungeon")
        async def back_to_dungeon(callback: types.CallbackQuery, state: FSMContext):
            await self.show_dungeon(callback.message, state)
            await callback.answer()
    
    async def enter_dungeon(self, callback: types.CallbackQuery, state: FSMContext):
        """Вход в подземелье"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        if 'dungeon_events' not in data or not data['dungeon_events']:
            events = Act1.generate_location_events(player.current_location)
            await state.update_data(dungeon_events=events)
        
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
            events = Act1.generate_location_events(player.current_location)
            await state.update_data(dungeon_events=events)
        
        current_index = player.position_in_location
        if current_index >= len(events):
            await self.show_location_complete(message, state)
            return
        
        current_event = events[current_index]
        
        location = AreaRegistry.get_location(player.current_location)
        if not location:
            await message.answer("Ошибка: локация не найдена")
            return
        
        # Прогресс-бар
        progress_bar = format_progress_bar(current_index, len(events),
                                          [e.get("type") for e in events])
        
        # Информация о событии
        event_info = self._format_event(current_event)
        
        area_level = AreaRegistry.get_area_level(player.current_location)
        
        text = (
            f"🗺️ **{location['name']}**\n"
            f"📊 Уровень локации: {area_level}\n\n"
            f"{progress_bar}\n\n"
            f"📍 **Событие {current_index + 1}/{len(events)}**\n\n"
            f"{event_info}\n\n"
            f"👤 {player.hp}/{player.max_hp} ❤️ | Ур. {player.level}"
        )
        
        keyboard = get_dungeon_keyboard(current_event, player)
        
        try:
            await message.edit_text(text, reply_markup=keyboard)
        except:
            await message.answer(text, reply_markup=keyboard)
    
    def _format_event(self, event):
        """Форматирует событие"""
        if event["type"] == "battle":
            monster = event["monster"]
            return (
                f"⚔️ **БИТВА**\n\n"
                f"{monster['emoji']} **{monster['name']}**\n"
                f"❤️ HP: {monster['base_hp']}\n"
                f"_{monster['description']}_"
            )
        elif event["type"] == "chest":
            rarity_colors = {"common": "🟢", "magic": "🟣", "rare": "🟡"}
            rarity_name = rarity_colors.get(event["rarity"], "🟢")
            return f"📦 **СУНДУК**\n\n{rarity_name} сундук"
        elif event["type"] == "trap":
            return f"⚠️ **ЛОВУШКА**\n\n💥 Урон: {event.get('damage', 20)}"
        elif event["type"] == "rest":
            return f"🔥 **МЕСТО ОТДЫХА**\n\n❤️ Восстановление: {event.get('heal', 30)} HP"
        elif event["type"] == "transition":
            next_loc_id = event.get("to_location")
            next_loc = AreaRegistry.get_location(next_loc_id)
            next_name = next_loc["name"] if next_loc else "Неизвестно"
            return (
                f"🚪 **ПЕРЕХОД**\n\n"
                f"{event.get('message', 'Ты нашел проход дальше...')}\n\n"
                f"➡️ Следующая локация: **{next_name}**"
            )
        return "❓ Неизвестное событие"
    
    async def next_step(self, callback: types.CallbackQuery, state: FSMContext):
        """Переход к следующему событию"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        
        player.position_in_location += 1
        await state.update_data(player=player)
        
        if player.position_in_location >= len(events):
            await self.show_location_complete(callback.message, state)
        else:
            await self.show_dungeon(callback.message, state)
        
        await callback.answer()
    
    async def show_location_complete(self, message: types.Message, state: FSMContext):
        """Завершение локации"""
        data = await state.get_data()
        player = data['player']
        
        location = AreaRegistry.get_location(player.current_location)
        if not location:
            return
        
        next_loc = AreaRegistry.get_location(location.get("next_location"))
        
        area_level = AreaRegistry.get_area_level(player.current_location)
        bonus_exp = area_level * 10
        bonus_gold = area_level * 20
        
        player.exp += bonus_exp
        player.gold += bonus_gold
        
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
    
    async def return_to_haven(self, callback: types.CallbackQuery, state: FSMContext):
        """Возврат в убежище"""
        await self.handlers.haven.enter_haven(callback, state)
    
    async def show_map(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает карту"""
        data = await state.get_data()
        player = data['player']
        
        locations = AreaRegistry.get_locations_by_act(player.act)
        
        text = f"🗺️ **КАРТА АКТА {player.act}**\n\n"
        
        for loc_id, loc_data in locations:
            if loc_id == player.current_location:
                text += f"👉 **{loc_data['name']}** (текущая)\n"
            elif loc_id in player.visited_locations:
                text += f"✅ {loc_data['name']}\n"
            else:
                text += f"⬜ {loc_data['name']}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
