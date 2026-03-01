import asyncio
import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
import os

from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask
from data.act1 import Act1
from systems.combat import CombatSystem, CombatAction, ActionResult
from systems.area_level import AreaLevelSystem, DifficultyCalculator
from systems.loot import LootSystem
from systems.progression import ProgressionSystem
from utils.keyboards import get_battle_action_keyboard, get_battle_result_keyboard
from utils.helpers import format_battle_view, format_hp_bar

# ============= ОСНОВНОЙ ХЕНДЛЕР БОЯ =============

class BattleHandler:
    """Хендлер для управления боем"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self.loot_system = LootSystem()
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "start_battle")
        async def start_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.start_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("battle_action_"))
        async def battle_action(callback: types.CallbackQuery, state: FSMContext):
            await self.process_battle_action(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_attack")
        async def battle_attack(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_heavy")
        async def battle_heavy(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.HEAVY_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_fast")
        async def battle_fast(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.FAST_ATTACK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_defend")
        async def battle_defend(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.DEFEND)
        
        @self.dp.callback_query(lambda c: c.data == "battle_dodge")
        async def battle_dodge(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.DODGE)
        
        @self.dp.callback_query(lambda c: c.data == "battle_flask")
        async def battle_flask(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.USE_FLASK)
        
        @self.dp.callback_query(lambda c: c.data == "battle_run")
        async def battle_run(callback: types.CallbackQuery, state: FSMContext):
            await self.process_action(callback, state, CombatAction.RUN)
        
        @self.dp.callback_query(lambda c: c.data == "battle_continue")
        async def battle_continue(callback: types.CallbackQuery, state: FSMContext):
            await self.continue_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_retry")
        async def battle_retry(callback: types.CallbackQuery, state: FSMContext):
            await self.retry_battle(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "battle_log")
        async def battle_log(callback: types.CallbackQuery, state: FSMContext):
            await self.show_battle_log(callback, state)
    
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
        area_level = AreaLevelSystem.get_area_level(player.current_location)
        
        # Создаем врага
        enemy = Enemy.from_monster_data(
            monster_data, 
            area_level, 
            current_event.get("rarity", "common")
        )
        
        # Создаем боевую систему
        combat = CombatSystem(player, enemy)
        
        # Сохраняем состояние боя
        await state.update_data(
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=1,
            battle_log=[]
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
        
        if not combat:
            # Создаем новую боевую систему, если ее нет
            combat = CombatSystem(player, enemy)
            await state.update_data(combat_system=combat)
        
        # Получаем статус боя
        status = combat.get_battle_status()
        
        # Формируем текст
        text = (
            f"⚔️ **РАУНД {turn}**\n\n"
            f"{status['enemy_info']}\n\n"
            f"{status['player_hp']}\n"
            f"{status['energy']}\n"
        )
        
        if status['combo']:
            text += f"{status['combo']}\n"
        
        text += f"\n🧪 **Фласки:**\n{status['flasks']}\n\n"
        text += f"**Твой ход:**"
        
        # Получаем клавиатуру
        keyboard = get_battle_action_keyboard(player)
        
        # Проверяем наличие изображения
        if enemy.image_path and os.path.exists(enemy.image_path):
            photo = FSInputFile(enemy.image_path)
            
            # Проверяем тип сообщения
            if hasattr(message, 'photo') and message.photo:
                await message.edit_caption(caption=text, reply_markup=keyboard)
            else:
                await message.delete()
                await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)
        else:
            # Текстовая версия
            battle_view = format_battle_view(enemy.emoji)
            full_text = f"{battle_view}\n\n{text}"
            
            try:
                await message.edit_text(full_text, reply_markup=keyboard)
            except:
                await message.answer(full_text, reply_markup=keyboard)
    
    async def process_action(self, callback: types.CallbackQuery, state: FSMContext, action: CombatAction):
        """Обрабатывает действие игрока в бою"""
        data = await state.get_data()
        player = data['player']
        enemy = data['battle_enemy']
        combat = data.get('combat_system')
        turn = data.get('battle_turn', 1)
        
        if not combat:
            await callback.answer("Ошибка боевой системы")
            return
        
        # Обрабатываем действие
        result = combat.process_turn(action)
        
        # Обновляем данные
        await state.update_data(
            player=player,
            battle_enemy=enemy,
            combat_system=combat,
            battle_turn=turn + 1
        )
        
        # Добавляем результат в лог
        battle_log = data.get('battle_log', [])
        battle_log.append({
            "turn": turn,
            "action": action.value,
            "result": result.messages.copy()
        })
        await state.update_data(battle_log=battle_log)
        
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
        
        # Показываем результат хода
        await self.show_turn_result(callback.message, state, result)
        await callback.answer()
    
    async def show_turn_result(self, message: types.Message, state: FSMContext, result: ActionResult):
        """Показывает результат хода"""
        data = await state.get_data()
        enemy = data['battle_enemy']
        turn = data.get('battle_turn', 1) - 1  # Текущий ход
        
        # Формируем текст результата
        text = f"⚔️ **ХОД {turn}**\n\n"
        text += result.get_text()
        text += f"\n\n**Продолжить?**"
        
        keyboard = get_battle_result_keyboard()
        
        # Проверяем наличие изображения
        if enemy.image_path and os.path.exists(enemy.image_path):
            if hasattr(message, 'photo') and message.photo:
                await message.edit_caption(caption=text, reply_markup=keyboard)
            else:
                await message.delete()
                photo = FSInputFile(enemy.image_path)
                await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)
        else:
            await message.edit_text(text, reply_markup=keyboard)
    
    async def continue_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Продолжает бой после показа результата"""
        await self.show_battle(callback.message, state)
        await callback.answer()
    
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
        area_level = AreaLevelSystem.get_area_level(player.current_location)
        loot = self.loot_system.generate_loot(
            enemy.rarity, 
            area_level, 
            enemy.monster_level,
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
        
        # Краткая статистика боя
        if combat:
            text += f"\n{combat.get_summary()}\n"
        
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
        
        # Телепорт в убежище
        player.current_location = 2  # Убежище
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
            battle_log=[]
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
            battle_log=[]
        )
        
        # Удаляем сообщение с боем
        try:
            await message.delete()
        except:
            pass
        
        await message.answer(text, reply_markup=keyboard)
    
    async def retry_battle(self, callback: types.CallbackQuery, state: FSMContext):
        """Повторяет бой (после поражения)"""
        data = await state.get_data()
        
        # Восстанавливаем врага из сохраненных данных
        if 'last_enemy' in data:
            enemy_data = data['last_enemy']
            # Здесь нужно восстановить врага
            # Пока просто начинаем заново
        
        await self.start_battle(callback, state)
    
    async def show_battle_log(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает лог боя"""
        data = await state.get_data()
        battle_log = data.get('battle_log', [])
        
        if not battle_log:
            await callback.answer("Лог боя пуст")
            return
        
        text = "📋 **ЛОГ БОЯ**\n\n"
        
        for entry in battle_log[-5:]:  # Последние 5 ходов
            text += f"**Ход {entry['turn']}:**\n"
            for msg in entry['result'][:3]:  # Первые 3 сообщения
                text += f"  {msg}\n"
            text += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Назад", callback_data="battle_continue")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def process_battle_action(self, callback: types.CallbackQuery, state: FSMContext):
        """Обрабатывает действие из callback data"""
        action = callback.data.split('_')[2]
        
        action_map = {
            "attack": CombatAction.ATTACK,
            "heavy": CombatAction.HEAVY_ATTACK,
            "fast": CombatAction.FAST_ATTACK,
            "defend": CombatAction.DEFEND,
            "dodge": CombatAction.DODGE,
            "flask": CombatAction.USE_FLASK,
            "run": CombatAction.RUN
        }
        
        combat_action = action_map.get(action)
        if combat_action:
            await self.process_action(callback, state, combat_action)
        else:
            await callback.answer("Неизвестное действие")


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

async def start_battle(callback: types.CallbackQuery, state: FSMContext):
    """Внешняя функция для начала боя"""
    handler = BattleHandler(callback.bot, None)  # dp не нужен для одного вызова
    await handler.start_battle(callback, state)


async def process_battle_action(callback: types.CallbackQuery, state: FSMContext, action: str):
    """Внешняя функция для обработки действия"""
    handler = BattleHandler(callback.bot, None)
    
    action_map = {
        "attack": CombatAction.ATTACK,
        "heavy": CombatAction.HEAVY_ATTACK,
        "fast": CombatAction.FAST_ATTACK,
        "defend": CombatAction.DEFEND,
        "dodge": CombatAction.DODGE,
        "flask": CombatAction.USE_FLASK,
        "run": CombatAction.RUN
    }
    
    combat_action = action_map.get(action)
    if combat_action:
        await handler.process_action(callback, state, combat_action)
    else:
        await callback.answer("Неизвестное действие")


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

async def test_battle_flow():
    """Тест для проверки потока боя"""
    print("=" * 50)
    print("ТЕСТ ПОТОКА БОЯ")
    print("=" * 50)
    
    # Создаем тестового игрока
    player = Player()
    
    # Создаем тестового врага
    monster_data = {
        "name": "Тестовый монстр",
        "base_hp": 50,
        "damage": (5, 10),
        "accuracy": 70,
        "defense": 3,
        "base_exp": 25,
        "emoji": "👾",
        "description": "Монстр для тестов"
    }
    
    enemy = Enemy.from_monster_data(monster_data, 1, "common")
    
    print(f"\n🔹 Начало боя:")
    print(f"Игрок: {player.hp}/{player.max_hp} HP")
    print(f"Враг: {enemy.hp}/{enemy.max_hp} HP")
    
    # Создаем боевую систему
    combat = CombatSystem(player, enemy)
    
    # Симулируем несколько ходов
    actions = [CombatAction.ATTACK, CombatAction.HEAVY_ATTACK, 
               CombatAction.FAST_ATTACK, CombatAction.DEFEND]
    
    turn = 1
    while not combat.is_player_dead() and not combat.is_enemy_dead() and turn <= 10:
        print(f"\n🔸 ХОД {turn}")
        print("-" * 30)
        
        action = random.choice(actions)
        print(f"Действие: {action.value}")
        
        result = combat.process_turn(action)
        print(result.get_text())
        
        turn += 1
    
    if combat.is_enemy_dead():
        print(f"\n🎉 Победа за {turn-1} ходов!")
        print(f"Награда: {enemy.get_exp_reward()} опыта, {enemy.get_gold_reward()} золота")
    else:
        print(f"\n💀 Поражение...")


if __name__ == "__main__":
    asyncio.run(test_battle_flow())
