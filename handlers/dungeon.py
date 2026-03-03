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
from data.act1 import Act1


class DungeonHandler:
    """Хендлер для управления подземельем"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self.loot_system = LootSystem()
        self.bot_username = None
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "enter_dungeon")
        async def enter_dungeon(callback: types.CallbackQuery, state: FSMContext):
            await self.enter_dungeon(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "next_step")
        async def next_step(callback: types.CallbackQuery, state: FSMContext):
            await self.next_step(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "go_to_next_location")
        async def go_to_next_location(callback: types.CallbackQuery, state: FSMContext):
            await self.go_to_next_location(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "complete_act")
        async def complete_act(callback: types.CallbackQuery, state: FSMContext):
            await self.complete_act(callback, state)
        
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
        
        @self.dp.callback_query(lambda c: c.data == "open_chest")
        async def open_chest(callback: types.CallbackQuery, state: FSMContext):
            await self.open_chest(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "trigger_trap")
        async def trigger_trap(callback: types.CallbackQuery, state: FSMContext):
            await self.trigger_trap(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "take_rest")
        async def take_rest(callback: types.CallbackQuery, state: FSMContext):
            await self.take_rest(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "start_battle_from_dungeon")
        async def start_battle_from_dungeon(callback: types.CallbackQuery, state: FSMContext):
            await self.handlers.battle.start_battle(callback, state)
    
    async def next_step_command(self, message: types.Message, state: FSMContext):
        """Обрабатывает команду next_step из гиперссылки"""
        await self.next_step(message, state)
    
    async def enter_dungeon(self, callback: types.CallbackQuery, state: FSMContext):
        """Вход в подземелье"""
        # Получаем username бота
        if not self.bot_username:
            bot_info = await self.bot.me()
            self.bot_username = bot_info.username
        
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
            f"{event_info}"
        )
        
        # Создаем клавиатуру для подземелья с учетом текущего события
        keyboard = self._create_dungeon_keyboard(current_event, player, current_index, events)
        
        try:
            await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except:
            await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    
    def _create_dungeon_keyboard(self, event, player, current_index, events):
        """Создает клавиатуру для подземелья с учетом текущей локации"""
        buttons = []
        
        # Определяем, был ли игрок уже в убежище
        has_been_in_haven = 2 in player.visited_locations
        
        # Базовая информация о персонаже
        player_hp_bar = self._create_hp_bar(player.hp, player.max_hp, 3)
        player_mana_bar = self._create_bar(player.mana, player.max_mana, 3)
        
        hp_text = f"❤️{player_hp_bar} {player.hp}/{player.max_hp}"
        mana_text = f"Ⓜ️{player_mana_bar} {player.mana}/{player.max_mana}"
        
        # Проверяем, является ли текущее событие битвой и не пройдена ли она
        is_battle_event = event["type"] == "battle" and not event.get("completed", False)
        
        # Первая строка - здоровье, кнопка вступления в бой (если нужно), мана
        if is_battle_event:
            # Если это битва и она не начата - показываем кнопку "Вступить в бой"
            buttons.append([
                InlineKeyboardButton(text=hp_text, callback_data="ignore"),
                InlineKeyboardButton(text="⚔️ Вступить в бой", callback_data="start_battle_from_dungeon"),
                InlineKeyboardButton(text=mana_text, callback_data="ignore")
            ])
        else:
            # Если это не битва или битва уже пройдена - показываем разделитель
            buttons.append([
                InlineKeyboardButton(text=hp_text, callback_data="ignore"),
                InlineKeyboardButton(text="➖", callback_data="ignore"),
                InlineKeyboardButton(text=mana_text, callback_data="ignore")
            ])
        
        # Для первой локации нет фласок
        if player.current_location == 1:
            # Только кнопки действий
            buttons.append([
                InlineKeyboardButton(text="⚔️ Атака", callback_data="battle_attack"),
                InlineKeyboardButton(text="💪 Мощная атака", callback_data="battle_heavy"),
                InlineKeyboardButton(text="⚡️ Умение", callback_data="battle_fast")
            ])
        else:
            # Для других локаций - показываем фласки
            # Находим фласки по типам
            health_flasks = [f for f in player.flasks if "💊" in f.emoji or "🧪" in f.emoji]
            mana_flasks = [f for f in player.flasks if "Ⓜ️" in f.emoji]
            
            # Создаем строку с фласками здоровья (3 слота)
            health_slots = ["⬜", "⬜", "⬜"]
            health_callbacks = ["ignore", "ignore", "ignore"]
            
            for i, flask in enumerate(health_flasks[:3]):
                flask_bar = self._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
                health_slots[i] = f"🟢💊[{flask_bar}]"
                health_callbacks[i] = f"battle_flask_health_{i}"
            
            health_row_text = f"{health_slots[0]} {health_slots[1]} {health_slots[2]}"
            
            # Создаем строку с фласками маны (3 слота)
            mana_slots = ["⬜", "⬜", "⬜"]
            mana_callbacks = ["ignore", "ignore", "ignore"]
            
            for i, flask in enumerate(mana_flasks[:3]):
                flask_bar = self._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
                mana_slots[i] = f"🟢Ⓜ️[{flask_bar}]"
                mana_callbacks[i] = f"battle_flask_mana_{i}"
            
            mana_row_text = f"{mana_slots[0]} {mana_slots[1]} {mana_slots[2]}"
            
            # Строка с фласками и картой
            buttons.append([
                InlineKeyboardButton(text=health_row_text, callback_data="ignore"),
                InlineKeyboardButton(text="🗺️ Карта", callback_data="show_map"),
                InlineKeyboardButton(text=mana_row_text, callback_data="ignore")
            ])
            
            # Кнопки для активных фласок
            health_buttons = []
            for i, callback in enumerate(health_callbacks):
                if callback != "ignore":
                    health_buttons.append(InlineKeyboardButton(text=f"💊{i+1}", callback_data=callback))
            
            mana_buttons = []
            for i, callback in enumerate(mana_callbacks):
                if callback != "ignore":
                    mana_buttons.append(InlineKeyboardButton(text=f"Ⓜ️{i+1}", callback_data=callback))
            
            if health_buttons:
                buttons.append(health_buttons)
            
            # Кнопки действий
            buttons.append([
                InlineKeyboardButton(text="⚔️ Атака", callback_data="battle_attack"),
                InlineKeyboardButton(text="💪 Мощная атака", callback_data="battle_heavy"),
                InlineKeyboardButton(text="⚡️ Умение", callback_data="battle_fast")
            ])
            
            if mana_buttons:
                buttons.append(mana_buttons)
        
        # Навигационные кнопки
        nav_row = []
        
        # Кнопка "Убежище" только если игрок уже был там
        if has_been_in_haven:
            nav_row.append(InlineKeyboardButton(text="🏚️ Убежище", callback_data="return_to_haven"))
        
        # Кнопка "Персонаж" доступна всегда
        nav_row.append(InlineKeyboardButton(text="👤 Персонаж", callback_data="battle_stats"))
        
        # Кнопка "Инвентарь" доступна всегда
        nav_row.append(InlineKeyboardButton(text="🎒 Инвентарь", callback_data="battle_inventory"))
        
        if nav_row:
            buttons.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _create_hp_bar(self, current, maximum, length):
        """Создает полоску здоровья"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)
    
    def _create_bar(self, current, maximum, length):
        """Создает полоску для любых показателей"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)
    
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
    
    async def next_step(self, message_or_callback, state: FSMContext):
        """Переход к следующему событию"""
        if isinstance(message_or_callback, types.CallbackQuery):
            message = message_or_callback.message
            callback = message_or_callback
        else:
            message = message_or_callback
            callback = None
        
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        
        player.position_in_location += 1
        await state.update_data(player=player)
        
        if player.position_in_location >= len(events):
            await self.show_location_complete(message, state)
        else:
            await self.show_dungeon(message, state)
        
        if callback:
            await callback.answer()
    
    async def show_location_complete(self, message: types.Message, state: FSMContext):
        """Завершение локации"""
        data = await state.get_data()
        player = data['player']
        
        location = AreaRegistry.get_location(player.current_location)
        if not location:
            return
        
        next_loc = AreaRegistry.get_next_location(player.current_location)
        
        area_level = AreaRegistry.get_area_level(player.current_location)
        bonus_exp = area_level * 10
        bonus_gold = area_level * 20
        
        player.exp += bonus_exp
        player.gold += bonus_gold
        
        # Проверяем, был ли игрок уже в убежище
        has_been_in_haven = 2 in player.visited_locations
        
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
        
        # Кнопка убежища только если игрок уже был там
        if has_been_in_haven:
            buttons.append([InlineKeyboardButton(text="🏚️ Вернуться в убежище", callback_data="return_to_haven")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await state.update_data(player=player)
        await message.edit_text(text, reply_markup=keyboard)
    
    async def go_to_next_location(self, callback: types.CallbackQuery, state: FSMContext):
        """Переход к следующей локации"""
        data = await state.get_data()
        player = data['player']
        
        location = AreaRegistry.get_location(player.current_location)
        if not location:
            await callback.answer("Ошибка: локация не найдена")
            return
        
        next_loc_id = location.get("next_location")
        if not next_loc_id:
            await callback.answer("Дальше пути нет!")
            return
        
        # Перемещаем игрока
        player.current_location = next_loc_id
        player.position_in_location = 0
        
        # Генерируем события для новой локации
        events = Act1.generate_location_events(next_loc_id)
        await state.update_data(player=player, dungeon_events=events)
        
        await self.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def complete_act(self, callback: types.CallbackQuery, state: FSMContext):
        """Завершение акта"""
        data = await state.get_data()
        player = data['player']
        
        # Переходим ко второму акту
        player.act = 2
        player.current_location = 8  # Первая локация второго акта
        player.position_in_location = 0
        
        # Генерируем события для новой локации
        events = Act1.generate_location_events(8)
        await state.update_data(player=player, dungeon_events=events)
        
        text = (
            f"🎉 **АКТ 1 ПРОЙДЕН!**\n\n"
            f"Ты выбрался из подземелья и попал в бескрайнюю пустыню.\n"
            f"Впереди тебя ждут пески забвения...\n\n"
            f"📍 Новая локация: Врата пустыни"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data="enter_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
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
        
        # Кнопка возврата
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def open_chest(self, callback: types.CallbackQuery, state: FSMContext):
        """Открытие сундука"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location
        
        if current_index >= len(events):
            await callback.answer("Ошибка: событие не найдена")
            return
        
        current_event = events[current_index]
        
        if current_event["type"] != "chest":
            await callback.answer("Это не сундук!")
            return
        
        # Генерируем лут из сундука
        area_level = AreaRegistry.get_area_level(player.current_location)
        loot = self.loot_system.generate_chest_loot(current_event["rarity"], area_level)
        
        loot_text = []
        for loot_item in loot:
            if loot_item.type == "gold":
                player.add_gold(loot_item.amount)
                loot_text.append(f"💰 {loot_item.amount} золота")
            elif loot_item.item:
                player.add_item(loot_item.item)
                loot_text.append(loot_item.get_name())
        
        player.add_chest_opened()
        
        # Отмечаем событие как пройденное
        events[current_index]["completed"] = True
        await state.update_data(player=player, dungeon_events=events)
        
        # Возвращаемся в подземелье
        await self.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def trigger_trap(self, callback: types.CallbackQuery, state: FSMContext):
        """Активация ловушки"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location
        
        if current_index >= len(events):
            await callback.answer("Ошибка: событие не найдена")
            return
        
        current_event = events[current_index]
        
        if current_event["type"] != "trap":
            await callback.answer("Это не ловушка!")
            return
        
        damage = current_event.get("damage", 20)
        actual_damage = player.take_damage(damage)
        player.add_trap_triggered()
        
        # Отмечаем событие как пройденное
        events[current_index]["completed"] = True
        await state.update_data(player=player, dungeon_events=events)
        
        if not player.is_alive():
            # В первой локации при смерти просто обновляем состояние
            if player.current_location == 1:
                player.hp = player.max_hp // 2
                player.mana = player.max_mana // 2
                player.position_in_location = 0
                await state.update_data(player=player)
        
        # Возвращаемся в подземелье
        await self.show_dungeon(callback.message, state)
        await callback.answer()
    
    async def take_rest(self, callback: types.CallbackQuery, state: FSMContext):
        """Отдых"""
        data = await state.get_data()
        player = data['player']
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location
        
        if current_index >= len(events):
            await callback.answer("Ошибка: событие не найдена")
            return
        
        current_event = events[current_index]
        
        if current_event["type"] != "rest":
            await callback.answer("Здесь нельзя отдохнуть!")
            return
        
        heal = current_event.get("heal", 30)
        player.heal(heal)
        
        # Отмечаем событие как пройденное
        events[current_index]["completed"] = True
        await state.update_data(player=player, dungeon_events=events)
        
        # Возвращаемся в подземелье
        await self.show_dungeon(callback.message, state)
        await callback.answer()
