import asyncio
import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
import os
from collections import deque

from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask
from data.act1 import Act1
from systems.combat import CombatSystem, CombatAction, ActionResult
from systems.area_level import Area, DifficultyCalculator, MonsterLevelSystem
from systems.loot import LootSystem
from systems.progression import ProgressionSystem
from utils.keyboards import get_battle_action_keyboard, get_battle_result_keyboard
from utils.helpers import format_battle_view, format_hp_bar

# ============= НОВЫЙ ИНТЕРФЕЙС БОЯ =============

class BattleUI:
    """Класс для формирования нового интерфейса боя"""
    
    # Символы для рамок
    TOP_LEFT = "┌"
    TOP_RIGHT = "┐"
    BOTTOM_LEFT = "└"
    BOTTOM_RIGHT = "┘"
    HORIZONTAL = "─"
    VERTICAL = "│"
    CROSS = "┼"
    TOP_MID = "┬"
    BOTTOM_MID = "┴"
    
    @classmethod
    def create_battle_screen(cls, player, enemy, combat, battle_log, turn):
        """Создает полный экран боя"""
        
        # Формируем строки
        lines = []
        
        # Заголовок с раундом
        lines.append(f"⚔️ **РАУНД {turn}**")
        lines.append("")
        
        # Информация о враге
        enemy_hp_bar = enemy.get_hp_bar()
        enemy_rarity = enemy.get_rarity_color()
        enemy_name = f"{enemy_rarity} {enemy.emoji} **{enemy.name}**"
        lines.append(f"  {enemy_name}  {enemy_hp_bar}")
        lines.append("")
        
        # Верхняя граница
        lines.append("🟫" * 30)
        lines.append("")
        
        # Лог боя (последние 3 сообщения)
        log_messages = cls._get_battle_log(battle_log)
        for msg in log_messages:
            padding = " " * ((60 - len(msg)) // 2)
            lines.append(f"{padding}{msg}")
        lines.append("")
        
        # Нижняя граница
        lines.append("🟫" * 30)
        lines.append("")
        
        # Нижняя панель с интерфейсом
        lines.append(cls._create_bottom_panel(player, enemy))
        
        return "\n".join(lines)
    
    @classmethod
    def _get_battle_log(cls, battle_log, max_messages=3):
        """Получает последние сообщения из лога боя"""
        if not battle_log:
            return ["⚔️ Бой начался!"]
        
        messages = []
        for entry in list(battle_log)[-max_messages:]:
            if entry.get("result"):
                # Берем последнее сообщение из результата
                last_msg = entry["result"][-1] if entry["result"] else "⚔️"
                messages.append(last_msg)
        
        # Дополняем до 3 сообщений, если нужно
        while len(messages) < max_messages:
            messages.insert(0, "⚔️")
        
        return messages
    
    @classmethod
    def _create_bottom_panel(cls, player, enemy):
        """Создает нижнюю панель с интерфейсом"""
        
        # Левая панель - характеристики игрока
        player_hp_bar = cls._create_hp_bar(player.hp, player.max_hp, 15)
        player_mp = player.mana if hasattr(player, 'mana') else 100
        player_max_mp = player.max_mana if hasattr(player, 'max_mana') else 100
        
        left_panel = [
            f"{cls.VERTICAL}  ❤️ {player_hp_bar} {player.hp}/{player.max_hp}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  💙 {cls._create_bar(player_mp, player_max_mp, 15)} {player_mp}/{player_max_mp}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  ⚔️ Урон: {player.get_total_damage()}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  🛡️ Защита: {player.defense}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  🔥 Крит: {player.crit_chance}%  {cls.VERTICAL}"
        ]
        
        # Центральная панель - фласки
        flask_panel = []
        for i, flask in enumerate(player.flasks[:3]):  # Максимум 3 фласки
            flask_type = cls._get_flask_type(flask)
            flask_bar = cls._create_bar(flask.current_uses, flask.flask_data["uses"], 5)
            marker = "👉" if i == player.active_flask else "  "
            flask_panel.append(
                f"{cls.VERTICAL}  {marker}{flask_type}{flask_bar}  {cls.VERTICAL}"
            )
        
        # Дополняем пустыми слотами
        while len(flask_panel) < 3:
            flask_panel.append(f"{cls.VERTICAL}     ⚪️ Пусто     {cls.VERTICAL}")
        
        # Правая панель - кнопки действий
        right_panel = cls._create_action_buttons()
        
        # Собираем все вместе
        separator = f"{cls.CROSS}{cls.HORIZONTAL * 20}{cls.CROSS}{cls.HORIZONTAL * 20}{cls.CROSS}{cls.HORIZONTAL * 20}{cls.CROSS}"
        
        top_line = f"{cls.TOP_LEFT}{cls.HORIZONTAL * 20}{cls.TOP_MID}{cls.HORIZONTAL * 20}{cls.TOP_MID}{cls.HORIZONTAL * 20}{cls.TOP_RIGHT}"
        bottom_line = f"{cls.BOTTOM_LEFT}{cls.HORIZONTAL * 20}{cls.BOTTOM_MID}{cls.HORIZONTAL * 20}{cls.BOTTOM_MID}{cls.HORIZONTAL * 20}{cls.BOTTOM_RIGHT}"
        
        lines = [top_line]
        
        # Добавляем все панели
        for i in range(max(len(left_panel), len(flask_panel), len(right_panel))):
            left = left_panel[i] if i < len(left_panel) else f"{cls.VERTICAL}{' ' * 22}{cls.VERTICAL}"
            center = flask_panel[i] if i < len(flask_panel) else f"{cls.VERTICAL}{' ' * 22}{cls.VERTICAL}"
            right = right_panel[i] if i < len(right_panel) else f"{cls.VERTICAL}{' ' * 22}{cls.VERTICAL}"
            
            lines.append(f"{left}{center}{right}")
            if i < max(len(left_panel), len(flask_panel), len(right_panel)) - 1:
                lines.append(separator)
        
        lines.append(bottom_line)
        
        return "\n".join(lines)
    
    @classmethod
    def _create_hp_bar(cls, current, maximum, length):
        """Создает полоску здоровья"""
        filled = int((current / maximum) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    @classmethod
    def _create_bar(cls, current, maximum, length):
        """Создает полоску для любых показателей"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)
    
    @classmethod
    def _get_flask_type(cls, flask):
        """Определяет тип фласки по эмодзи"""
        if "💊" in flask.emoji or "🧪" in flask.emoji:
            return "🟢💊🧪"  # Фласка здоровья
        elif "✨" in flask.emoji:
            return "⚪️✨🧪"  # Фласка баффа
        elif "🛡️" in flask.emoji:
            return "🔵🛡️🧪"  # Фласка защиты
        else:
            return "🟢💊🧪"
    
    @classmethod
    def _create_action_buttons(cls):
        """Создает панель с кнопками действий"""
        return [
            f"{cls.VERTICAL}     💪 Тяжелая     {cls.VERTICAL}",
            f"{cls.VERTICAL}     ⚡️ Быстрая     {cls.VERTICAL}",
            f"{cls.VERTICAL}     💨 Уклон       {cls.VERTICAL}",
            f"{cls.VERTICAL}     👤 Персонаж    {cls.VERTICAL}",
            f"{cls.VERTICAL}     🎒 Инвентарь    {cls.VERTICAL}"
        ]


# ============= ОСНОВНОЙ ХЕНДЛЕР БОЯ =============

class BattleHandler:
    """Хендлер для управления боем"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self.loot_system = LootSystem()
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "start_battle")
        async def start_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.start_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_attack_heavy")
        async def battle_heavy(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.HEAVY_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_attack_fast")
        async def battle_fast(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.FAST_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_dodge")
        async def battle_dodge(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.DODGE)
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_flask_"))
        async def battle_flask(callback: types.CallbackQuery, state: FSMContext):
            flask_index = int(callback.data.split('_')[2])
            await self.use_flask(callback, state, flask_index)
        
        @self.dp.callback_query(lambda c: c.data == "battle_continue")
        async def battle_continue(callback: types.CallbackQuery, state: FSMContext):
            await self.continue_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_log")
        async def battle_log(callback: types.CallbackQuery, state: FSMContext):
            await self.show_battle_log(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_player_stats")
        async def show_player_stats(callback: types.CallbackQuery, state: FSMContext):
            await self.show_player_stats(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_inventory_battle")
        async def show_inventory_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.handlers.inventory.show_inventory(callback, state)
    
    async def start_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Начинает бой"""
        data = await state.get_data()
        player = data['player']
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
        from systems.area_level import Area
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
        
        # Сохраняем состояние боя
        await state.update_data(
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=1,
            battle_log=deque(maxlen=10)  # Храним последние 10 записей
        )
        
        await self.show_battle(callback.message, state)
        await callback.answer()
    
    async def show_battle(self, message: types.Message, state: FSMContext):
        """Показывает экран боя"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not combat:
            combat = CombatSystem(player, enemy)
            await state.update_data(combat_system=combat)
        
        # Создаем новый интерфейс
        ui = BattleUI.create_battle_screen(player, enemy, combat, battle_log, turn)
        
        # Создаем клавиатуру
        keyboard = self._create_battle_keyboard(player)
        
        try:
            await message.edit_text(ui, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            # Если ошибка форматирования, пробуем без Markdown
            try:
                await message.edit_text(ui.replace("*", ""), reply_markup=keyboard)
            except:
                await message.answer(ui, reply_markup=keyboard)
    
    def _create_battle_keyboard(self, player):
        """Создает клавиатуру для боя"""
        buttons = []
        
        # Кнопки действий
        action_row = [
            InlineKeyboardButton(text="💪 Тяжелая", callback_data="battle_attack_heavy"),
            InlineKeyboardButton(text="⚡️ Быстрая", callback_data="battle_attack_fast"),
            InlineKeyboardButton(text="💨 Уклон", callback_data="battle_dodge")
        ]
        buttons.append(action_row)
        
        # Кнопки фласок
        flask_row = []
        for i, flask in enumerate(player.flasks[:3]):
            flask_type = "🟢💊" if i == 0 else "⚪️✨" if i == 1 else "🔵🛡️"
            flask_row.append(InlineKeyboardButton(
                text=f"{flask_type} [{flask.current_uses}/{flask.flask_data['uses']}]",
                callback_data=f"battle_flask_{i}"
            ))
        buttons.append(flask_row)
        
        # Кнопки интерфейса
        nav_row = [
            InlineKeyboardButton(text="👤", callback_data="show_player_stats"),
            InlineKeyboardButton(text="🎒", callback_data="show_inventory_battle")
        ]
        buttons.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def use_flask(self, callback: types.CallbackQuery, state: FSMContext, flask_index: int):
        """Использование фласки"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if flask_index >= len(player.flasks):
            await callback.answer("Фласка не найдена")
            return
        
        flask = player.flasks[flask_index]
        heal = flask.use()
        
        result_msg = ""
        if heal > 0:
            player.heal(heal)
            result_msg = f"🧪 Использована {flask.name}: +{heal} HP"
            
            # Если фласка опустела, переключаем активную
            if flask.current_uses == 0 and player._switch_to_next_flask():
                result_msg += f"\n🔄 Переключено на {player.flasks[player.active_flask].name}"
        else:
            result_msg = "❌ Фласка пуста!"
        
        # Добавляем в лог
        battle_log.append({"turn": turn, "result": [result_msg]})
        
        # Ход врага
        enemy_action = combat._choose_enemy_action()
        if enemy_action in [CombatAction.ATTACK, CombatAction.HEAVY_ATTACK]:
            # Враг атакует
            damage = enemy.attack()
            if enemy_action == CombatAction.HEAVY_ATTACK:
                damage = int(damage * 1.5)
                result_msg += f"\n💥 {enemy.name} использует тяжелую атаку!"
            
            actual_damage = player.take_damage(damage)
            result_msg += f"\n💥 {enemy.name} атакует: {actual_damage} урона"
            
            battle_log.append({"turn": turn, "result": [f"{enemy.name} атакует: {actual_damage} урона"]})
        
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
        await callback.answer(result_msg.split('\n')[0])
    
    async def process_action(self, callback: types.CallbackQuery, state: FSMContext, action: CombatAction):
        """Обрабатывает действие игрока"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not combat:
            await callback.answer("Ошибка боевой системы")
            return
        
        # Проверяем ману
        mana_cost = 10  # Базовая стоимость
        if hasattr(player, 'mana') and player.mana < mana_cost:
            await callback.answer("❌ Недостаточно маны!")
            return
        
        # Тратим ману
        if hasattr(player, 'mana'):
            player.mana -= mana_cost
        
        # Обрабатываем действие
        result = combat.process_turn(action)
        
        # Добавляем результат в лог
        battle_log.append({
            "turn": turn,
            "action": action.value,
            "result": result.messages.copy()
        })
        
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
        
        # Обновляем экран боя
        await self.show_battle(callback.message, state)
        await callback.answer()
    
    async def continue_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Продолжает бой"""
        await self.show_battle(callback.message, state)
        await callback.answer()
    
    async def show_battle_log(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает полный лог боя"""
        data = await state.get_data()
        battle_log = data.get('battle_log', [])
        
        if not battle_log:
            await callback.answer("Лог боя пуст")
            return
        
        text = "📋 **ПОЛНЫЙ ЛОГ БОЯ**\n\n"
        
        for entry in battle_log:
            text += f"**Ход {entry['turn']}:**\n"
            for msg in entry['result']:
                text += f"  {msg}\n"
            text += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад в бой", callback_data="battle_continue")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_player_stats(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает статистику игрока в бою"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        
        text = (
            f"👤 **{player.name}** | Ур. {player.level}\n\n"
            f"❤️ HP: {player.hp}/{player.max_hp}\n"
            f"💙 Мана: {player.mana if hasattr(player, 'mana') else 100}/100\n"
            f"⚔️ Урон: {player.get_total_damage()}\n"
            f"🛡️ Защита: {player.defense}\n"
            f"🎯 Точность: {player.accuracy}%\n"
            f"🔥 Крит: {player.crit_chance}% x{player.crit_multiplier}%\n\n"
            f"💪 Сила: {player.strength}\n"
            f"🏹 Ловкость: {player.dexterity}\n"
            f"📚 Интеллект: {player.intelligence}\n\n"
            f"💰 Золото: {player.gold}\n"
            f"✨ Опыт: {player.exp}/{player.level * 100}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад в бой", callback_data="battle_continue")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    # ... остальные методы (handle_victory, handle_defeat, handle_flee) остаются без изменений ...
    
    async def handle_victory(self, message: types.Message, state: FSMContext):
        """Обрабатывает победу"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        events = data.get('dungeon_events', [])
        current_index = player.position_in_location
        
        # Добавляем опыт
        exp_gained = enemy.get_exp_reward()
        levels_gained = player.add_exp(exp_gained)
        
        # Добавляем золото
        gold_gained = enemy.get_gold_reward()
        player.add_gold(gold_gained)
        
        # Восстанавливаем заряды фласок
        charges_restored = player.add_flask_charge()
        
        # Добавляем убийство в статистику
        player.add_kill(enemy.name)
        
        # Генерируем лут
        from systems.area_level import Area
        area = Area(player.current_location)
        area_level = area.current_level
        
        loot = self.loot_system.generate_loot(
            enemy.rarity, 
            area_level, 
            enemy.area_level,
            player.current_location
        )
        
        # Добавляем лут в инвентарь
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
        
        # Проверяем прогресс квестов
        if 'quest_manager' in data:
            await self.handlers.quest.check_quest_progress(
                state, "kill_monsters", enemy.name, 1, player.current_location
            )
            if enemy.rarity == "boss":
                await self.handlers.quest.check_quest_progress(
                    state, "kill_boss", enemy.name, 1, player.current_location
                )
        
        # Формируем текст победы
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
        
        text += f"\n**Что дальше?**"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Идти дальше", callback_data="next_step")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")],
            [InlineKeyboardButton(text="📊 Статы", callback_data="show_progression")]
        ])
        
        # Сохраняем обновленного игрока
        await state.update_data(player=player)
        
        # Удаляем сообщение с боем
        try:
            await message.delete()
        except:
            pass
        
        # Отправляем сообщение о победе
        await message.answer(text, reply_markup=keyboard)
    
    async def handle_defeat(self, message: types.Message, state: FSMContext):
        """Обрабатывает поражение"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        
        # Увеличиваем счетчик смертей
        player.add_death()
        
        # Частичное восстановление в убежище
        player.hp = player.max_hp // 2
        
        # Частичное восстановление фласок
        for flask in player.flasks:
            flask.current_uses = max(1, flask.flask_data["uses"] // 2)
        
        # Восстанавливаем ману
        if hasattr(player, 'mana'):
            player.mana = player.max_mana
        
        # Телепорт в убежище
        player.current_location = 2
        player.position_in_location = 0
        
        text = (
            f"💀 **ПОРАЖЕНИЕ...**\n\n"
            f"Ты пал в бою с {enemy.emoji} {enemy.name}.\n\n"
            f"Ты очнулся в убежище, едва живой.\n"
            f"❤️ Здоровье восстановлено до {player.hp}/{player.max_hp}\n"
            f"🧪 Фласки частично восстановлены\n\n"
            f"**Что дальше?**"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")],
            [InlineKeyboardButton(text="📊 Статы", callback_data="show_progression")]
        ])
        
        # Сохраняем состояние
        await state.update_data(
            player=player,
            battle_enemy=None,
            combat_system=None,
            battle_log=deque(maxlen=10)
        )
        
        # Удаляем сообщение с боем
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, reply_markup=keyboard)
    
    async def handle_flee(self, message: types.Message, state: FSMContext):
        """Обрабатывает побег"""
        data = await state.get_data()
        player = data['player']
        
        text = (
            f"🏃 **ПОБЕГ**\n\n"
            f"Ты успешно сбежал от врага!\n\n"
            f"**Что дальше?**"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data="next_step")],
            [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")]
        ])
        
        # Очищаем состояние боя
        await state.update_data(
            battle_enemy=None,
            combat_system=None,
            battle_log=deque(maxlen=10)
        )
        
        # Удаляем сообщение с боем
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, reply_markup=keyboard)
