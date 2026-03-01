from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional

from models.player import Player
from models.item import Item, ItemType, MeleeWeapon, Flask
from models.enemy import Enemy
from data.act1 import Act1

# ============= ОСНОВНЫЕ КЛАВИАТУРЫ =============

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для стартового экрана"""
    buttons = [
        [InlineKeyboardButton(text="⚔️ Начать игру", callback_data="start_game")],
        [InlineKeyboardButton(text="📜 Помощь", callback_data="show_help")],
        [InlineKeyboardButton(text="ℹ️ Об игре", callback_data="show_about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для экрана помощи"""
    buttons = [
        [InlineKeyboardButton(text="🎮 К игре", callback_data="start_game")],
        [InlineKeyboardButton(text="ℹ️ Об игре", callback_data="show_about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ ПОДЗЕМЕЛЬЯ =============

def get_dungeon_keyboard(event: Dict, player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для подземелья в зависимости от события"""
    buttons = []
    
    # Кнопка для текущего события
    if event["type"] == "battle" and not event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="⚔️ Вступить в бой", callback_data="start_battle")])
    elif event["type"] == "boss" and not event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="👑 Сразиться с боссом", callback_data="start_battle")])
    elif event["type"] == "chest" and not event.get("completed", False):
        rarity_emoji = {
            "common": "🟢",
            "magic": "🟣",
            "rare": "🟡"
        }.get(event.get("rarity", "common"), "📦")
        buttons.append([InlineKeyboardButton(text=f"{rarity_emoji} Открыть сундук", callback_data="open_chest")])
    elif event["type"] == "trap" and not event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="⚠️ Пройти ловушку", callback_data="trigger_trap")])
    elif event["type"] == "rest" and not event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="🔥 Отдохнуть", callback_data="take_rest")])
    elif event["type"] == "transition" and not event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="🚪 Перейти", callback_data="go_to_next_location")])
    
    # Кнопка "Идти дальше" (если событие пройдено)
    if event.get("completed", False):
        buttons.append([InlineKeyboardButton(text="➡️ Идти дальше", callback_data="next_step")])
    
    # Навигационные кнопки
    nav_buttons = []
    
    if player.current_location != 2:  # Если не в убежище
        nav_buttons.append(InlineKeyboardButton(text="🏚️ Убежище", callback_data="enter_haven"))
    
    nav_buttons.append(InlineKeyboardButton(text="🎒 Инвентарь", callback_data="show_inventory"))
    nav_buttons.append(InlineKeyboardButton(text="📊 Экипировка", callback_data="show_equipment"))
    
    buttons.append(nav_buttons)
    
    # Дополнительные кнопки
    more_buttons = []
    more_buttons.append(InlineKeyboardButton(text="🗺️ Карта", callback_data="show_map"))
    more_buttons.append(InlineKeyboardButton(text="📋 Квесты", callback_data="show_quests"))
    
    if len(player.flasks) > 1:
        more_buttons.append(InlineKeyboardButton(text="🧪 Сменить фласку", callback_data="switch_flask"))
    
    buttons.append(more_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ БОЯ =============

def get_battle_action_keyboard(player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для выбора действия в бою"""
    buttons = [
        [
            InlineKeyboardButton(text="🔪 Атака", callback_data="battle_attack"),
            InlineKeyboardButton(text="💪 Тяжелая", callback_data="battle_heavy"),
            InlineKeyboardButton(text="⚡ Быстрая", callback_data="battle_fast")
        ],
        [
            InlineKeyboardButton(text="🛡️ Защита", callback_data="battle_defend"),
            InlineKeyboardButton(text="💨 Уклон", callback_data="battle_dodge"),
            InlineKeyboardButton(text="🧪 Фласка", callback_data="battle_flask")
        ],
        [
            InlineKeyboardButton(text="🏃 Побег", callback_data="battle_run")
        ]
    ]
    
    # Добавляем индикатор активной фласки
    if player.flasks:
        active_flask = player.flasks[player.active_flask]
        flask_status = f"{active_flask.get_status()}"
        buttons.append([InlineKeyboardButton(text=f"📊 {flask_status}", callback_data="battle_status")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_battle_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для показа результата хода"""
    buttons = [
        [InlineKeyboardButton(text="➡️ Продолжить", callback_data="battle_continue")],
        [InlineKeyboardButton(text="📋 Лог боя", callback_data="battle_log")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ ИНВЕНТАРЯ =============

def get_inventory_keyboard(player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для инвентаря"""
    buttons = []
    
    # Кнопки для просмотра предметов (максимум 5)
    if player.inventory:
        row = []
        for i in range(min(5, len(player.inventory))):
            row.append(InlineKeyboardButton(text=f"🔍 {i+1}", callback_data=f"inspect_{i+1}"))
        buttons.append(row)
    
    # Кнопки управления
    buttons.append([
        InlineKeyboardButton(text="📊 Экипировка", callback_data="show_equipment"),
        InlineKeyboardButton(text="📋 Квесты", callback_data="show_quests")
    ])
    
    buttons.append([
        InlineKeyboardButton(text="📦 Сортировать", callback_data="sort_inventory"),
        InlineKeyboardButton(text="🗑️ Удалить", callback_data="drop_item_0")
    ])
    
    buttons.append([
        InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_item_action_keyboard(item: Item, item_index: int, player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для действий с предметом"""
    buttons = []
    
    if item.item_type != ItemType.FLASK:
        # Проверяем, можно ли экипировать
        can_equip = True
        if isinstance(item, MeleeWeapon) and item.requirements:
            if "str" in item.requirements and player.strength < item.requirements["str"]:
                can_equip = False
            if "dex" in item.requirements and player.dexterity < item.requirements["dex"]:
                can_equip = False
            if "int" in item.requirements and player.intelligence < item.requirements["int"]:
                can_equip = False
        
        if can_equip:
            buttons.append([InlineKeyboardButton(text="⚔️ Экипировать", callback_data=f"equip_{item_index}")])
    else:
        buttons.append([InlineKeyboardButton(text="🧪 Использовать", callback_data=f"use_flask_{item_index}")])
    
    buttons.append([InlineKeyboardButton(text="💰 Продать", callback_data=f"sell_{item_index}")])
    buttons.append([InlineKeyboardButton(text="🗑️ Выбросить", callback_data=f"drop_{item_index}")])
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="show_inventory")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ ЭКИПИРОВКИ =============

def get_equipment_keyboard(player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для экипировки"""
    buttons = []
    
    # Кнопки для снятия предметов
    for slot_type, item in player.equipped.items():
        if item:
            slot_name = {
                ItemType.WEAPON: "⚔️ Оружие",
                ItemType.HELMET: "⛑️ Шлем",
                ItemType.ARMOR: "🛡️ Броня",
                ItemType.GLOVES: "🧤 Перчатки",
                ItemType.BOOTS: "👢 Сапоги",
                ItemType.BELT: "🔗 Пояс",
                ItemType.RING: "💍 Кольцо",
                ItemType.AMULET: "📿 Амулет"
            }.get(slot_type, "Предмет")
            
            buttons.append([InlineKeyboardButton(text=f"❌ Снять {slot_name}", callback_data=f"unequip_{slot_type.value}")])
    
    buttons.append([InlineKeyboardButton(text="🎒 Инвентарь", callback_data="show_inventory")])
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ УБЕЖИЩА =============

def get_haven_keyboard(player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для убежища"""
    buttons = [
        [
            InlineKeyboardButton(text="👴 Морли", callback_data="npc_morley"),
            InlineKeyboardButton(text="🛒 Грег", callback_data="npc_greg")
        ],
        [
            InlineKeyboardButton(text="⚒️ Брок", callback_data="npc_brock"),
            InlineKeyboardButton(text="🔮 Элли", callback_data="npc_ellie")
        ],
        [InlineKeyboardButton(text="🪣 Колодец", callback_data="use_well")],
        [InlineKeyboardButton(text="📋 Квесты", callback_data="show_quests")],
        [InlineKeyboardButton(text="➡️ Выйти в подземелье", callback_data="enter_dungeon")],
        [InlineKeyboardButton(text="📊 Статы", callback_data="show_progression")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_npc_dialogue_keyboard(npc: Dict, player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для диалога с NPC"""
    buttons = []
    
    if npc.get("is_merchant"):
        buttons.append([InlineKeyboardButton(text="🛒 Купить", callback_data="show_shop")])
    
    if npc.get("is_blacksmith"):
        buttons.append([InlineKeyboardButton(text="⚒️ Купить", callback_data="show_blacksmith")])
        buttons.append([InlineKeyboardButton(text="🔧 Починить", callback_data="repair_equipment")])
    
    if npc.get("has_quest"):
        # Проверяем активные квесты
        has_active_quest = False
        for quest_id in npc.get("quest_ids", []):
            if quest_id in player.quests and player.quests[quest_id]["status"] == "active":
                has_active_quest = True
                buttons.append([InlineKeyboardButton(text="📋 О задании", callback_data=f"quest_details_{quest_id}")])
        
        if not has_active_quest:
            buttons.append([InlineKeyboardButton(text="📜 Взять задание", callback_data="show_available_quests")])
    
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="show_haven")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_shop_keyboard(items: List[Dict], shop_type: str) -> InlineKeyboardMarkup:
    """Клавиатура для магазина"""
    buttons = []
    
    # Кнопки для покупки товаров
    for i in range(len(items)):
        buttons.append([InlineKeyboardButton(text=f"💰 Купить {i+1}", callback_data=f"buy_{shop_type}_{i+1}")])
    
    buttons.append([InlineKeyboardButton(text="💰 Продать", callback_data="sell_0")])
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data=f"npc_{shop_type}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ КВЕСТОВ =============

def get_quests_keyboard(active: List, available: List, completed: List) -> InlineKeyboardMarkup:
    """Клавиатура для журнала квестов"""
    buttons = []
    
    if active:
        buttons.append([InlineKeyboardButton(text="⚔️ Активные квесты", callback_data="show_active_quests")])
    
    if available:
        buttons.append([InlineKeyboardButton(text="📜 Доступные квесты", callback_data="show_available_quests")])
    
    if completed:
        buttons.append([InlineKeyboardButton(text="✅ Завершенные", callback_data="show_completed_quests")])
    
    buttons.append([InlineKeyboardButton(text="🔄 Обновить", callback_data="update_quests")])
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quest_details_keyboard(quest) -> InlineKeyboardMarkup:
    """Клавиатура для деталей квеста"""
    buttons = []
    
    if quest.status.value == "available":
        buttons.append([InlineKeyboardButton(text="📜 Принять квест", callback_data=f"accept_quest_{quest.id}")])
    elif quest.status.value == "active":
        if quest.check_completion():
            buttons.append([InlineKeyboardButton(text="✅ Сдать квест", callback_data=f"complete_quest_{quest.id}")])
        buttons.append([InlineKeyboardButton(text="❌ Отказаться", callback_data=f"abandon_quest_{quest.id}")])
    
    buttons.append([InlineKeyboardButton(text="◀ Назад", callback_data="show_quests")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= КЛАВИАТУРЫ ПРОГРЕССИИ =============

def get_progression_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для экрана прогрессии"""
    buttons = [
        [InlineKeyboardButton(text="🏆 Достижения", callback_data="show_achievements")],
        [InlineKeyboardButton(text="🌳 Мастерство", callback_data="show_mastery")],
        [InlineKeyboardButton(text="⭐ Репутация", callback_data="show_reputation")],
        [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_dungeon")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_keyboards():
    """Тест клавиатур"""
    print("=" * 50)
    print("ТЕСТ КЛАВИАТУР")
    print("=" * 50)
    
    from models.player import Player
    
    player = Player()
    
    print("\n🔹 Стартовая клавиатура:")
    keyboard = get_start_keyboard()
    for row in keyboard.inline_keyboard:
        print(f"  {[btn.text for btn in row]}")
    
    print("\n🔹 Клавиатура подземелья (битва):")
    event = {"type": "battle", "completed": False}
    keyboard = get_dungeon_keyboard(event, player)
    for row in keyboard.inline_keyboard:
        print(f"  {[btn.text for btn in row]}")
    
    print("\n🔹 Клавиатура боя:")
    keyboard = get_battle_action_keyboard(player)
    for row in keyboard.inline_keyboard:
        print(f"  {[btn.text for btn in row]}")
    
    print("\n🔹 Клавиатура убежища:")
    keyboard = get_haven_keyboard(player)
    for row in keyboard.inline_keyboard:
        print(f"  {[btn.text for btn in row]}")
    
    print("\n🔹 Клавиатура квестов:")
    keyboard = get_quests_keyboard([], [], [])
    for row in keyboard.inline_keyboard:
        print(f"  {[btn.text for btn in row]}")


if __name__ == "__main__":
    test_keyboards()
