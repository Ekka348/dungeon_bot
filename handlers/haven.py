import asyncio
import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.item import Item, MeleeWeapon, Flask, generate_melee_weapon, generate_flask
from data.act1 import Act1
from systems.progression import ProgressionSystem
from systems.loot import LootSystem
from utils.keyboards import get_haven_keyboard, get_npc_dialogue_keyboard, get_shop_keyboard
from utils.helpers import format_npc_dialogue, format_shop_items

# ============= ОСНОВНОЙ ХЕНДЛЕР УБЕЖИЩА =============

class HavenHandler:
    """Хендлер для управления убежищем"""
    
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self.loot_system = LootSystem()
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "enter_haven")
        async def enter_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.enter_haven(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_haven")
        async def show_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.show_haven(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("npc_"))
        async def talk_to_npc(callback: types.CallbackQuery, state: FSMContext):
            await self.talk_to_npc(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "use_well")
        async def use_well(callback: types.CallbackQuery, state: FSMContext):
            await self.use_well(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("buy_"))
        async def buy_item(callback: types.CallbackQuery, state: FSMContext):
            await self.buy_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("sell_"))
        async def sell_item(callback: types.CallbackQuery, state: FSMContext):
            await self.sell_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_shop")
        async def show_shop(callback: types.CallbackQuery, state: FSMContext):
            await self.show_shop(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_blacksmith")
        async def show_blacksmith(callback: types.CallbackQuery, state: FSMContext):
            await self.show_blacksmith(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "repair_equipment")
        async def repair_equipment(callback: types.CallbackQuery, state: FSMContext):
            await self.repair_equipment(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "leave_haven")
        async def leave_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.leave_haven(callback, state)
    
    async def enter_haven(self, callback: types.CallbackQuery, state: FSMContext):
        """Вход в убежище"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Перемещаем игрока в убежище
        haven = Act1.get_location_by_id(2)  # Убежище всегда ID 2
        player.current_location = haven["id"]
        player.position_in_location = 0
        
        # Сбрасываем события подземелья
        await state.update_data(
            player=player,
            dungeon_events=[],
            current_npc=None,
            shop_items=None
        )
        
        await self.show_haven(callback.message, state)
        await callback.answer()
    
    async def show_haven(self, message: types.Message, state: FSMContext):
        """Показывает убежище"""
        data = await state.get_data()
        player = data['player']
        
        # Получаем информацию о локации
        haven = Act1.get_location_by_id(2)
        
        # Получаем активные квесты
        active_quests = []
        for quest_id, quest_data in player.quests.items():
            if quest_data["status"] == "active":
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    active_quests.append(quest_info["name"])
        
        # Формируем текст
        text = (
            f"🏚️ **{haven['name']}**\n\n"
            f"{haven['description']}\n\n"
            f"**Обитатели убежища:**\n"
            f"👴 Старик Морли - бывалый выживший\n"
            f"🛒 Торговец Грег - продает всякую всячину\n"
            f"⚒️ Кузнец Брок - может сковать оружие\n"
            f"🔮 Безумная Элли - местная провидица\n\n"
        )
        
        if active_quests:
            text += f"**Активные квесты:**\n"
            for quest in active_quests[:3]:
                text += f"  • {quest}\n"
            text += "\n"
        
        text += (
            f"**Твое состояние:**\n"
            f"👤 {player.hp}/{player.max_hp} ❤️ | Ур. {player.level}\n"
            f"💰 {player.gold} золота\n"
            f"🧪 Фласок: {len(player.flasks)}/{player.max_flasks}"
        )
        
        # Клавиатура
        keyboard = get_haven_keyboard(player)
        
        try:
            await message.edit_text(text, reply_markup=keyboard)
        except:
            await message.answer(text, reply_markup=keyboard)
    
    async def talk_to_npc(self, callback: types.CallbackQuery, state: FSMContext):
        """Разговор с NPC"""
        data = await state.get_data()
        player = data['player']
        
        # Получаем ID NPC
        npc_id = callback.data.split('_')[1]
        npc = Act1.get_npc_by_id(npc_id)
        
        if not npc:
            await callback.answer("NPC не найден")
            return
        
        # Сохраняем текущего NPC
        await state.update_data(current_npc=npc_id)
        
        # Получаем диалог
        dialogue = self._get_npc_dialogue(npc, player)
        
        # Формируем текст
        text = format_npc_dialogue(npc, dialogue)
        
        # Клавиатура
        keyboard = get_npc_dialogue_keyboard(npc, player)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _get_npc_dialogue(self, npc, player):
        """Получает диалог NPC в зависимости от состояния"""
        # Проверяем, первый ли это разговор
        if npc["id"] not in player.visited_locations:  # Используем visited_locations как флаг
            return npc["dialogue"]["first"]
        
        # Проверяем квесты
        if npc.get("has_quest"):
            # Проверяем активные квесты
            for quest_id in npc.get("quest_ids", []):
                if quest_id in player.quests:
                    quest_data = player.quests[quest_id]
                    if quest_data["status"] == "active":
                        # Проверяем, выполнен ли квест
                        quest_info = Act1.get_quest_by_id(quest_id)
                        if quest_info and self._is_quest_completed(player, quest_info):
                            return npc["dialogue"].get("quest_complete", "Ты выполнил задание?")
                        else:
                            return npc["dialogue"].get("quest_active", "Как продвигается задание?")
                    elif quest_data["status"] == "completed":
                        return npc["dialogue"].get("quest_done", "Спасибо за помощь!")
        
        # Обычный диалог
        return npc["dialogue"].get("idle", npc["dialogue"]["first"])
    
    def _is_quest_completed(self, player, quest_info):
        """Проверяет, выполнен ли квест"""
        # Здесь должна быть логика проверки выполнения квеста
        # Пока возвращаем False
        return False
    
    async def use_well(self, callback: types.CallbackQuery, state: FSMContext):
        """Использование колодца для восстановления фласок"""
        data = await state.get_data()
        player = data['player']
        
        # Восстанавливаем все фласки
        restored = 0
        for flask in player.flasks:
            if flask.current_uses < flask.flask_data["uses"]:
                flask.current_uses = flask.flask_data["uses"]
                restored += 1
        
        # Также восстанавливаем фласки в инвентаре
        for item in player.inventory:
            if isinstance(item, Flask) and item.current_uses < item.flask_data["uses"]:
                item.current_uses = item.flask_data["uses"]
                restored += 1
        
        await state.update_data(player=player)
        
        if restored > 0:
            await callback.answer(f"🧪 Колодец восстановил {restored} фласок!")
        else:
            await callback.answer("🧪 Все фласки уже полны")
        
        # Возвращаемся в убежище
        await self.show_haven(callback.message, state)
    
    async def show_shop(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает магазин Грега"""
        data = await state.get_data()
        player = data['player']
        
        # Генерируем товары, если их нет
        if 'shop_items' not in data:
            shop_items = self._generate_shop_items(player)
            await state.update_data(shop_items=shop_items)
        else:
            shop_items = data['shop_items']
        
        text = (
            f"🛒 **ТОРГОВЕЦ ГРЕГ**\n\n"
            f"\"Заходи, не стесняйся! Всё честно, всё по-честному...\"\n\n"
            f"💰 Твои деньги: {player.gold} золота\n\n"
        )
        
        # Добавляем товары
        text += format_shop_items(shop_items, player)
        
        keyboard = get_shop_keyboard(shop_items, "greg")
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _generate_shop_items(self, player):
        """Генерирует товары в магазине"""
        items = []
        
        # Базовые товары всегда есть
        base_items = [
            {"id": "rusted_sword", "name": "Ржавый меч", "price": 50, "type": "weapon"},
            {"id": "spiked_club", "name": "Шипастая дубинка", "price": 60, "type": "weapon"},
            {"id": "glass_dagger", "name": "Стеклянный кинжал", "price": 45, "type": "weapon"},
        ]
        
        for item_data in base_items:
            item = generate_melee_weapon(1, "common")
            if item:
                items.append({
                    "item": item,
                    "price": item_data["price"],
                    "stock": random.randint(1, 3)
                })
        
        # Добавляем случайные фласки
        for _ in range(random.randint(1, 3)):
            flask = generate_flask()
            price = flask.flask_data["heal"] // 2
            items.append({
                "item": flask,
                "price": price,
                "stock": random.randint(1, 2)
            })
        
        return items
    
    async def show_blacksmith(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает кузницу Брока"""
        data = await state.get_data()
        player = data['player']
        
        # Генерируем товары кузнеца
        blacksmith_items = self._generate_blacksmith_items(player)
        
        text = (
            f"⚒️ **КУЗНЕЦ БРОК**\n\n"
            f"\"Ха! Смотри что у меня есть! Сам ковал, сам проверял!\"\n\n"
            f"💰 Твои деньги: {player.gold} золота\n\n"
        )
        
        # Добавляем товары
        for i, item_data in enumerate(blacksmith_items, 1):
            item = item_data["item"]
            min_dmg, max_dmg = item.get_damage_range() if isinstance(item, MeleeWeapon) else (0, 0)
            text += f"{i}. {item.get_name_colored()}\n"
            text += f"   Урон: {min_dmg}-{max_dmg} | Скорость: {item.attack_speed:.2f}\n"
            text += f"   💰 {item_data['price']} золота | В наличии: {item_data['stock']}\n\n"
        
        keyboard = get_shop_keyboard(blacksmith_items, "brock")
        
        await state.update_data(blacksmith_items=blacksmith_items)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _generate_blacksmith_items(self, player):
        """Генерирует товары кузнеца"""
        items = []
        
        # Оружие лучшего качества
        weapon_tiers = [
            {"id": "copper_sword", "level": 2, "price": 120},
            {"id": "stone_hammer", "level": 2, "price": 150},
            {"id": "jade_axe", "level": 2, "price": 130},
        ]
        
        for weapon_data in weapon_tiers:
            item = generate_melee_weapon(weapon_data["level"], "magic")
            if item:
                items.append({
                    "item": item,
                    "price": weapon_data["price"],
                    "stock": random.randint(1, 2)
                })
        
        return items
    
    async def buy_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Покупка предмета"""
        data = await state.get_data()
        player = data['player']
        
        parts = callback.data.split('_')
        if len(parts) < 3:
            await callback.answer("Ошибка: неверный формат")
            return
        
        shop_type = parts[1]
        item_index = int(parts[2]) - 1
        
        # Получаем список товаров
        if shop_type == "greg":
            items = data.get('shop_items', [])
        elif shop_type == "brock":
            items = data.get('blacksmith_items', [])
        else:
            await callback.answer("Магазин не найден")
            return
        
        if item_index < 0 or item_index >= len(items):
            await callback.answer("Товар не найден")
            return
        
        item_data = items[item_index]
        
        # Проверяем наличие
        if item_data["stock"] <= 0:
            await callback.answer("Товар закончился")
            return
        
        # Проверяем деньги
        if player.gold < item_data["price"]:
            await callback.answer("❌ Недостаточно золота")
            return
        
        # Покупаем
        player.gold -= item_data["price"]
        item_data["stock"] -= 1
        
        # Копируем предмет и добавляем в инвентарь
        item = item_data["item"]
        player.inventory.append(item)
        
        await state.update_data(player=player)
        
        await callback.answer(f"✅ Куплено: {item.name}")
        
        # Возвращаемся в магазин
        if shop_type == "greg":
            await self.show_shop(callback, state)
        else:
            await self.show_blacksmith(callback, state)
    
    async def sell_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Продажа предмета"""
        data = await state.get_data()
        player = data['player']
        
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        item_index = int(parts[1]) - 1
        
        if item_index < 0 or item_index >= len(player.inventory):
            await callback.answer("Предмет не найден")
            return
        
        item = player.inventory[item_index]
        
        # Нельзя продавать экипированные предметы
        if self._is_equipped(player, item):
            await callback.answer("❌ Нельзя продать экипированный предмет")
            return
        
        # Рассчитываем цену (50% от стоимости)
        price = max(1, item.calculate_value() // 2)
        
        # Продаем
        player.gold += price
        player.inventory.pop(item_index)
        
        await state.update_data(player=player)
        await callback.answer(f"💰 Продано за {price} золота")
        
        # Возвращаемся в убежище
        await self.show_haven(callback.message, state)
    
    def _is_equipped(self, player, item):
        """Проверяет, экипирован ли предмет"""
        for slot, equipped_item in player.equipped.items():
            if equipped_item == item:
                return True
        return False
    
    async def repair_equipment(self, callback: types.CallbackQuery, state: FSMContext):
        """Ремонт экипировки (заглушка)"""
        await callback.answer("⚒️ Скоро появится!")
    
    async def leave_haven(self, callback: types.CallbackQuery, state: FSMContext):
        """Выход из убежища в подземелье"""
        data = await state.get_data()
        player = data['player']
        
        # Возвращаемся в последнюю исследованную локацию
        # или в первую, если нет сохраненной
        from handlers.dungeon import show_dungeon
        
        # Сбрасываем NPC
        await state.update_data(current_npc=None)
        
        await show_dungeon(callback.message, state)
        await callback.answer()


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

async def show_haven(callback_or_message, state: FSMContext):
    """Внешняя функция для показа убежища"""
    handler = HavenHandler(callback_or_message.bot, None)
    
    if isinstance(callback_or_message, types.CallbackQuery):
        await handler.show_haven(callback_or_message.message, state)
    else:
        await handler.show_haven(callback_or_message, state)


async def enter_haven(callback: types.CallbackQuery, state: FSMContext):
    """Внешняя функция для входа в убежище"""
    handler = HavenHandler(callback.bot, None)
    await handler.enter_haven(callback, state)


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_haven_formatting():
    """Тест форматирования убежища"""
    print("=" * 50)
    print("ТЕСТ ФОРМАТИРОВАНИЯ УБЕЖИЩА")
    print("=" * 50)
    
    from models.player import Player
    
    player = Player()
    
    # Добавляем тестовые квесты
    player.quests["quest1"]["status"] = "active"
    
    handler = HavenHandler(None, None)
    
    # Тест отображения убежища
    print("\n🔹 Убежище:")
    haven = Act1.get_location_by_id(2)
    text = (
        f"🏚️ **{haven['name']}**\n\n"
        f"{haven['description']}\n\n"
        f"**Обитатели убежища:**\n"
        f"👴 Старик Морли - бывалый выживший\n"
        f"🛒 Торговец Грег - продает всякую всячину\n"
        f"⚒️ Кузнец Брок - может сковать оружие\n"
        f"🔮 Безумная Элли - местная провидица\n\n"
        f"**Активные квесты:**\n"
        f"  • Потерянный амулет\n\n"
        f"**Твое состояние:**\n"
        f"👤 150/150 ❤️ | Ур. 1\n"
        f"💰 50 золота\n"
        f"🧪 Фласок: 1/3"
    )
    print(text)
    
    # Тест диалога
    print("\n🔹 Диалог с NPC:")
    npc = Act1.get_npc_by_id("morley")
    dialogue = npc["dialogue"]["first"]
    print(f"{npc['emoji']} **{npc['name']}** - {npc['title']}")
    print(f"\"{dialogue}\"")
    
    # Тест магазина
    print("\n🔹 Магазин:")
    shop_items = handler._generate_shop_items(player)
    for i, item_data in enumerate(shop_items, 1):
        item = item_data["item"]
        print(f"{i}. {item.get_name_colored()} - 💰 {item_data['price']} (x{item_data['stock']})")


if __name__ == "__main__":
    test_haven_formatting()
