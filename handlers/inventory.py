from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.item import Item, ItemType, ItemRarity, MeleeWeapon, Flask
from utils.keyboards import get_inventory_keyboard, get_item_action_keyboard
from utils.helpers import format_item_list, format_equipment_slots

# ============= ОСНОВНОЙ ХЕНДЛЕР ИНВЕНТАРЯ =============

class InventoryHandler:
    """Хендлер для управления инвентарем и экипировкой"""
    
    def __init__(self, bot, dp, handlers_container):
        self.bot = bot
        self.dp = dp
        self.handlers = handlers_container
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует обработчики"""
        
        @self.dp.callback_query(lambda c: c.data == "show_inventory")
        async def show_inventory(callback: types.CallbackQuery, state: FSMContext):
            await self.show_inventory(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_equipment")
        async def show_equipment(callback: types.CallbackQuery, state: FSMContext):
            await self.show_equipment(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("inspect_"))
        async def inspect_item(callback: types.CallbackQuery, state: FSMContext):
            await self.inspect_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("equip_"))
        async def equip_item(callback: types.CallbackQuery, state: FSMContext):
            await self.equip_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("unequip_"))
        async def unequip_item(callback: types.CallbackQuery, state: FSMContext):
            await self.unequip_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data.startswith("use_flask_"))
        async def use_flask(callback: types.CallbackQuery, state: FSMContext):
            await self.use_flask(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "switch_flask")
        async def switch_flask(callback: types.CallbackQuery, state: FSMContext):
            await self.switch_flask(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "sort_inventory")
        async def sort_inventory(callback: types.CallbackQuery, state: FSMContext):
            await self.sort_inventory(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "drop_item")
        async def drop_item(callback: types.CallbackQuery, state: FSMContext):
            await self.drop_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "confirm_drop")
        async def confirm_drop(callback: types.CallbackQuery, state: FSMContext):
            await self.confirm_drop(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "cancel_drop")
        async def cancel_drop(callback: types.CallbackQuery, state: FSMContext):
            await self.cancel_drop(callback, state)
    
    async def show_inventory(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает инвентарь игрока"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        text = self._format_inventory(player)
        keyboard = get_inventory_keyboard(player)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _format_inventory(self, player):
        """Форматирует инвентарь для отображения"""
        if not player.inventory and not player.flasks:
            return f"🎒 **Инвентарь пуст**\n\n💰 Золото: {player.gold}"
        
        lines = ["🎒 **ИНВЕНТАРЬ**\n"]
        
        # Группируем предметы по типу
        weapons = []
        armor = []
        other = []
        flasks = []
        
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
        
        # Нумерация
        index = 1
        
        # Оружие
        if weapons:
            lines.append("**⚔️ ОРУЖИЕ:**")
            for item in weapons:
                equipped_mark = " [Э]" if self._is_equipped(player, item) else ""
                req_status = self._check_requirements(player, item)
                lines.append(f"{index}. {item.get_name_colored()}{equipped_mark}{req_status}")
                index += 1
            lines.append("")
        
        # Броня
        if armor:
            lines.append("**🛡️ БРОНЯ:**")
            for item in armor:
                equipped_mark = " [Э]" if self._is_equipped(player, item) else ""
                req_status = self._check_requirements(player, item)
                lines.append(f"{index}. {item.get_name_colored()}{equipped_mark}{req_status}")
                index += 1
            lines.append("")
        
        # Аксессуары
        if other:
            lines.append("**💍 АКСЕССУАРЫ:**")
            for item in other:
                equipped_mark = " [Э]" if self._is_equipped(player, item) else ""
                req_status = self._check_requirements(player, item)
                lines.append(f"{index}. {item.get_name_colored()}{equipped_mark}{req_status}")
                index += 1
            lines.append("")
        
        # Фласки в инвентаре
        if flasks:
            lines.append("**🧪 ФЛАСКИ (В ИНВЕНТАРЕ):**")
            for item in flasks:
                lines.append(f"{index}. {item.get_name_colored()} [{item.current_uses}/{item.flask_data['uses']}]")
                index += 1
            lines.append("")
        
        # Экипированные фласки
        if player.flasks:
            lines.append("**🧪 ФЛАСКИ (ЭКИПИРОВАНЫ):**")
            for i, flask in enumerate(player.flasks):
                marker = "👉" if i == player.active_flask else "  "
                lines.append(f"{marker} {flask.get_name_colored()} [{flask.current_uses}/{flask.flask_data['uses']}]")
            lines.append("")
        
        lines.append(f"💰 Золото: {player.gold}")
        
        return "\n".join(lines)
    
    def _is_equipped(self, player, item):
        """Проверяет, экипирован ли предмет"""
        for slot, equipped_item in player.equipped.items():
            if equipped_item == item:
                return True
        return False
    
    def _check_requirements(self, player, item):
        """Проверяет требования предмета"""
        if isinstance(item, MeleeWeapon) and hasattr(item, 'requirements') and item.requirements:
            reqs = []
            if "str" in item.requirements and player.strength < item.requirements["str"]:
                reqs.append(f"💪 {item.requirements['str']}")
            if "dex" in item.requirements and player.dexterity < item.requirements["dex"]:
                reqs.append(f"🏹 {item.requirements['dex']}")
            if "int" in item.requirements and player.intelligence < item.requirements["int"]:
                reqs.append(f"📚 {item.requirements['int']}")
            
            if reqs:
                return f" ❌ Требуется: {' '.join(reqs)}"
        return ""
    
    async def show_equipment(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает экипировку игрока"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        text = self._format_equipment(player)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎒 Инвентарь", callback_data="show_inventory")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    def _format_equipment(self, player):
        """Форматирует экипировку для отображения"""
        lines = ["📊 **ЭКИПИРОВКА**\n"]
        
        # Слоты экипировки
        slot_names = {
            ItemType.WEAPON: "⚔️ Оружие",
            ItemType.HELMET: "⛑️ Шлем",
            ItemType.ARMOR: "🛡️ Броня",
            ItemType.GLOVES: "🧤 Перчатки",
            ItemType.BOOTS: "👢 Сапоги",
            ItemType.BELT: "🔗 Пояс",
            ItemType.RING: "💍 Кольцо",
            ItemType.AMULET: "📿 Амулет"
        }
        
        for slot_type, slot_name in slot_names.items():
            item = player.equipped.get(slot_type)
            if item:
                lines.append(f"**{slot_name}:**")
                lines.append(f"└ {item.get_name_colored()}")
                
                # Показываем базовые характеристики для оружия
                if isinstance(item, MeleeWeapon):
                    min_dmg, max_dmg = item.get_damage_range()
                    lines.append(f"   Урон: {min_dmg}-{max_dmg}")
                    lines.append(f"   Скорость: {item.attack_speed:.2f}")
                    lines.append(f"   Крит: {item.crit_chance + item.stats.get('crit_chance', 0)}%")
                
                # Показываем аффиксы
                if hasattr(item, 'affixes') and item.affixes:
                    for affix_type, affix_data in item.affixes[:2]:
                        value = item.stats.get(affix_data["stat"], 0)
                        stat_names = {
                            "damage": "⚔️ Урон",
                            "max_hp": "❤️ Здоровье",
                            "defense": "🛡️ Защита",
                            "attack_speed": "⚡ Скорость",
                            "accuracy": "🎯 Точность",
                            "crit_chance": "🔥 Шанс крита",
                            "crit_multiplier": "💥 Множитель",
                            "life_on_hit": "🩸 Вампиризм"
                        }
                        stat_name = stat_names.get(affix_data["stat"], affix_data["stat"])
                        lines.append(f"   • {affix_data['name']}: {stat_name} +{value}")
                lines.append("")
            else:
                lines.append(f"**{slot_name}:** Пусто\n")
        
        # Итоговые статы
        lines.append("📊 **ИТОГОВЫЕ СТАТЫ:**")
        lines.append(f"❤️ HP: {player.hp}/{player.max_hp}")
        lines.append(f"⚔️ Урон: {player.get_total_damage()}")
        lines.append(f"🛡️ Защита: {player.defense}")
        lines.append(f"🎯 Точность: {player.accuracy}%")
        lines.append(f"🔥 Крит: {player.crit_chance}% x{player.crit_multiplier}%")
        lines.append(f"💪 Сила: {player.strength}")
        lines.append(f"🏹 Ловкость: {player.dexterity}")
        lines.append(f"📚 Интеллект: {player.intelligence}")
        
        return "\n".join(lines)
    
    async def inspect_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Просмотр детальной информации о предмете"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Получаем индекс предмета
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        try:
            item_index = int(parts[1]) - 1
        except ValueError:
            await callback.answer("Ошибка: неверный индекс")
            return
        
        if item_index < 0 or item_index >= len(player.inventory):
            await callback.answer("Предмет не найден")
            return
        
        item = player.inventory[item_index]
        
        # Получаем детальную информацию
        text = item.get_detailed_info()
        
        # Проверяем требования
        if isinstance(item, MeleeWeapon) and hasattr(item, 'requirements') and item.requirements:
            req_text = "\n\n**Требования:** "
            req_parts = []
            if "str" in item.requirements:
                req_parts.append(f"💪 {item.requirements['str']}")
            if "dex" in item.requirements:
                req_parts.append(f"🏹 {item.requirements['dex']}")
            if "int" in item.requirements:
                req_parts.append(f"📚 {item.requirements['int']}")
            req_text += " | ".join(req_parts)
            
            # Проверка выполнения
            can_use = True
            if "str" in item.requirements and player.strength < item.requirements["str"]:
                can_use = False
            if "dex" in item.requirements and player.dexterity < item.requirements["dex"]:
                can_use = False
            if "int" in item.requirements and player.intelligence < item.requirements["int"]:
                can_use = False
            
            if not can_use:
                req_text += "\n❌ **Требования не выполнены!**"
            
            text += req_text
        
        # Клавиатура действий
        keyboard = get_item_action_keyboard(item, item_index + 1, player)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def equip_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Экипирует предмет"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Получаем индекс предмета
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        try:
            item_index = int(parts[1]) - 1
        except ValueError:
            await callback.answer("Ошибка: неверный индекс")
            return
        
        if item_index < 0 or item_index >= len(player.inventory):
            await callback.answer("Предмет не найден")
            return
        
        item = player.inventory[item_index]
        
        # Проверяем, можно ли экипировать
        if item.item_type == ItemType.FLASK:
            # Фласки экипируются отдельно
            await self._equip_flask(player, item, item_index)
            await state.update_data(player=player)
            await callback.answer(f"🧪 Фласка {item.name} экипирована")
        else:
            # Экипируем в соответствующий слот
            success, message = player.equip(item, item.item_type)
            if success:
                await state.update_data(player=player)
                await callback.answer(message)
            else:
                await callback.answer(f"❌ {message}")
                return
        
        # Возвращаемся к инвентарю
        await self.show_inventory(callback, state)
    
    async def _equip_flask(self, player, flask, inventory_index):
        """Экипирует фласку"""
        if len(player.flasks) < player.max_flasks:
            player.flasks.append(flask)
            player.inventory.pop(inventory_index)
        else:
            if player.flasks:
                active_flask = player.flasks[player.active_flask]
                player.flasks[player.active_flask] = flask
                player.inventory[inventory_index] = active_flask
    
    async def unequip_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Снимает предмет"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Получаем тип слота
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        slot_name = parts[1]
        
        # Преобразуем название слота в ItemType
        slot_map = {
            "weapon": ItemType.WEAPON,
            "helmet": ItemType.HELMET,
            "armor": ItemType.ARMOR,
            "gloves": ItemType.GLOVES,
            "boots": ItemType.BOOTS,
            "belt": ItemType.BELT,
            "ring": ItemType.RING,
            "amulet": ItemType.AMULET
        }
        
        slot_type = slot_map.get(slot_name)
        if not slot_type:
            await callback.answer("Неизвестный слот")
            return
        
        # Снимаем предмет
        success, message = player.unequip(slot_type)
        
        if success:
            await state.update_data(player=player)
            await callback.answer(message)
        else:
            await callback.answer(f"❌ {message}")
            return
        
        # Возвращаемся к экипировке
        await self.show_equipment(callback, state)
    
    async def use_flask(self, callback: types.CallbackQuery, state: FSMContext):
        """Использует фласку (вне боя)"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        if not player.flasks:
            await callback.answer("❌ Нет фласок!")
            return
        
        # Получаем индекс фласки
        parts = callback.data.split('_')
        if len(parts) >= 3:
            try:
                flask_index = int(parts[2])
            except ValueError:
                flask_index = player.active_flask
        else:
            flask_index = player.active_flask
        
        if flask_index >= len(player.flasks):
            await callback.answer("Фласка не найдена")
            return
        
        flask = player.flasks[flask_index]
        heal = flask.use()
        
        if heal > 0:
            player.hp = min(player.max_hp, player.hp + heal)
            await state.update_data(player=player)
            await callback.answer(f"🧪 Использована {flask.name}: +{heal} HP")
        else:
            await callback.answer("❌ Фласка пуста!")
    
    async def switch_flask(self, callback: types.CallbackQuery, state: FSMContext):
        """Переключает активную фласку"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        if len(player.flasks) <= 1:
            await callback.answer("❌ Только одна фласка")
            return
        
        success, message = player.switch_flask()
        await state.update_data(player=player)
        await callback.answer(message)
        
        # Обновляем отображение
        await self.show_inventory(callback, state)
    
    async def sort_inventory(self, callback: types.CallbackQuery, state: FSMContext):
        """Сортирует инвентарь"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        # Сортировка: сначала оружие, потом броня, потом остальное
        weapons = [i for i in player.inventory if i.item_type == ItemType.WEAPON]
        armor = [i for i in player.inventory if i.item_type in [ItemType.HELMET, ItemType.ARMOR, 
                                                                 ItemType.GLOVES, ItemType.BOOTS, ItemType.BELT]]
        accessories = [i for i in player.inventory if i.item_type in [ItemType.RING, ItemType.AMULET]]
        flasks = [i for i in player.inventory if i.item_type == ItemType.FLASK]
        
        # Сортируем по редкости внутри категорий
        rarity_order = {ItemRarity.UNIQUE: 0, ItemRarity.RARE: 1, 
                        ItemRarity.MAGIC: 2, ItemRarity.NORMAL: 3}
        
        weapons.sort(key=lambda x: rarity_order.get(x.rarity, 4))
        armor.sort(key=lambda x: rarity_order.get(x.rarity, 4))
        accessories.sort(key=lambda x: rarity_order.get(x.rarity, 4))
        
        player.inventory = weapons + armor + accessories + flasks
        
        await state.update_data(player=player)
        await callback.answer("✅ Инвентарь отсортирован")
        await self.show_inventory(callback, state)
    
    async def drop_item(self, callback: types.CallbackQuery, state: FSMContext):
        """Запрос на удаление предмета"""
        data = await state.get_data()
        
        # Получаем индекс предмета
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("Ошибка: неверный формат")
            return
        
        try:
            item_index = int(parts[1]) - 1
        except ValueError:
            await callback.answer("Ошибка: неверный индекс")
            return
        
        # Сохраняем индекс для подтверждения
        await state.update_data(drop_item_index=item_index)
        
        text = "❓ **Вы уверены?**\n\nПредмет будет безвозвратно потерян."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_drop")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_drop")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    async def confirm_drop(self, callback: types.CallbackQuery, state: FSMContext):
        """Подтверждение удаления предмета"""
        data = await state.get_data()
        player = data.get('player')
        item_index = data.get('drop_item_index')
        
        if not player or item_index is None or item_index >= len(player.inventory):
            await callback.answer("Ошибка: предмет не найден")
            return
        
        # Удаляем предмет
        item = player.inventory.pop(item_index)
        
        await state.update_data(player=player, drop_item_index=None)
        await callback.answer(f"🗑️ {item.name} удален")
        
        # Возвращаемся к инвентарю
        await self.show_inventory(callback, state)
    
    async def cancel_drop(self, callback: types.CallbackQuery, state: FSMContext):
        """Отмена удаления предмета"""
        await state.update_data(drop_item_index=None)
        await self.show_inventory(callback, state)
        await callback.answer()
