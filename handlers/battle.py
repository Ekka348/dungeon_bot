import asyncio
import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
import os
from collections import deque
from urllib.parse import quote

from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask, ItemType
from data.act1 import Act1
from systems.combat import CombatSystem, CombatAction, ActionResult
from systems.area_level import Area, DifficultyCalculator, MonsterLevelSystem
from systems.loot import LootSystem
from systems.progression import ProgressionSystem

# ============= ИНТЕРФЕЙС БОЯ С ИНЛАЙН КНОПКАМИ =============

class BattleUI:
    """Класс для формирования интерфейса боя с инлайн кнопками"""
    
    @classmethod
    def create_battle_screen(cls, player, enemy, battle_log):
        """Создает текст боя"""
        
        lines = []
        
        # Информация о враге
        enemy_hp_bar = cls._create_hp_bar(enemy.hp, enemy.max_hp, 10)
        enemy_rarity = enemy.get_rarity_color()
        enemy_name = f"{enemy_rarity} {enemy.emoji} {enemy.name}"
        lines.append(f"{enemy_name} ❤️{enemy_hp_bar} {enemy.hp}/{enemy.max_hp}")
        lines.append("")
        
        # Лог боя (последние 3 сообщения)
        if battle_log and len(battle_log) > 0:
            log_list = list(battle_log)
            for entry in log_list[-3:]:
                if entry and entry.get("result"):
                    for msg in entry["result"][-1:]:  # Берем последнее сообщение из каждого хода
                        lines.append(msg)
        
        return "\n".join(lines)
    
    @classmethod
    def _create_hp_bar(cls, current, maximum, length):
        """Создает полоску здоровья"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)
    
    @classmethod
    def _create_bar(cls, current, maximum, length):
        """Создает полоску для любых показателей"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)


# ============= КЛАВИАТУРА БОЯ =============

class BattleKeyboard:
    """Класс для создания клавиатуры боя"""
    
    @classmethod
    def get_battle_keyboard(cls, player, bot_username):
        """Создает клавиатуру для боя"""
        
        buttons = []
        
        # Полоски здоровья и маны
        player_hp_bar = BattleUI._create_hp_bar(player.hp, player.max_hp, 5)
        player_mana_bar = BattleUI._create_bar(player.mana, player.max_mana, 5)
        
        hp_text = f"❤️{player_hp_bar} {player.hp}/{player.max_hp}"
        mana_text = f"Ⓜ️{player_mana_bar} {player.mana}/{player.max_mana}"
        
        # Первая строка - здоровье и мана (неактивные кнопки)
        buttons.append([
            InlineKeyboardButton(text=hp_text, callback_data="ignore"),
            InlineKeyboardButton(text="➖", callback_data="ignore"),
            InlineKeyboardButton(text=mana_text, callback_data="ignore")
        ])
        
        # Находим фласки по типам
        health_flasks = [f for f in player.flasks if "💊" in f.emoji or "🧪" in f.emoji]
        mana_flasks = [f for f in player.flasks if "Ⓜ️" in f.emoji]
        
        # Проверяем, находится ли игрок в убежище или уже получил базовые предметы
        has_portal = player.current_location == 2 or player.has_portal
        
        # Определяем, есть ли у игрока фласки
        has_any_flask = len(health_flasks) > 0 or len(mana_flasks) > 0
        
        if has_any_flask:
            # Создаем строку с фласками здоровья (3 слота)
            health_slots = ["⬜", "⬜", "⬜"]
            health_callbacks = ["ignore", "ignore", "ignore"]
            
            for i, flask in enumerate(health_flasks[:3]):
                flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
                health_slots[i] = f"🟢💊[{flask_bar}]"
                health_callbacks[i] = f"battle_flask_health_{i}"
            
            health_row_text = f"{health_slots[0]} {health_slots[1]} {health_slots[2]}"
            
            # Создаем строку с фласками маны (3 слота)
            mana_slots = ["⬜", "⬜", "⬜"]
            mana_callbacks = ["ignore", "ignore", "ignore"]
            
            for i, flask in enumerate(mana_flasks[:3]):
                flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
                mana_slots[i] = f"🟢Ⓜ️[{flask_bar}]"
                mana_callbacks[i] = f"battle_flask_mana_{i}"
            
            mana_row_text = f"{mana_slots[0]} {mana_slots[1]} {mana_slots[2]}"
            
            # Строка с фласками и картой
            buttons.append([
                InlineKeyboardButton(text=health_row_text, callback_data="ignore"),
                InlineKeyboardButton(text="🗺️ Карта", callback_data="show_map"),
                InlineKeyboardButton(text=mana_row_text, callback_data="ignore")
            ])
            
            # Кнопки для активных фласок здоровья
            health_buttons = []
            for i, callback in enumerate(health_callbacks):
                if callback != "ignore":
                    health_buttons.append(InlineKeyboardButton(text=f"💊{i+1}", callback_data=callback))
            
            if health_buttons:
                buttons.append(health_buttons)
            
            # Кнопки действий
            buttons.append([
                InlineKeyboardButton(text="⚔️ Атака", callback_data="battle_attack"),
                InlineKeyboardButton(text="💪 Мощная атака", callback_data="battle_heavy"),
                InlineKeyboardButton(text="⚡️ Умение", callback_data="battle_fast")
            ])
            
            # Кнопки для активных фласок маны
            mana_buttons = []
            for i, callback in enumerate(mana_callbacks):
                if callback != "ignore":
                    mana_buttons.append(InlineKeyboardButton(text=f"Ⓜ️{i+1}", callback_data=callback))
            
            if mana_buttons:
                buttons.append(mana_buttons)
        else:
            # Нет фласок - только кнопки действий
            buttons.append([
                InlineKeyboardButton(text="⚔️ Атака", callback_data="battle_attack"),
                InlineKeyboardButton(text="💪 Мощная атака", callback_data="battle_heavy"),
                InlineKeyboardButton(text="⚡️ Умение", callback_data="battle_fast")
            ])
        
        # Навигационная строка
        nav_buttons = [
            InlineKeyboardButton(text="👤 Персонаж", callback_data="battle_stats"),
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="battle_inventory")
        ]
        
        # Кнопка портала доступна только если игрок в убежище или уже получил свиток
        if has_portal:
            nav_buttons.append(InlineKeyboardButton(text="🌀 Побег", callback_data="battle_run"))
        
        buttons.append(nav_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= ОСНОВНОЙ ХЕНДЛЕР БОЯ =============

class BattleHandler:
    """Хендлер для управления боем"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self.loot_system = LootSystem()
        self.bot_username = None
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "ignore")
        async def ignore_callback(callback: types.CallbackQuery):
            await callback.answer("❌ Недоступно")
        
        @self.dp.callback_query(lambda c: c.data == "battle_attack")
        async def battle_attack(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_heavy")
        async def battle_heavy(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.HEAVY_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_fast")
        async def battle_fast(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.FAST_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_run")
        async def battle_run(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.RUN)
        
        @self.dp.callback_query(lambda c: c.data == "battle_back")
        async def battle_back(callback: types.CallbackQuery, state: FSMContext):
            # Проверяем, есть ли активный бой
            data = await state.get_data()
            battle_enemy = data.get('battle_enemy')
            
            if battle_enemy:
                # Если бой идет - возвращаемся в бой
                await self.show_battle(callback.message, state)
            else:
                # Если боя нет - возвращаемся в подземелье
                await self.handlers.dungeon.show_dungeon(callback.message, state)
            
            await callback.answer()
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_health_"))
        async def battle_flask_health(callback: types.CallbackQuery, state: FSMContext):
            try:
                flask_index = int(callback.data.split('_')[3])
                await self.use_flask(callback, state, flask_index, "health")
            except:
                await callback.answer("❌ Ошибка")
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_mana_"))
        async def battle_flask_mana(callback: types.CallbackQuery, state: FSMContext):
            try:
                flask_index = int(callback.data.split('_')[3])
                await self.use_flask(callback, state, flask_index, "mana")
            except:
                await callback.answer("❌ Ошибка")
        
        @self.dp.callback_query(lambda c: c.data == "battle_stats")
        async def battle_stats(callback: types.CallbackQuery, state: FSMContext):
            await self.show_player_stats(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_inventory")
        async def battle_inventory(callback: types.CallbackQuery, state: FSMContext):
            await self.handlers.inventory.show_inventory(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "start_battle")
        async def start_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.start_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "next_step")
        async def next_step(callback: types.CallbackQuery, state: FSMContext):
            await self.handlers.dungeon.next_step(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "return_to_haven")
        async def return_to_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.handlers.haven.enter_haven(callback, state)
    
    async def start_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Начинает бой"""
        # Получаем username бота
        if not self.bot_username:
            bot_info = await self.bot.me()
            self.bot_username = bot_info.username
        
        data = await state.get_data()
        player = data.get('player')
        if not player:
            await callback.answer("❌ Игрок не найден")
            return
        
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location
        
        if current_index >= len(events):
            await callback.answer("Ошибка: событие не найдено")
            return
        
        current_event = events[current_index]
        
        if current_event["type"] not in ["battle", "boss"]:
            await callback.answer("Это не битва!")
            return
        
        # Получаем данные монстра
        monster_data = current_event["monster"]
        
        # Получаем уровень локации
        area = Area(player.current_location)
        area_level = area.current_level
        
        # Создаем врага
        enemy = Enemy.from_monster_data(
            monster_data, 
            area_level, 
            current_event.get("rarity", "common")
        )
        
        # Добавляем игроку ману, если её нет
        if not hasattr(player, 'mana'):
            player.mana = 100
            player.max_mana = 100
        
        # Создаем боевую систему
        combat = CombatSystem(player, enemy)
        
        # Создаем начальный лог
        battle_log = deque(maxlen=10)
        battle_log.append({"turn": 0, "result": ["⚔️ Бой начался!"]})
        
        # Сохраняем состояние боя
        await state.update_data(
            player=player,
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=1,
            battle_log=battle_log
        )
        
        # Удаляем сообщение с кнопкой
        try:
            await callback.message.delete()
        except:
            pass
        
        # Показываем бой
        await self.show_battle(callback.message, state, is_new=True)
        await callback.answer()
    
    async def show_battle(self, message: types.Message, state: FSMContext, is_new: bool = False):
        """Показывает экран боя"""
        data = await state.get_data()
        player = data.get('player')
        enemy = data.get('battle_enemy')
        combat = data.get('combat_system')
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not player or not enemy or not combat:
            # Если нет боя, показываем подземелье
            await self.handlers.dungeon.show_dungeon(message, state)
            return
        
        # Создаем текст боя
        ui = BattleUI.create_battle_screen(player, enemy, battle_log)
        
        # Создаем клавиатуру
        keyboard = BattleKeyboard.get_battle_keyboard(player, self.bot_username)
        
        try:
            if is_new:
                await message.answer(ui, reply_markup=keyboard)
            else:
                await message.edit_text(ui, reply_markup=keyboard)
        except Exception as e:
            try:
                await message.answer(ui, reply_markup=keyboard)
            except:
                pass
    
    async def use_flask(self, callback: types.CallbackQuery, state: FSMContext, flask_index: int, flask_type: str):
        """Использование фласки"""
        data = await state.get_data()
        player = data.get('player')
        enemy = data.get('battle_enemy')
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not player or not enemy or not combat:
            await callback.answer("❌ Ошибка состояния боя")
            return
        
        # Находим подходящую фласку по типу
        available_flasks = []
        if flask_type == "health":
            available_flasks = [f for f in player.flasks if "💊" in f.emoji]
        elif flask_type == "mana":
            available_flasks = [f for f in player.flasks if "Ⓜ️" in f.emoji]
        
        if flask_index >= len(available_flasks):
            await callback.answer("❌ Фласка не найдена")
            return
        
        flask = available_flasks[flask_index]
        
        # Используем фласку
        if flask_type == "health":
            heal = flask.use()
            if heal > 0:
                player.heal(heal)
                result_msg = f"🧪 Использована фласка здоровья: +{heal} HP"
            else:
                result_msg = "❌ Фласка пуста!"
        
        elif flask_type == "mana":
            mana_restore = flask.use()
            if mana_restore > 0:
                player.restore_mana(mana_restore)
                result_msg = f"💙 Использована фласка маны: +{mana_restore} MP"
            else:
                result_msg = "❌ Фласка пуста!"
        
        # Добавляем в лог
        battle_log.append({"turn": turn, "result": [result_msg]})
        
        # Ход врага
        enemy_action = combat._choose_enemy_action()
        if enemy_action in [CombatAction.ATTACK, CombatAction.HEAVY_ATTACK]:
            damage = enemy.attack()
            if enemy_action == CombatAction.HEAVY_ATTACK:
                damage = int(damage * 1.5)
            
            actual_damage = player.take_damage(damage)
            battle_log.append({"turn": turn, "result": [f"💥 {enemy.name} атакует: {actual_damage} урона"]})
        
        # Обновляем состояние
        await state.update_data(
            player=player,
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=turn + 1,
            battle_log=battle_log
        )
        
        # Проверяем смерть
        if not player.is_alive():
            await self.handle_defeat(callback.message, state)
            await callback.answer()
            return
        
        await self.show_battle(callback.message, state)
        await callback.answer()
    
    async def process_action(self, callback: types.CallbackQuery, state: FSMContext, action: CombatAction):
        """Обрабатывает действие игрока"""
        data = await state.get_data()
        player = data.get('player')
        enemy = data.get('battle_enemy')
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not player or not enemy or not combat:
            await callback.answer("❌ Ошибка состояния боя")
            return
        
        # Проверяем, доступен ли побег
        if action == CombatAction.RUN:
            has_portal = player.current_location == 2 or player.has_portal
            if not has_portal:
                await callback.answer("❌ У тебя нет свитка портала!")
                return
        
        # Проверяем ману для действий, кроме обычной атаки и побега
        if action not in [CombatAction.ATTACK, CombatAction.RUN]:
            mana_cost = combat.MANA_COSTS.get(action, 5)
            if hasattr(player, 'mana') and player.mana < mana_cost:
                await callback.answer(f"❌ Недостаточно маны! Нужно {mana_cost}")
                return
            if hasattr(player, 'mana'):
                player.mana -= mana_cost
        
        # Обрабатываем действие
        result = combat.process_turn(action)
        
        # Добавляем результат в лог
        for msg in result.messages:
            battle_log.append({"turn": turn, "result": [msg]})
        
        # Обновляем данные
        await state.update_data(
            player=player,
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=turn + 1,
            battle_log=battle_log
        )
        
        # Проверяем результаты боя
        if result.fled:
            await self.handle_flee(callback.message, state)
            await callback.answer()
            return
        
        if combat.is_enemy_dead():
            await self.handle_victory(callback.message, state)
            await callback.answer()
            return
        
        if combat.is_player_dead():
            await self.handle_defeat(callback.message, state)
            await callback.answer()
            return
        
        # Восстанавливаем немного маны каждый ход
        if hasattr(player, 'restore_mana'):
            player.restore_mana(3)
        
        await self.show_battle(callback.message, state)
        await callback.answer()
    
    async def show_player_stats(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает статистику игрока"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("❌ Игрок не найден")
            return
        
        text = (
            f"👤 **{player.name}** | Ур. {player.level}\n\n"
            f"**Характеристики:**\n"
            f"💪 Сила: {player.strength}\n"
            f"🏹 Ловкость: {player.dexterity}\n"
            f"📚 Интеллект: {player.intelligence}\n\n"
            f"**Боевые статы:**\n"
            f"❤️ HP: {player.hp}/{player.max_hp}\n"
            f"💙 Мана: {player.mana}/{player.max_mana}\n"
            f"⚔️ Урон: {player.get_total_damage()}\n"
            f"🛡️ Защита: {player.defense}\n"
            f"🎯 Точность: {player.accuracy}%\n"
            f"🔥 Крит: {player.crit_chance}% x{player.crit_multiplier}%\n\n"
            f"💰 Золото: {player.gold}\n"
            f"✨ Опыт: {player.exp}/{player.level * 100}"
        )
        
        # Кнопка "Назад" (без указания "в бой")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="battle_back")]
        ])
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    async def handle_victory(self, message: types.Message, state: FSMContext):
        """Обрабатывает победу"""
        data = await state.get_data()
        player = data.get('player')
        enemy = data.get('battle_enemy')
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location if player else 0
        
        if not player or not enemy:
            await message.answer("❌ Ошибка состояния")
            return
        
        exp_gained = enemy.get_exp_reward()
        levels_gained = player.add_exp(exp_gained)
        gold_gained = enemy.get_gold_reward()
        player.add_gold(gold_gained)
        charges_restored = player.add_flask_charge()
        player.add_kill(enemy.name)
        
        # Генерируем лут
        area = Area(player.current_location)
        area_level = area.current_level
        
        loot = self.loot_system.generate_loot(
            enemy.rarity, 
            area_level, 
            enemy.area_level,
            player.current_location
        )
        
        loot_text = []
        for loot_item in loot:
            if loot_item.type == "gold":
                player.add_gold(loot_item.amount)
                loot_text.append(f"💰 {loot_item.amount} золота")
            elif loot_item.item:
                player.add_item(loot_item.item)
                loot_text.append(loot_item.get_name())
        
        # Отмечаем событие как пройденное
        if current_index < len(events):
            events[current_index]["completed"] = True
            await state.update_data(dungeon_events=events)
        
        # Удаляем врага из состояния (бой окончен)
        await state.update_data(battle_enemy=None, combat_system=None)
        
        # Показываем подземелье с обновленным событием
        await self.handlers.dungeon.show_dungeon(message, state)
    
    async def handle_defeat(self, message: types.Message, state: FSMContext):
        """Обрабатывает поражение"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ Ошибка состояния")
            return
        
        player.add_death()
        
        # В первой локации при смерти просто возрождаемся в начале локации
        if player.current_location == 1:
            player.hp = player.max_hp // 2
            player.mana = player.max_mana // 2
            player.position_in_location = 0
            
            text = (
                f"💀 **ПОРАЖЕНИЕ...**\n\n"
                f"Ты потерял сознание, но очнулся в начале подземелья.\n"
                f"❤️ Здоровье: {player.hp}/{player.max_hp}\n"
                f"💙 Мана: {player.mana}/{player.max_mana}"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➡️ Продолжить", callback_data="next_step")]
            ])
            
            await state.update_data(battle_enemy=None, combat_system=None)
            await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            # В других локациях возрождаемся в убежище
            player.hp = player.max_hp // 2
            player.mana = player.max_mana // 2
            
            for flask in player.flasks:
                flask.current_uses = max(1, flask.flask_data["uses"] // 2)
            
            player.current_location = 2
            player.position_in_location = 0
            
            text = (
                f"💀 **ПОРАЖЕНИЕ...**\n\n"
                f"Ты очнулся в убежище, едва живой.\n"
                f"❤️ Здоровье: {player.hp}/{player.max_hp}\n"
                f"💙 Мана: {player.mana}/{player.max_mana}"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")]
            ])
            
            await state.update_data(
                player=player,
                battle_enemy=None,
                combat_system=None,
                battle_log=deque(maxlen=10)
            )
            
            await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def handle_flee(self, message: types.Message, state: FSMContext):
        """Обрабатывает побег"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ Ошибка состояния")
            return
        
        # Проверяем, есть ли портал
        has_portal = player.current_location == 2 or player.has_portal
        if not has_portal:
            await message.answer("❌ У тебя нет свитка портала!")
            return
        
        text = (
            f"🏃 **ПОБЕГ**\n\n"
            f"Ты успешно сбежал от врага!"
        )
        
        # Определяем доступные кнопки после побега
        keyboard_buttons = [
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data="next_step")]
        ]
        
        if player.current_location != 1 and (player.current_location == 2 or 2 in player.visited_locations):
            keyboard_buttons.append([InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await state.update_data(
            battle_enemy=None,
            combat_system=None,
            battle_log=deque(maxlen=10)
        )
        
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
