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

# ============= ИНТЕРФЕЙС БОЯ С ГИПЕРССЫЛКАМИ =============

class BattleUI:
    """Класс для формирования интерфейса боя с гиперссылками"""
    
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
    def create_battle_screen(cls, player, enemy, combat, battle_log, turn, bot_username):
        """Создает полный экран боя с гиперссылками"""
        
        lines = []
        
        # Заголовок с раундом
        lines.append(f"⚔️ **РАУНД {turn}**")
        lines.append("")
        
        # Информация о враге
        enemy_hp_bar = cls._create_hp_bar(enemy.hp, enemy.max_hp, 15)
        enemy_rarity = enemy.get_rarity_color()
        enemy_name = f"{enemy_rarity} {enemy.emoji} **{enemy.name}**"
        lines.append(f"  {enemy_name}")
        lines.append(f"  ❤️ {enemy_hp_bar} {enemy.hp}/{enemy.max_hp}")
        lines.append("")
        
        # Верхняя граница лога
        lines.append("🟫" * 30)
        lines.append("")
        
        # Лог боя (последние 3 сообщения)
        log_messages = cls._get_battle_log(battle_log)
        for msg in log_messages:
            padding = " " * ((60 - len(cls._clean_text(msg))) // 2)
            lines.append(f"{padding}{msg}")
        lines.append("")
        
        # Нижняя граница лога
        lines.append("🟫" * 30)
        lines.append("")
        
        # Нижняя панель с тремя колонками
        lines.append(cls._create_bottom_panel(player, bot_username))
        
        return "\n".join(lines)
    
    @classmethod
    def _clean_text(cls, text):
        """Очищает текст от Markdown для подсчета длины"""
        import re
        return re.sub(r'[*_`\[\]]', '', text)
    
    @classmethod
    def _get_battle_log(cls, battle_log, max_messages=3):
        """Получает последние сообщения из лога боя"""
        if not battle_log:
            return ["⚔️ Бой начался!"]
        
        messages = []
        for entry in list(battle_log)[-max_messages:]:
            if entry.get("result"):
                last_msg = entry["result"][-1] if entry["result"] else "⚔️"
                messages.append(last_msg)
        
        while len(messages) < max_messages:
            messages.insert(0, "⚔️")
        
        return messages
    
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
    
    @classmethod
    def _create_bottom_panel(cls, player, bot_username):
        """Создает нижнюю панель с тремя колонками и гиперссылками"""
        
        # Левая колонка - характеристики игрока
        player_hp_bar = cls._create_hp_bar(player.hp, player.max_hp, 10)
        player_mana_bar = cls._create_bar(player.mana, player.max_mana, 10)
        
        left_lines = [
            f"{cls.VERTICAL}  ❤️ {player_hp_bar} {player.hp}/{player.max_hp}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  💙 {player_mana_bar} {player.mana}/{player.max_mana}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  ⚔️ Урон: {player.get_total_damage()}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  🛡️ Защита: {player.defense}  {cls.VERTICAL}",
            f"{cls.VERTICAL}  🔥 Крит: {player.crit_chance}%  {cls.VERTICAL}"
        ]
        
        # Центральная колонка - фласки (кликабельные)
        center_lines = []
        for i, flask in enumerate(player.flasks[:3]):
            flask_type = "🟢💊" if i == 0 else "⚪️✨" if i == 1 else "🔵🛡️"
            flask_bar = cls._create_bar(flask.current_uses, flask.flask_data["uses"], 5)
            marker = "👉" if i == player.active_flask else "  "
            
            # Кликабельная фласка
            flask_link = f"tg://resolve?domain={bot_username}&start=battle_flask_{i}"
            flask_text = f"{marker} [{flask_type}🧪]({flask_link}) [{flask_bar}]"
            center_lines.append(f"{cls.VERTICAL}  {flask_text}  {cls.VERTICAL}")
        
        # Дополняем пустыми слотами
        while len(center_lines) < 3:
            center_lines.append(f"{cls.VERTICAL}     ⚪️ Пусто     {cls.VERTICAL}")
        
        # Правая колонка - действия (кликабельные)
        right_lines = [
            f"{cls.VERTICAL}     [💪 Тяжелая](tg://resolve?domain={bot_username}&start=battle_heavy)     {cls.VERTICAL}",
            f"{cls.VERTICAL}     [⚡️ Быстрая](tg://resolve?domain={bot_username}&start=battle_fast)     {cls.VERTICAL}",
            f"{cls.VERTICAL}     [💨 Уклон](tg://resolve?domain={bot_username}&start=battle_dodge)     {cls.VERTICAL}",
            f"{cls.VERTICAL}     [👤 Персонаж](tg://resolve?domain={bot_username}&start=battle_stats)     {cls.VERTICAL}",
            f"{cls.VERTICAL}     [🎒 Инвентарь](tg://resolve?domain={bot_username}&start=battle_inventory)     {cls.VERTICAL}"
        ]
        
        # Собираем все вместе
        top_line = f"{cls.TOP_LEFT}{cls.HORIZONTAL * 22}{cls.TOP_MID}{cls.HORIZONTAL * 22}{cls.TOP_MID}{cls.HORIZONTAL * 22}{cls.TOP_RIGHT}"
        separator = f"{cls.CROSS}{cls.HORIZONTAL * 22}{cls.CROSS}{cls.HORIZONTAL * 22}{cls.CROSS}{cls.HORIZONTAL * 22}{cls.CROSS}"
        bottom_line = f"{cls.BOTTOM_LEFT}{cls.HORIZONTAL * 22}{cls.BOTTOM_MID}{cls.HORIZONTAL * 22}{cls.BOTTOM_MID}{cls.HORIZONTAL * 22}{cls.BOTTOM_RIGHT}"
        
        panel_lines = [top_line]
        
        for i in range(5):
            panel_lines.append(f"{left_lines[i]}{center_lines[i]}{right_lines[i]}")
            if i < 4:
                panel_lines.append(separator)
        
        panel_lines.append(bottom_line)
        
        return "\n".join(panel_lines)


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
        
        @self.dp.message(lambda message: message.text and message.text.startswith('/start battle_'))
        async def battle_command(message: types.Message, state: FSMContext):
            await self.process_battle_command(message, state)
        
        @self.dp.callback_query(lambda c: c.data == "start_battle")
        async def start_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.start_battle(callback, state)
    
    async def process_battle_command(self, message: types.Message, state: FSMContext):
        """Обрабатывает команды из гиперссылок"""
        command = message.text.replace('/start ', '').strip()
        
        if command.startswith('battle_heavy'):
            await self.process_action(message, state, CombatAction.HEAVY_ATTACK)
        elif command.startswith('battle_fast'):
            await self.process_action(message, state, CombatAction.FAST_ATTACK)
        elif command.startswith('battle_dodge'):
            await self.process_action(message, state, CombatAction.DODGE)
        elif command.startswith('battle_flask_'):
            try:
                flask_index = int(command.split('_')[2])
                await self.use_flask(message, state, flask_index)
            except:
                await message.answer("❌ Ошибка использования фласки")
        elif command.startswith('battle_stats'):
            await self.show_player_stats(message, state)
        elif command.startswith('battle_inventory'):
            await self.handlers.inventory.show_inventory(message, state)
    
    async def start_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Начинает бой"""
        # Получаем username бота
        if not self.bot_username:
            bot_info = await self.bot.me()
            self.bot_username = bot_info.username
        
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
            battle_log=deque(maxlen=10)
        )
        
        # Удаляем сообщение с кнопкой
        try:
            await callback.message.delete()
        except:
            pass
        
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
        
        # Создаем интерфейс с гиперссылками
        ui = BattleUI.create_battle_screen(
            player, enemy, combat, battle_log, turn, self.bot_username
        )
        
        try:
            await message.edit_text(ui, parse_mode="Markdown")
        except Exception as e:
            # Если ошибка форматирования, пробуем без Markdown
            try:
                await message.edit_text(ui.replace("*", "").replace("[", "").replace("]", ""))
            except:
                await message.answer(ui, parse_mode="Markdown")
    
    async def use_flask(self, message: types.Message, state: FSMContext, flask_index: int):
        """Использование фласки"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if flask_index >= len(player.flasks):
            await message.answer("❌ Фласка не найдена")
            return
        
        flask = player.flasks[flask_index]
        heal = flask.use()
        
        result_msg = ""
        if heal > 0:
            player.heal(heal)
            result_msg = f"🧪 Использована {flask.name}: +{heal} HP"
            
            # Если фласка опустела, переключаем активную
            if flask.current_uses == 0 and hasattr(player, '_switch_to_next_flask') and player._switch_to_next_flask():
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
            await self.handle_defeat(message, state)
            return
        
        # Восстанавливаем ману
        if hasattr(player, 'restore_mana'):
            player.restore_mana(3)
        
        await self.show_battle(message, state)
    
    async def process_action(self, message: types.Message, state: FSMContext, action: CombatAction):
        """Обрабатывает действие игрока"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        battle_log = data.get('battle_log', deque(maxlen=10))
        
        if not combat:
            await message.answer("❌ Ошибка боевой системы")
            return
        
        # Проверяем ману
        mana_cost = combat.MANA_COSTS.get(action, 5)
        if hasattr(player, 'mana') and player.mana < mana_cost:
            await message.answer(f"❌ Недостаточно маны! Нужно {mana_cost}")
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
            await self.handle_flee(message, state)
            return
        
        if combat.is_enemy_dead():
            await self.handle_victory(message, state)
            return
        
        if combat.is_player_dead():
            await self.handle_defeat(message, state)
            return
        
        # Восстанавливаем ману
        if hasattr(player, 'restore_mana'):
            player.restore_mana(3)
        
        # Обновляем экран боя
        await self.show_battle(message, state)
    
    async def show_player_stats(self, message: types.Message, state: FSMContext):
        """Показывает статистику игрока в бою"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        
        text = (
            f"👤 **{player.name}** | Ур. {player.level}\n\n"
            f"❤️ HP: {player.hp}/{player.max_hp}\n"
            f"💙 Мана: {player.mana}/{player.max_mana}\n"
            f"⚔️ Урон: {player.get_total_damage()}\n"
            f"🛡️ Защита: {player.defense}\n"
            f"🎯 Точность: {player.accuracy}%\n"
            f"🔥 Крит: {player.crit_chance}% x{player.crit_multiplier}%\n\n"
            f"💪 Сила: {player.strength}\n"
            f"🏹 Ловкость: {player.dexterity}\n"
            f"📚 Интеллект: {player.intelligence}\n\n"
            f"💰 Золото: {player.gold}\n"
            f"✨ Опыт: {player.exp}/{player.level * 100}\n\n"
            f"[◀ Назад в бой](tg://resolve?domain={self.bot_username}&start=battle_back)"
        )
        
        await message.edit_text(text, parse_mode="Markdown")
    
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
        
        text += f"\n**Что дальше?**\n\n"
        text += f"[➡️ Идти дальше](tg://resolve?domain={self.bot_username}&start=next_step)\n"
        text += f"[🏚️ В убежище](tg://resolve?domain={self.bot_username}&start=return_haven)"
        
        # Сохраняем обновленного игрока
        await state.update_data(player=player)
        
        # Удаляем сообщение с боем
        try:
            await message.delete()
        except:
            pass
        
        # Отправляем сообщение о победе
        await message.answer(text, parse_mode="Markdown")
    
    async def handle_defeat(self, message: types.Message, state: FSMContext):
        """Обрабатывает поражение"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        
        # Увеличиваем счетчик смертей
        player.add_death()
        
        # Частичное восстановление
        player.hp = player.max_hp // 2
        player.mana = player.max_mana // 2
        
        for flask in player.flasks:
            flask.current_uses = max(1, flask.flask_data["uses"] // 2)
        
        # Телепорт в убежище
        player.current_location = 2
        player.position_in_location = 0
        
        text = (
            f"💀 **ПОРАЖЕНИЕ...**\n\n"
            f"Ты пал в бою с {enemy.emoji} {enemy.name}.\n\n"
            f"Ты очнулся в убежище, едва живой.\n"
            f"❤️ Здоровье: {player.hp}/{player.max_hp}\n"
            f"💙 Мана: {player.mana}/{player.max_mana}\n\n"
            f"[🏚️ В убежище](tg://resolve?domain={self.bot_username}&start=return_haven)\n"
            f"[📊 Статы](tg://resolve?domain={self.bot_username}&start=show_stats)"
        )
        
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
        
        await message.answer(text, parse_mode="Markdown")
    
    async def handle_flee(self, message: types.Message, state: FSMContext):
        """Обрабатывает побег"""
        data = await state.get_data()
        player = data['player']
        
        text = (
            f"🏃 **ПОБЕГ**\n\n"
            f"Ты успешно сбежал от врага!\n\n"
            f"[➡️ Продолжить](tg://resolve?domain={self.bot_username}&start=next_step)\n"
            f"[🏚️ В убежище](tg://resolve?domain={self.bot_username}&start=return_haven)"
        )
        
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
        
        await message.answer(text, parse_mode="Markdown")
