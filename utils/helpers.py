import random
import time
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from models.player import Player
from models.enemy import Enemy
from models.item import Item, ItemRarity, MeleeWeapon, Flask

# ============= ФОРМАТИРОВАНИЕ ТЕКСТА =============

def format_number(num: int) -> str:
    """Форматирует число с разделителями тысяч"""
    return f"{num:,}".replace(",", " ")


def format_percentage(value: float) -> str:
    """Форматирует процент"""
    return f"{value:.1f}%"


def format_time(seconds: int) -> str:
    """Форматирует время в секундах"""
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ч"
    else:
        days = seconds // 86400
        return f"{days} д"


def format_timestamp(timestamp: float) -> str:
    """Форматирует временную метку"""
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    
    if dt.date() == now.date():
        return f"сегодня в {dt.strftime('%H:%M')}"
    elif (now - dt).days == 1:
        return f"вчера в {dt.strftime('%H:%M')}"
    else:
        return dt.strftime('%d.%m.%Y %H:%M')


# ============= ФОРМАТИРОВАНИЕ ПОЛОСОК ПРОГРЕССА =============

def format_hp_bar(current: int, max_hp: int, length: int = 10) -> str:
    """Возвращает полоску здоровья"""
    if max_hp <= 0:
        return "💀"
    
    filled = int((current / max_hp) * length)
    filled = min(filled, length)
    bar = "█" * filled + "░" * (length - filled)
    
    # Цвет в зависимости от процента здоровья
    percent = (current / max_hp) * 100
    if percent > 66:
        color = "🟢"
    elif percent > 33:
        color = "🟡"
    else:
        color = "🔴"
    
    return f"{color} {bar} {current}/{max_hp}"


def format_exp_bar(current: int, needed: int, length: int = 10) -> str:
    """Возвращает полоску опыта"""
    if needed <= 0:
        return "✨ Макс. уровень"
    
    percent = min(100, int((current / needed) * 100))
    filled = int((current / needed) * length)
    filled = min(filled, length)
    bar = "█" * filled + "░" * (length - filled)
    
    return f"✨ {bar} {percent}%"


def format_energy_bar(current: int, max_energy: int, length: int = 5) -> str:
    """Возвращает полоску энергии"""
    filled = int((current / max_energy) * length)
    filled = min(filled, length)
    return "🔋" * filled + "⚪" * (length - filled)


def format_progress_bar(current: int, total: int, event_types: List[str] = None, length: int = 10) -> str:
    """Возвращает полоску прогресса локации"""
    if total <= 0:
        return ""
    
    # Если есть типы событий, показываем их иконками
    if event_types and len(event_types) >= length:
        icons = []
        for i, event_type in enumerate(event_types[:length]):
            if i < current:
                # Пройденные события
                icons.append("✅")
            elif i == current:
                # Текущее событие
                if event_type == "battle":
                    icons.append("⚔️")
                elif event_type == "chest":
                    icons.append("📦")
                elif event_type == "trap":
                    icons.append("⚠️")
                elif event_type == "rest":
                    icons.append("🔥")
                elif event_type == "transition":
                    icons.append("🚪")
                elif event_type == "boss":
                    icons.append("👑")
                else:
                    icons.append("⬜")
            else:
                # Будущие события
                icons.append("⬜")
        
        return " ".join(icons)
    else:
        # Обычная полоска
        filled = int((current / total) * length)
        filled = min(filled, length)
        bar = "█" * filled + "░" * (length - filled)
        return f"📊 {bar} {current}/{total}"


# ============= ФОРМАТИРОВАНИЕ ВИЗУАЛИЗАЦИЙ =============

def format_dungeon_view(player_emoji: str = "👨‍🦱", enemy_emoji: str = None) -> str:
    """Форматирует визуализацию подземелья"""
    if enemy_emoji:
        return (
            f"🟫🟫🟫🟫🟫🟫\n\n"
            f"    {player_emoji}            {enemy_emoji}\n\n"
            f"🟫🟫🟫🟫🟫🟫"
        )
    else:
        return (
            f"🟫🟫🟫🟫🟫🟫\n\n"
            f"    {player_emoji}\n\n"
            f"🟫🟫🟫🟫🟫🟫"
        )


def format_battle_view(enemy_emoji: str) -> str:
    """Форматирует визуализацию боя"""
    return (
        f"🟫🟫🟫🟫🟫🟫\n\n"
        f"    👨‍🦱            {enemy_emoji}\n\n"
        f"🟫🟫🟫🟫🟫🟫"
    )


# ============= ФОРМАТИРОВАНИЕ СПИСКОВ =============

def format_item_list(items: List[Item], start_index: int = 1) -> str:
    """Форматирует список предметов"""
    if not items:
        return "  Пусто"
    
    lines = []
    for i, item in enumerate(items, start_index):
        if isinstance(item, Flask):
            lines.append(f"{i}. {item.get_name_colored()} [{item.current_uses}/{item.flask_data['uses']}]")
        else:
            lines.append(f"{i}. {item.get_name_colored()}")
    
    return "\n".join(lines)


def format_equipment_slots(player: Player) -> str:
    """Форматирует слоты экипировки"""
    slot_names = {
        "weapon": "⚔️ Оружие",
        "helmet": "⛑️ Шлем",
        "armor": "🛡️ Броня",
        "gloves": "🧤 Перчатки",
        "boots": "👢 Сапоги",
        "belt": "🔗 Пояс",
        "ring": "💍 Кольцо",
        "amulet": "📿 Амулет"
    }
    
    lines = []
    for slot_key, slot_name in slot_names.items():
        item = player.equipped.get(slot_key)
        if item:
            lines.append(f"**{slot_name}:** {item.get_name_colored()}")
        else:
            lines.append(f"**{slot_name}:** Пусто")
    
    return "\n".join(lines)


def format_shop_items(items: List[Dict], player: Player) -> str:
    """Форматирует товары в магазине"""
    if not items:
        return "  Товаров нет"
    
    lines = []
    for i, item_data in enumerate(items, 1):
        item = item_data["item"]
        price = item_data["price"]
        stock = item_data.get("stock", 1)
        
        can_afford = "✅" if player.gold >= price else "❌"
        
        if isinstance(item, MeleeWeapon):
            min_dmg, max_dmg = item.get_damage_range()
            lines.append(f"{i}. {item.get_name_colored()} {can_afford}")
            lines.append(f"   Урон: {min_dmg}-{max_dmg} | 💰 {price}")
        elif isinstance(item, Flask):
            lines.append(f"{i}. {item.get_name_colored()} {can_afford}")
            lines.append(f"   Лечение: +{item.flask_data['heal']} HP | 💰 {price}")
        else:
            lines.append(f"{i}. {item.get_name_colored()} {can_afford}")
            lines.append(f"   💰 {price}")
        
        if stock > 1:
            lines[-1] += f" (x{stock})"
        lines.append("")
    
    return "\n".join(lines)


# ============= ФОРМАТИРОВАНИЕ КВЕСТОВ =============

def format_quest_progress(quest) -> str:
    """Форматирует прогресс квеста"""
    if not quest.objectives:
        return ""
    
    lines = []
    for obj in quest.objectives:
        if obj.required > 1:
            progress = f"{obj.progress}/{obj.required}"
            status = "✅" if obj.is_completed() else "⬜"
            lines.append(f"  {status} {obj.get_description_string()} ({progress})")
        else:
            status = "✅" if obj.is_completed() else "⬜"
            lines.append(f"  {status} {obj.get_description_string()}")
    
    return "\n".join(lines)


def format_quest_rewards(rewards) -> str:
    """Форматирует награды за квест"""
    rewards_list = []
    
    if rewards.exp > 0:
        rewards_list.append(f"✨ {rewards.exp} опыта")
    if rewards.gold > 0:
        rewards_list.append(f"💰 {rewards.gold} золота")
    if rewards.items:
        for item in rewards.items:
            rewards_list.append(f"📦 {item}")
    if rewards.item:
        rewards_list.append(f"🎁 Особый предмет")
    
    return ", ".join(rewards_list) if rewards_list else "Нет наград"


# ============= ФОРМАТИРОВАНИЕ NPC =============

def format_npc_dialogue(npc: Dict, dialogue: str) -> str:
    """Форматирует диалог с NPC"""
    return (
        f"{npc['emoji']} **{npc['name']}** - {npc['title']}\n\n"
        f"\"{dialogue}\""
    )


# ============= ФОРМАТИРОВАНИЕ СООБЩЕНИЙ =============

def format_welcome_message(user_name: str) -> str:
    """Форматирует приветственное сообщение"""
    return (
        f"⚔️ **Добро пожаловать в Dungeon Crawler, {user_name}!** ⚔️\n\n"
        f"Ты был сброшен в темницу за преступления, которых не совершал.\n"
        f"Холодный камень встречает твое падение. Вокруг лишь тьма\n"
        f"и звуки капающей воды. Нужно найти выход...\n\n"
        f"🕷️ **Что тебя ждет:**\n"
        f"• Исследуй 7 уникальных локаций\n"
        f"• Сражайся с монстрами подземелья\n"
        f"• Собирай лут с аффиксами\n"
        f"• Выполняй квесты и прокачивайся\n"
        f"• Сразись с боссом акта\n\n"
        f"Напиши /help для списка команд или нажми кнопку ниже!"
    )


def format_help_message() -> str:
    """Форматирует сообщение помощи"""
    return (
        "📜 **ПОМОЩЬ ПО ИГРЕ**\n\n"
        "**Основные команды:**\n"
        "/start - начать игру\n"
        "/help - показать эту справку\n"
        "/stats - показать статистику\n"
        "/info - информация о текущей локации\n"
        "/reset - сбросить прогресс\n\n"
        
        "**Боевая система:**\n"
        "🔪 Атака (1 эн.) - обычная атака\n"
        "💪 Тяжелая (2 эн.) - больше урона, шанс оглушить\n"
        "⚡ Быстрая (1 эн.) - выше точность, больше шанс крита\n"
        "🛡️ Защита (1 эн.) - снижение получаемого урона\n"
        "💨 Уклон (1 эн.) - шанс избежать урона\n"
        "🧪 Фласка - лечение\n"
        "🏃 Побег - попытка сбежать\n\n"
        
        "**Система лута:**\n"
        "⚪ Обычные предметы - без аффиксов\n"
        "🔵 Магические - 1 аффикс\n"
        "🟡 Редкие - 2-4 аффикса\n"
        "🔴 Уникальные - особые свойства\n\n"
        
        "**Советы:**\n"
        "• Возвращайся в убежище, чтобы восстановить фласки\n"
        "• Выполняй квесты для получения наград\n"
        "• Следи за уровнем локации - монстры могут быть сильнее\n"
        "• Собирай лут и экипируй лучшее\n\n"
        
        "Удачи в приключении, странник! 🍀"
    )


# ============= РАСЧЕТЫ =============

def calculate_damage(base_damage: int, crit_chance: float, crit_mult: float, 
                     defense: int = 0, is_crit: bool = False) -> Tuple[int, bool]:
    """Рассчитывает урон с учетом крита и защиты"""
    if is_crit or random.random() * 100 < crit_chance:
        damage = int(base_damage * (crit_mult / 100))
        return damage, True
    else:
        return base_damage, False


def calculate_defense_reduction(damage: int, defense: int) -> int:
    """Рассчитывает уменьшение урона от защиты"""
    reduction = defense // 3
    return max(1, damage - reduction)


def calculate_dodge_chance(dexterity: int, base_chance: float = 5) -> float:
    """Рассчитывает шанс уклонения"""
    return base_chance + (dexterity // 10)


def calculate_stun_chance(damage: int, target_max_hp: int, stun_mult: float = 1.0) -> float:
    """Рассчитывает шанс оглушения"""
    base_chance = (damage / target_max_hp) * 100
    return min(80, base_chance * stun_mult)


# ============= ГЕНЕРАЦИЯ =============

def generate_random_name(prefixes: List[str], suffixes: List[str]) -> str:
    """Генерирует случайное имя"""
    prefix = random.choice(prefixes) if prefixes else ""
    suffix = random.choice(suffixes) if suffixes else ""
    
    if prefix and suffix:
        return f"{prefix} {suffix}"
    elif prefix:
        return prefix
    elif suffix:
        return suffix
    else:
        return "Предмет"


def generate_random_color() -> str:
    """Генерирует случайный цвет для эмодзи"""
    colors = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪"]
    return random.choice(colors)


# ============= ВАЛИДАЦИЯ =============

def validate_index(index: int, max_value: int) -> bool:
    """Проверяет корректность индекса"""
    return 0 <= index < max_value


def validate_level(player_level: int, required_level: int) -> bool:
    """Проверяет уровень игрока"""
    return player_level >= required_level


def validate_gold(player_gold: int, price: int) -> bool:
    """Проверяет достаточно ли золота"""
    return player_gold >= price


# ============= КОНВЕРТАЦИЯ =============

def rarity_to_emoji(rarity: ItemRarity) -> str:
    """Конвертирует редкость в эмодзи"""
    emoji_map = {
        ItemRarity.NORMAL: "⚪",
        ItemRarity.MAGIC: "🔵",
        ItemRarity.RARE: "🟡",
        ItemRarity.UNIQUE: "🔴"
    }
    return emoji_map.get(rarity, "⚪")


def rarity_to_name(rarity: ItemRarity) -> str:
    """Конвертирует редкость в название"""
    name_map = {
        ItemRarity.NORMAL: "Обычный",
        ItemRarity.MAGIC: "Магический",
        ItemRarity.RARE: "Редкий",
        ItemRarity.UNIQUE: "Уникальный"
    }
    return name_map.get(rarity, "Обычный")


def item_type_to_emoji(item_type) -> str:
    """Конвертирует тип предмета в эмодзи"""
    emoji_map = {
        "weapon": "⚔️",
        "helmet": "⛑️",
        "armor": "🛡️",
        "gloves": "🧤",
        "boots": "👢",
        "belt": "🔗",
        "ring": "💍",
        "amulet": "📿",
        "flask": "🧪"
    }
    return emoji_map.get(item_type, "📦")


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_helpers():
    """Тест вспомогательных функций"""
    print("=" * 50)
    print("ТЕСТ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ")
    print("=" * 50)
    
    # Тест форматирования чисел
    print("\n🔹 Форматирование чисел:")
    print(f"  1234567 -> {format_number(1234567)}")
    
    # Тест полосок
    print("\n🔹 Полоски:")
    print(f"  HP: {format_hp_bar(75, 100)}")
    print(f"  EXP: {format_exp_bar(450, 1000)}")
    print(f"  Energy: {format_energy_bar(3, 5)}")
    
    # Тест прогресс-бара
    print("\n🔹 Прогресс-бар локации:")
    event_types = ["battle", "chest", "battle", "trap", "rest", "battle", "chest"]
    print(f"  {format_progress_bar(2, 7, event_types)}")
    
    # Тест визуализации
    print("\n🔹 Визуализация:")
    print(format_battle_view("👾"))
    
    # Тест расчета урона
    print("\n🔹 Расчет урона:")
    damage, crit = calculate_damage(50, 10, 150)
    print(f"  Урон: {damage}, Крит: {crit}")
    
    # Тест защиты
    print("\n🔹 Защита:")
    reduced = calculate_defense_reduction(50, 15)
    print(f"  50 урона с защитой 15 -> {reduced}")
    
    # Тест шанса уклонения
    print("\n🔹 Уклонение:")
    dodge = calculate_dodge_chance(20)
    print(f"  Ловкость 20 -> {dodge:.1f}% уклонения")


if __name__ == "__main__":
    test_helpers()
