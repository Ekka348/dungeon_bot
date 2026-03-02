import random
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.item import generate_melee_weapon, generate_flask
from systems.area_level import AreaRegistry
from utils.keyboards import get_haven_keyboard, get_npc_dialogue_keyboard, get_shop_keyboard
from utils.helpers import format_npc_dialogue, format_shop_items


# ============= ДАННЫЕ NPC =============

class NPCData:
    """Статические данные NPC"""
    
    HAVEN_NPCS = [
        {
            "id": "morley",
            "name": "Старик Морли",
            "title": "Выживший",
            "emoji": "👴",
            "dialogue": {
                "first": "О, еще один бедолага... Добро пожаловать в наш скорбный приют.",
                "idle": "Колодец восстанавливает силы, если что.",
                "quest": "В тюрьме остались выжившие. Если найдешь их, приведи сюда."
            },
            "has_quest": True,
            "quest_ids": ["side_quest1"]
        },
        {
            "id": "greg",
            "name": "Торговец Грег",
            "title": "Скупщик",
            "emoji": "🛒",
            "dialogue": {
                "first": "Товар есть? Деньги есть? У меня есть все, что нужно выжившему.",
                "idle": "Заходи, если что-то нужно."
            },
            "is_merchant": True
        },
        {
            "id": "brock",
            "name": "Кузнец Брок",
            "title": "Бывший оружейник",
            "emoji": "⚒️",
            "dialogue": {
                "first": "Ха! Живой! Я Брок, кую что могу из того хлама, что нахожу в туннелях.",
                "idle": "У меня есть пара неплохих клинков."
            },
            "is_blacksmith": True
        },
        {
            "id": "ellie",
            "name": "Безумная Элли",
            "title": "Провидица",
            "emoji": "🔮",
            "dialogue": {
                "first": "Я вижу... вижу твою судьбу! Ты пройдешь через тьму и выйдешь к свету!",
                "idle": "Глубины зовут... слышишь? Они шепчут..."
            },
            "has_quest": True,
            "quest_ids": ["quest1", "quest2", "quest3"]
        }
    ]
    
    MERCHANT_ITEMS = {
        "rusted_sword": {
            "name": "Ржавый меч",
            "type": "weapon",
            "base": "rusted_sword",
            "price": 50,
            "min_level": 1,
            "emoji": "⚔️"
        },
        "spiked_club": {
            "name": "Дубинка с шипами",
            "type": "weapon",
            "base": "spiked_club",
            "price": 60,
            "min_level": 1,
            "emoji": "🔨"
        }
    }
    
    @classmethod
    def get_npc(cls, npc_id):
        """Получает NPC по ID"""
        for npc in cls.HAVEN_NPCS:
            if npc["id"] == npc_id:
                return npc
        return None


# ============= ХЕНДЛЕР УБЕЖИЩА =============

class HavenHandler:
    """Хендлер для управления убежищем"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "enter_haven")
        async def enter_haven(callback: types.CallbackQuery, state: FSMContext):
            await self.enter_haven(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_haven")
        async def show_haven_callback(callback: types.CallbackQuery, state: FSMContext):
            await self.show_haven(callback.message, state)
            await callback.answer()
        
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
        
        haven = AreaRegistry.get_location(2)
        if not haven:
            await callback.answer("Ошибка: убежище не найдено")
            return
        
        player.current_location = haven["id"]
        player.position_in_location = 0
        
        await state.update_data(player=player, dungeon_events=[])
        
        await self.show_haven(callback.message, state)
        await callback.answer()
    
    async def show_haven(self, message: types.Message, state: FSMContext):
        """Показывает убежище"""
        data = await state.get_data()
        player = data['player']
        
        haven = AreaRegistry.get_location(2)
        
        # Получаем активные квесты из QuestManager
        active_quests = []
        if 'quest_manager' in data:
            active = data['quest_manager'].get_active_quests()
            active_quests = [q.name for q in active[:3]]
        
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
            for quest in active_quests:
                text += f"  • {quest}\n"
            text += "\n"
        
        text += (
            f"**Твое состояние:**\n"
            f"👤 {player.hp}/{player.max_hp} ❤️ | Ур. {player.level}\n"
            f"💰 {player.gold} золота\n"
            f"🧪 Фласок: {len(player.flasks)}/{player.max_flasks}"
        )
        
        keyboard = get_haven_keyboard(player)
        
        try:
            await message.edit_text(text, reply_markup=keyboard)
        except:
            await message.answer(text, reply_markup=keyboard)
    
    async def talk_to_npc(self, callback: types.CallbackQuery, state: FSMContext):
        """Разговор с NPC"""
        data = await state.get_data()
        player = data['player']
        
        npc_id = callback.data.split('_')[1]
        npc = NPCData.get_npc(npc_id)
        
        if not npc:
            await callback.answer("NPC не найден")
            return
        
        await state.update_data(current_npc=npc_id)
        
        # Определяем диалог
        if npc_id not in player.talked_to_npcs:
            dialogue = npc["dialogue"]["first"]
            player.talked_to_npcs.add(npc_id)
        else:
            dialogue = npc["dialogue"].get("idle", npc["dialogue"]["first"])
        
        text = format_npc_dialogue(npc, dialogue)
        keyboard = get_npc_dialogue_keyboard(npc, player)
        
        await state.update_data(player=player)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def use_well(self, callback: types.CallbackQuery, state: FSMContext):
        """Использование колодца"""
        data = await state.get_data()
        player = data['player']
        
        restored = 0
        for flask in player.flasks:
            if flask.current_uses < flask.flask_data["uses"]:
                flask.current_uses = flask.flask_data["uses"]
                restored += 1
        
        await state.update_data(player=player)
        
        if restored > 0:
            await callback.answer(f"🧪 Колодец восстановил {restored} фласок!")
        else:
            await callback.answer("🧪 Все фласки уже полны")
        
        await self.show_haven(callback.message, state)
    
    async def show_shop(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает магазин"""
        data = await state.get_data()
        player = data['player']
        
        if 'shop_items' not in data:
            shop_items = self._generate_shop_items(player)
            await state.update_data(shop_items=shop_items)
        else:
            shop_items = data['shop_items']
        
        text = (
            f"🛒 **ТОРГОВЕЦ ГРЕГ**\n\n"
            f"💰 Твои деньги: {player.gold} золота\n\n"
        )
        
        text += format_shop_items(shop_items, player)
        keyboard = get_shop_keyboard(shop_items, "greg")
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _generate_shop_items(self, player):
        """Генерирует товары"""
        items = []
        
        base_items = [
            {"id": "rusted_sword", "price": 50},
            {"id": "spiked_club", "price": 60},
        ]
        
        for item_data in base_items:
            item = generate_melee_weapon(1, "common")
            if item:
                items.append({
                    "item": item,
                    "price": item_data["price"],
                    "stock": random.randint(1, 3)
                })
        
        for _ in range(random.randint(1, 2)):
            flask = generate_flask()
            price = flask.flask_data["heal"] // 2
            items.append({
                "item": flask,
                "price": price,
                "stock": random.randint(1, 2)
            })
        
        return items
    
    async def show_blacksmith(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает кузницу"""
        data = await state.get_data()
        player = data['player']
        
        items = self._generate_blacksmith_items(player)
        
        text = (
            f"⚒️ **КУЗНЕЦ БРОК**\n\n"
            f"💰 Твои деньги: {player.gold} золота\n\n"
        )
        
        for i, item_data in enumerate(items, 1):
            item = item_data["item"]
            min_dmg, max_dmg = item.get_damage_range() if hasattr(item, 'get_damage_range') else (0, 0)
            text += f"{i}. {item.get_name_colored()}\n"
            text += f"   Урон: {min_dmg}-{max_dmg} | 💰 {item_data['price']}\n\n"
        
        keyboard = get_shop_keyboard(items, "brock")
        
        await state.update_data(blacksmith_items=items)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _generate_blacksmith_items(self, player):
        """Генерирует товары кузнеца"""
        items = []
        
        weapon_tiers = [
            {"id": "copper_sword", "price": 120},
            {"id": "stone_hammer", "price": 150},
        ]
        
        for weapon_data in weapon_tiers:
            item = generate_melee_weapon(2, "magic")
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
        
        items = data.get(f'{shop_type}_items', [])
        
        if item_index < 0 or item_index >= len(items):
            await callback.answer("Товар не найден")
            return
        
        item_data = items[item_index]
        
        if item_data["stock"] <= 0:
            await callback.answer("Товар закончился")
            return
        
        if player.gold < item_data["price"]:
            await callback.answer("❌ Недостаточно золота")
            return
        
        player.gold -= item_data["price"]
        item_data["stock"] -= 1
        
        player.inventory.append(item_data["item"])
        
        await state.update_data(player=player)
        await callback.answer(f"✅ Куплено: {item_data['item'].name}")
        
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
        
        # Проверка на экипированный предмет
        for slot, equipped in player.equipped.items():
            if equipped == item:
                await callback.answer("❌ Нельзя продать экипированный предмет")
                return
        
        price = max(1, item.item_level * 5)
        player.gold += price
        player.inventory.pop(item_index)
        
        await state.update_data(player=player)
        await callback.answer(f"💰 Продано за {price} золота")
        await self.show_haven(callback.message, state)
    
    async def leave_haven(self, callback: types.CallbackQuery, state: FSMContext):
        """Выход из убежища"""
        await self.handlers.dungeon.show_dungeon(callback.message, state)
        await callback.answer()


# ============= ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ =============

async def show_haven(message: types.Message, state: FSMContext):
    """Внешняя функция для показа убежища"""
    # Эта функция будет вызвана через контейнер handlers
    pass
