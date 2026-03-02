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
from models.item import Item, MeleeWeapon, Flask
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
        
        # Первая строка - сообщение из лога
        first_message = "⚔️ Бой начался!"
        if battle_log and len(battle_log) > 0:
            last_entry = list(battle_log)[-1]
            if last_entry and last_entry.get("result"):
                first_message = last_entry["result"][-1]
        
        lines.append(first_message)
        lines.append("")
        
        # Информация о враге
        enemy_hp_bar = cls._create_hp_bar(enemy.hp, enemy.max_hp, 10)
        enemy_rarity = enemy.get_rarity_color()
        enemy_name = f"{enemy_rarity} {enemy.emoji} {enemy.name}"
        lines.append(f"{enemy_name} ❤️ {enemy_hp_bar} {enemy.hp}/{enemy.max_hp}")
        lines.append("")
        
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
        
        # Полоски здоровья и маны (неактивные кнопки)
        player_hp_bar = BattleUI._create_hp_bar(player.hp, player.max_hp, 6)
        player_mana_bar = BattleUI._create_bar(player.mana, player.max_mana, 6)
        
        hp_text = f"❤️ {player_hp_bar} {player.hp}/{player.max_hp}"
        mana_text = f"Ⓜ️ {player_mana_bar} {player.mana}/{player.max_mana}"
        
        # Первая строка - здоровье и мана (неактивные кнопки)
        buttons.append([
            InlineKeyboardButton(text=hp_text, callback_data="ignore"),
            InlineKeyboardButton(text="➖", callback_data="ignore"),
            InlineKeyboardButton(text=mana_text, callback_data="ignore")
        ])
        
        # Находим фласки по типам
        health_flasks = [f for f in player.flasks if "💊" in f.emoji or "🧪" in f.emoji]
        mana_flasks = [f for f in player.flasks if "Ⓜ️" in f.emoji]
        buff_flasks = [f for f in player.flasks if "✨" in f.emoji]
        defense_flasks = [f for f in player.flasks if "🛡️" in f.emoji]
        
        # Строка с фласками здоровья и маны
        health_text1 = "🟢💊🧪 [   ]"
        if len(health_flasks) > 0:
            flask = health_flasks[0]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            health_text1 = f"🟢💊🧪 [{flask_bar}]"
        
        mana_text1 = "🟢Ⓜ️🧪 [   ]"
        if len(mana_flasks) > 0:
            flask = mana_flasks[0]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            mana_text1 = f"🟢Ⓜ️🧪 [{flask_bar}]"
        
        buttons.append([
            InlineKeyboardButton(text=health_text1, callback_data="battle_flask_health_0" if len(health_flasks) > 0 else "ignore"),
            InlineKeyboardButton(text="Атака оружием ⚔️", callback_data="battle_attack"),
            InlineKeyboardButton(text=mana_text1, callback_data="battle_flask_mana_0" if len(mana_flasks) > 0 else "ignore")
        ])
        
        # Вторая строка с фласками
        health_text2 = "🟢💊🧪 [   ]"
        if len(health_flasks) > 1:
            flask = health_flasks[1]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            health_text2 = f"🟢💊🧪 [{flask_bar}]"
        
        mana_text2 = "🟢Ⓜ️🧪 [   ]"
        if len(mana_flasks) > 1:
            flask = mana_flasks[1]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            mana_text2 = f"🟢Ⓜ️🧪 [{flask_bar}]"
        
        buttons.append([
            InlineKeyboardButton(text=health_text2, callback_data="battle_flask_health_1" if len(health_flasks) > 1 else "ignore"),
            InlineKeyboardButton(text="Мощная атака 💪", callback_data="battle_heavy"),
            InlineKeyboardButton(text=mana_text2, callback_data="battle_flask_mana_1" if len(mana_flasks) > 1 else "ignore")
        ])
        
        # Третья строка - бафф, защита и умение
        buff_text = "⚪️✨🧪 [   ]"
        if len(buff_flasks) > 0:
            flask = buff_flasks[0]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            buff_text = f"⚪️✨🧪 [{flask_bar}]"
        
        defense_text = "🔵🛡️🧪 [   ]"
        if len(defense_flasks) > 0:
            flask = defense_flasks[0]
            flask_bar = BattleUI._create_bar(flask.current_uses, flask.flask_data["uses"], 3)
            defense_text = f"🔵🛡️🧪 [{flask_bar}]"
        
        buttons.append([
            InlineKeyboardButton(text=buff_text, callback_data="battle_flask_buff_0" if len(buff_flasks) > 0 else "ignore"),
            InlineKeyboardButton(text="Умение ⚡️", callback_data="battle_fast"),
            InlineKeyboardButton(text=defense_text, callback_data="battle_flask_defense_0" if len(defense_flasks) > 0 else "ignore")
        ])
        
        # Четвертая строка - навигация
        buttons.append([
            InlineKeyboardButton(text="👤 Персонаж", callback_data="battle_stats"),
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="battle_inventory"),
            InlineKeyboardButton(text="🌀 Побег", callback_data="battle_run")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @classmethod
    def get_empty_button(cls):
        """Создает пустую неактивную кнопку"""
        return InlineKeyboardButton(text="➖", callback_data="ignore")


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
            await callback.answer()
        
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
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_health_"))
        async def battle_flask_health(callback: types.CallbackQuery, state: FSMContext):
            flask_index = int(callback.data.split('_')[3])
            await self.use_flask(callback, state, flask_index, "health")
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_mana_"))
        async def battle_flask_mana(callback: types.CallbackQuery, state: FSMContext):
            flask_index = int(callback.data.split('_')[3])
            await self.use_flask(callback, state, flask_index, "mana")
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_buff_"))
        async def battle_flask_buff(callback: types.CallbackQuery, state: FSMContext):
            flask_index = int(callback.data.split('_')[3])
            await self.use_flask(callback, state, flask_index, "buff")
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_defense_"))
        async def battle_flask_defense(callback: types.CallbackQuery, state: FSMContext):
            flask_index = int(callback.data.split('_')[3])
            await self.use_flask(callback, state, flask_index, "defense")
        
        @self.dp.callback_query(lambda c: c.data == "battle_stats")
        async def battle_stats(callback: types.CallbackQuery, state: FSMContext):
            await self.show_player_stats(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_inventory")
        async def battle_inventory(callback: types.CallbackQuery, state: FSMContext):
            await self.show_inventory(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "start_battle")
        async def start_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.start_battle(callback, state)
    
    async def show_inventory(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает инвентарь"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("❌ Игрок не найден")
            return
        
        text = self._format_inventory(player)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад в бой", callback_data="battle_back")]
        ])
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    def _format_inventory(self, player):
        """Форматирует инвентарь для отображения"""
        if not player.inventory and not player.flasks:
            return "🎒 **Инвентарь пуст**\n\n💰 Золото: {player.gold}"
        
        lines = ["🎒 **ИНВЕНТАРЬ**\n"]
        
        # Группируем предметы по типу
        weapons = []
        armor = []
        other = []
        flasks = []
        
        from models.item import ItemType
        for item in player.inventory:
            if item.item_type == ItemType.WEAPON:
                weapons.append(item)
            elif item.item_type in [ItemType.HELMET, ItemType.ARMOR, ItemType.GLOVES, 
                                    ItemType.BOOTS, ItemType.BELT]:
                armor.append(item)
            elif item.item_type in [ItemType.RING, ItemType.AMULET]:
                other.append(item)
            elif item.item_type == ItemType.FLASK:
                flasks.append(item)
        
        index = 1
        
        if weapons:
            lines.append("**⚔️ ОРУЖИЕ:**")
            for item in weapons:
                lines.append(f"{index}. {item.get_name_colored()}")
                index += 1
            lines.append("")
        
        if armor:
            lines.append("**🛡️ БРОНЯ:**")
            for item in armor:
                lines.append(f"{index}. {item.get_name_colored()}")
                index += 1
            lines.append("")
        
        if other:
            lines.append("**💍 АКСЕССУАРЫ:**")
            for item in other:
                lines.append(f"{index}. {item.get_name_colored()}")
                index += 1
            lines.append("")
        
        if flasks:
            lines.append("**🧪 ФЛАСКИ:**")
            for item in flasks:
                flask_type = "🟢💊" if "💊" in item.emoji else "🟢Ⓜ️" if "Ⓜ️" in item.emoji else "⚪️✨" if "✨" in item.emoji else "🔵🛡️"
                lines.append(f"{index}. {flask_type} {item.get_name_colored()} [{item.current_uses}/{item.flask_data['uses']}]")
                index += 1
            lines.append("")
        
        lines.append(f"💰 Золото: {player.gold}")
        
        return "\n".join(lines)
    
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
            await message.answer("❌ Ошибка состояния боя")
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
        elif flask_type == "buff":
            available_flasks = [f for f in player.flasks if "✨" in f.emoji]
        elif flask_type == "defense":
            available_flasks = [f for f in player.flasks if "🛡️" in f.emoji]
        
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
        
        elif flask_type == "defense":
            result_msg = "🛡️ Использована фласка защиты"
            flask.use()
        
        else:
            result_msg = "✨ Использована фласка баффа"
            flask.use()
        
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
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад в бой", callback_data="battle_back")]
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
                loot_text.append(f"💰 {loot_item.amount} золота")
            elif loot_item.item:
                player.add_item(loot_item.item)
                loot_text.append(loot_item.get_name())
        
        # Отмечаем событие как пройденное
        if current_index < len(events):
            events[current_index]["completed"] = True
            await state.update_data(dungeon_events=events)
        
        text = f"🎉 **ПОБЕДА!**\n\n"
        text += f"Ты победил {enemy.emoji} {enemy.name}!\n\n"
        text += f"✨ Опыт: +{exp_gained}\n"
        text += f"💰 Золото: +{gold_gained}\n"
        
        if charges_restored > 0:
            text += f"🧪 Восстановлено зарядов фласок: +{charges_restored}\n"
        
        if levels_gained > 0:
            text += f"⬆️ Новый уровень: {player.level}!\n"
        
        if loot_text:
            text += f"\n**Добыча:**\n"
            for item in loot_text:
                text += f"  {item}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Идти дальше", callback_data="next_step")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")]
        ])
        
        await state.update_data(player=player)
        
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def handle_defeat(self, message: types.Message, state: FSMContext):
        """Обрабатывает поражение"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ Ошибка состояния")
            return
        
        player.add_death()
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
        
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def handle_flee(self, message: types.Message, state: FSMContext):
        """Обрабатывает побег"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await message.answer("❌ Ошибка состояния")
            return
        
        text = (
            f"🏃 **ПОБЕГ**\n\n"
            f"Ты успешно сбежал от врага!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data="next_step")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")]
        ])
        
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
