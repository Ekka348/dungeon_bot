from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.player import Player
from models.item import Item, ItemType, ItemRarity, MeleeWeapon, Flask
from utils.helpers import format_item_list, format_equipment_slots

# ============= ОСНОВНОЙ ХЕНДЛЕР ИНВЕНТАРЯ =============

class InventoryHandler:
    """Хендлер для управления инвентарем и экипировкой"""
    
    MAX_INVENTORY_SLOTS = 20  # Максимум 20 слотов в инвентаре
    
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
        
        @self.dp.callback_query(lambda c: c.data.startswith("drop_"))
        async def drop_item(callback: types.CallbackQuery, state: FSMContext):
            await self.drop_item(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "confirm_drop")
        async def confirm_drop(callback: types.CallbackQuery, state: FSMContext):
            await self.confirm_drop(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "cancel_drop")
        async def cancel_drop(callback: types.CallbackQuery, state: FSMContext):
            await self.cancel_drop(callback, state)
        
        @self.dp.callback_query(lambda c: c.data == "show_inventory_battle")
        async def show_inventory_battle(callback: types.CallbackQuery, state: FSMContext):
            await self.show_inventory(callback, state)
    
    async def show_inventory(self, callback: types.CallbackQuery, state: FSMContext):
        """Показывает инвентарь игрока с экипировкой в виде человечка"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        text = self._format_inventory_with_equipment(player)
        keyboard = self._get_inventory_keyboard(player)
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    def _format_inventory_with_equipment(self, player):
        """Форматирует инвентарь с экипировкой в виде человечка"""
        lines = ["🎒 **ИНВЕНТАРЬ**\n"]
        
        # Экипировка в виде человечка
        lines.append("**ЭКИПИРОВКА:**")
        
        # Получаем экипированные предметы
        weapon = player.equipped.get(ItemType.WEAPON)
        shield = None  # Щит пока не реализован, но оставляем место
        helmet = player.equipped.get(ItemType.HELMET)
        ring1 = player.equipped.get(ItemType.RING)
        armor = player.equipped.get(ItemType.ARMOR)
        ring2 = None
        gloves = player.equipped.get(ItemType.GLOVES)
        belt = player.equipped.get(ItemType.BELT)
        boots = player.equipped.get(ItemType.BOOTS)
        
        # Находим второе кольцо (если есть)
        rings = [item for item in player.inventory if item.item_type == ItemType.RING and item != ring1]
        if rings:
            ring2 = rings[0]
        
        # Форматируем текст для каждого слота
        weapon_text = "⚔️ Пусто" if not weapon else weapon.get_name_colored()
        shield_text = "🛡️ Пусто"  # Заглушка для щита
        helmet_text = "⛑️ Пусто" if not helmet else helmet.get_name_colored()
        ring1_text = "💍 Пусто" if not ring1 else ring1.get_name_colored()
        armor_text = "🛡️ Пусто" if not armor else armor.get_name_colored()
        ring2_text = "💍 Пусто" if not ring2 else ring2.get_name_colored()
        gloves_text = "🧤 Пусто" if not gloves else gloves.get_name_colored()
        belt_text = "🔗 Пусто" if not belt else belt.get_name_colored()
        boots_text = "👢 Пусто" if not boots else boots.get_name_colored()
        empty_text = "⬜"
        
        # Обрезаем длинные названия (максимум 12 символов)
        weapon_text = weapon_text[:12] + "..." if len(weapon_text) > 12 else weapon_text
        shield_text = shield_text[:12] + "..." if len(shield_text) > 12 else shield_text
        helmet_text = helmet_text[:12] + "..." if len(helmet_text) > 12 else helmet_text
        ring1_text = ring1_text[:10] + "..." if len(ring1_text) > 10 else ring1_text
        armor_text = armor_text[:12] + "..." if len(armor_text) > 12 else armor_text
        ring2_text = ring2_text[:10] + "..." if len(ring2_text) > 10 else ring2_text
        gloves_text = gloves_text[:10] + "..." if len(gloves_text) > 10 else gloves_text
        belt_text = belt_text[:10] + "..." if len(belt_text) > 10 else belt_text
        boots_text = boots_text[:10] + "..." if len(boots_text) > 10 else boots_text
        
        # Строим схему экипировки
        lines.append("")
        
        # Строка 1: Оружие, пустая кнопка, Щит
        lines.append(f"    {weapon_text}         {empty_text}         {shield_text}    ")
        lines.append("")
        
        # Строка 2: пустая кнопка, Шлем, пустая кнопка
        lines.append(f"    {empty_text}           {helmet_text}           {empty_text}    ")
        lines.append("")
        
        # Строка 3: Кольцо, Нагрудник, Кольцо
        lines.append(f"    {ring1_text}        {armor_text}        {ring2_text}    ")
        lines.append("")
        
        # Строка 4: Перчатки, Пояс, Сапоги
        lines.append(f"    {gloves_text}        {belt_text}        {boots_text}    ")
        lines.append("")
        
        # Строка 5: три пустых кнопки (для будущих слотов)
        lines.append(f"    {empty_text}           {empty_text}           {empty_text}    ")
        lines.append("")
        
        # Инвентарь с лутом (максимум 20 слотов)
        lines.append("**ЛУТ В ИНВЕНТАРЕ:**")
        
        if not player.inventory:
            lines.append("  Пусто")
        else:
            # Показываем предметы с индексами
            for i, item in enumerate(player.inventory[:self.MAX_INVENTORY_SLOTS], 1):
                if isinstance(item, Flask):
                    flask_type = "🟢💊" if "💊" in item.emoji else "🟢Ⓜ️" if "Ⓜ️" in item.emoji else "⚪️✨" if "✨" in item.emoji else "🔵🛡️"
                    lines.append(f"{i}. {flask_type} {item.get_name_colored()} [{item.current_uses}/{item.flask_data['uses']}]")
                else:
                    lines.append(f"{i}. {item.get_name_colored()}")
            
            # Показываем количество свободных слотов
            free_slots = self.MAX_INVENTORY_SLOTS - len(player.inventory)
            if free_slots > 0:
                lines.append(f"  ... еще {free_slots} слотов свободно")
        
        lines.append("")
        lines.append(f"💰 Золото: {player.gold}")
        
        return "\n".join(lines)
    
    def _get_inventory_keyboard(self, player):
        """Создает клавиатуру для инвентаря"""
        buttons = []
        
        # Кнопки для просмотра предметов (по 5 в ряд)
        if player.inventory:
            items_row = []
            for i in range(min(5, len(player.inventory))):
                items_row.append(InlineKeyboardButton(text=f"📦 {i+1}", callback_data=f"inspect_{i+1}"))
            buttons.append(items_row)
            
            # Вторая строка предметов, если есть
            if len(player.inventory) > 5:
                items_row2 = []
                for i in range(5, min(10, len(player.inventory))):
                    items_row2.append(InlineKeyboardButton(text=f"📦 {i+1}", callback_data=f"inspect_{i+1}"))
                buttons.append(items_row2)
            
            # Третья строка предметов, если есть
            if len(player.inventory) > 10:
                items_row3 = []
                for i in range(10, min(15, len(player.inventory))):
                    items_row3.append(InlineKeyboardButton(text=f"📦 {i+1}", callback_data=f"inspect_{i+1}"))
                buttons.append(items_row3)
            
            # Четвертая строка предметов, если есть
            if len(player.inventory) > 15:
                items_row4 = []
                for i in range(15, min(20, len(player.inventory))):
                    items_row4.append(InlineKeyboardButton(text=f"📦 {i+1}", callback_data=f"inspect_{i+1}"))
                buttons.append(items_row4)
        
        # Кнопки для снятия экипировки
        equip_row = []
        if player.equipped[ItemType.WEAPON]:
            equip_row.append(InlineKeyboardButton(text="⚔️ Снять оружие", callback_data="unequip_weapon"))
        if player.equipped[ItemType.HELMET]:
            equip_row.append(InlineKeyboardButton(text="⛑️ Снять шлем", callback_data="unequip_helmet"))
        if player.equipped[ItemType.ARMOR]:
            equip_row.append(InlineKeyboardButton(text="🛡️ Снять броню", callback_data="unequip_armor"))
        if equip_row:
            buttons.append(equip_row)
        
        equip_row2 = []
        if player.equipped[ItemType.GLOVES]:
            equip_row2.append(InlineKeyboardButton(text="🧤 Снять перчатки", callback_data="unequip_gloves"))
        if player.equipped[ItemType.BELT]:
            equip_row2.append(InlineKeyboardButton(text="🔗 Снять пояс", callback_data="unequip_belt"))
        if player.equipped[ItemType.BOOTS]:
            equip_row2.append(InlineKeyboardButton(text="👢 Снять сапоги", callback_data="unequip_boots"))
        if equip_row2:
            buttons.append(equip_row2)
        
        equip_row3 = []
        if player.equipped[ItemType.RING]:
            equip_row3.append(InlineKeyboardButton(text="💍 Снять кольцо", callback_data="unequip_ring"))
        if player.equipped[ItemType.AMULET]:
            equip_row3.append(InlineKeyboardButton(text="📿 Снять амулет", callback_data="unequip_amulet"))
        if equip_row3:
            buttons.append(equip_row3)
        
        # Кнопки управления
        control_row = []
        if len(player.inventory) > 1:
            control_row.append(InlineKeyboardButton(text="📦 Сортировать", callback_data="sort_inventory"))
        if player.flasks:
            control_row.append(InlineKeyboardButton(text="🧪 Сменить фласку", callback_data="switch_flask"))
        if control_row:
            buttons.append(control_row)
        
        # Кнопка удаления и возврата
        nav_row = [
            InlineKeyboardButton(text="🗑️ Удалить", callback_data="drop_0"),
            InlineKeyboardButton(text="◀ Назад", callback_data="battle_back")
        ]
        buttons.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
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
        """Показывает детальную экипировку"""
        data = await state.get_data()
        player = data.get('player')
        
        if not player:
            await callback.answer("Ошибка: игрок не найден")
            return
        
        text = self._format_equipment_details(player)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎒 Инвентарь", callback_data="show_inventory")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="battle_back")]
        ])
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    def _format_equipment_details(self, player):
        """Форматирует детальную информацию об экипировке"""
        lines = ["📊 **ДЕТАЛЬНАЯ ЭКИПИРОВКА**\n"]
        
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
                
                if isinstance(item, MeleeWeapon):
                    min_dmg, max_dmg = item.get_damage_range()
                    lines.append(f"   Урон: {min_dmg}-{max_dmg}")
                    lines.append(f"   Скорость: {item.attack_speed:.2f}")
                
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
        keyboard = self._get_item_action_keyboard(item, item_index + 1, player)
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    def _get_item_action_keyboard(self, item, item_index, player):
        """Создает клавиатуру для действий с предметом"""
        buttons = []
        
        if item.item_type != ItemType.FLASK:
            # Проверяем, можно ли экипировать
            can_equip = True
            if isinstance(item, MeleeWeapon) and hasattr(item, 'requirements'):
                if "str" in item.requirements and player.strength < item.requirements["str"]:
                    can_equip = False
                if "dex" in item.requirements and player.dexterity < item.requirements["dex"]:
                    can_equip = False
                if "int" in item.requirements and player.intelligence < item.requirements["int"]:
                    can_equip = False
            
            if can_equip and not self._is_equipped(player, item):
                buttons.append([InlineKeyboardButton(text="⚔️ Экипировать", callback_data=f"equip_{item_index}")])
        else:
            buttons.append([InlineKeyboardButton(text="🧪 Использовать", callback_data=f"use_flask_{item_index}")])
        
        buttons.append([InlineKeyboardButton(text="💰 Продать", callback_data=f"sell_{item_index}")])
        buttons.append([InlineKeyboardButton(text="🗑️ Выбросить", callback_data=f"drop_{item_index}")])
        buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="show_inventory")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
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
        
        # Возвращаемся к инвентарю
        await self.show_inventory(callback, state)
    
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
                flask_index = int(parts[2]) - 1
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
        
        if item_index >= len(player.inventory):
            await callback.answer("Предмет не найден")
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
