from enum import Enum

# ============= ТИПЫ ПРЕДМЕТОВ =============

class ItemRarity(Enum):
    NORMAL = "normal"
    MAGIC = "magic"
    RARE = "rare"
    UNIQUE = "unique"

class ItemType(Enum):
    WEAPON = "weapon"
    HELMET = "helmet"
    ARMOR = "armor"
    GLOVES = "gloves"
    BOOTS = "boots"
    BELT = "belt"
    RING = "ring"
    AMULET = "amulet"
    FLASK = "flask"

class AffixType(Enum):
    PREFIX = "prefix"
    SUFFIX = "suffix"

# ============= ТИПЫ ОРУЖИЯ =============

class WeaponType:
    """Типы оружия ближнего боя"""
    ONE_HAND_SWORD = "one_hand_sword"
    THRUSTING_SWORD = "thrusting_sword"
    ONE_HAND_AXE = "one_hand_axe"
    ONE_HAND_MACE = "one_hand_mace"
    CLAW = "claw"
    DAGGER = "dagger"
    SCEPTRE = "sceptre"
    TWO_HAND_SWORD = "two_hand_sword"
    TWO_HAND_AXE = "two_hand_axe"
    TWO_HAND_MACE = "two_hand_mace"
    STAFF = "staff"
    QUARTERSTAFF = "quarterstaff"
    SPEAR = "spear"
    FLAIL = "flail"

# ============= АФФИКСЫ (МОДИФИКАТОРЫ) =============

PREFIXES = {
    # Оружие
    "weapon_damage": {"name": "Закаленное", "stat": "damage", "value": (5, 10), "tier": 1},
    "weapon_damage2": {"name": "Острое", "stat": "damage", "value": (10, 15), "tier": 2},
    "weapon_damage3": {"name": "Убийственное", "stat": "damage", "value": (15, 25), "tier": 3},
    "weapon_damage4": {"name": "Безжалостное", "stat": "damage", "value": (20, 35), "tier": 4},
    "weapon_damage5": {"name": "Смертоносное", "stat": "damage", "value": (30, 50), "tier": 5},
    
    # Здоровье
    "health": {"name": "Здоровое", "stat": "max_hp", "value": (10, 20), "tier": 1},
    "health2": {"name": "Крепкое", "stat": "max_hp", "value": (20, 35), "tier": 2},
    "health3": {"name": "Могучая", "stat": "max_hp", "value": (35, 50), "tier": 3},
    "health4": {"name": "Титаническое", "stat": "max_hp", "value": (50, 75), "tier": 4},
    "health5": {"name": "Бессмертное", "stat": "max_hp", "value": (75, 100), "tier": 5},
    
    # Защита
    "defense": {"name": "Прочное", "stat": "defense", "value": (3, 6), "tier": 1},
    "defense2": {"name": "Твердое", "stat": "defense", "value": (6, 10), "tier": 2},
    "defense3": {"name": "Несокрушимое", "stat": "defense", "value": (10, 15), "tier": 3},
    "defense4": {"name": "Адамантитовое", "stat": "defense", "value": (15, 22), "tier": 4},
    "defense5": {"name": "Божественное", "stat": "defense", "value": (20, 30), "tier": 5},
    
    # Скорость атаки
    "attack_speed": {"name": "Быстрое", "stat": "attack_speed", "value": (5, 10), "tier": 1},
    "attack_speed2": {"name": "Проворное", "stat": "attack_speed", "value": (10, 15), "tier": 2},
    "attack_speed3": {"name": "Вихревое", "stat": "attack_speed", "value": (15, 22), "tier": 3},
    "attack_speed4": {"name": "Неудержимое", "stat": "attack_speed", "value": (20, 30), "tier": 4},
    "attack_speed5": {"name": "Молниеносное", "stat": "attack_speed", "value": (25, 40), "tier": 5},
    
    # Точность
    "accuracy": {"name": "Точное", "stat": "accuracy", "value": (5, 10), "tier": 1},
    "accuracy2": {"name": "Меткое", "stat": "accuracy", "value": (10, 16), "tier": 2},
    "accuracy3": {"name": "Снайперское", "stat": "accuracy", "value": (16, 24), "tier": 3},
    "accuracy4": {"name": "Непревзойденное", "stat": "accuracy", "value": (20, 35), "tier": 4},
    "accuracy5": {"name": "Абсолютное", "stat": "accuracy", "value": (30, 50), "tier": 5},
}

SUFFIXES = {
    # Шанс крита
    "crit_chance": {"name": "Удачи", "stat": "crit_chance", "value": (3, 6), "tier": 1},
    "crit_chance2": {"name": "Везучего", "stat": "crit_chance", "value": (6, 10), "tier": 2},
    "crit_chance3": {"name": "Рока", "stat": "crit_chance", "value": (10, 15), "tier": 3},
    "crit_chance4": {"name": "Судьбы", "stat": "crit_chance", "value": (12, 20), "tier": 4},
    "crit_chance5": {"name": "Провидения", "stat": "crit_chance", "value": (15, 25), "tier": 5},
    
    # Множитель крита
    "crit_mult": {"name": "Боли", "stat": "crit_multiplier", "value": (10, 20), "tier": 1},
    "crit_mult2": {"name": "Агонии", "stat": "crit_multiplier", "value": (20, 30), "tier": 2},
    "crit_mult3": {"name": "Экзекуции", "stat": "crit_multiplier", "value": (30, 45), "tier": 3},
    "crit_mult4": {"name": "Мученичества", "stat": "crit_multiplier", "value": (40, 60), "tier": 4},
    "crit_mult5": {"name": "Апокалипсиса", "stat": "crit_multiplier", "value": (50, 80), "tier": 5},
    
    # Регенерация
    "life_regen": {"name": "Жизни", "stat": "life_regen", "value": (2, 4), "tier": 1},
    "life_regen2": {"name": "Возрождения", "stat": "life_regen", "value": (4, 7), "tier": 2},
    "life_regen3": {"name": "Бессмертия", "stat": "life_regen", "value": (7, 11), "tier": 3},
    "life_regen4": {"name": "Вечности", "stat": "life_regen", "value": (10, 15), "tier": 4},
    "life_regen5": {"name": "Феникса", "stat": "life_regen", "value": (12, 20), "tier": 5},
    
    # Вампиризм
    "life_leech": {"name": "Вампира", "stat": "life_on_hit", "value": (2, 5), "tier": 1},
    "life_leech2": {"name": "Кровопийцы", "stat": "life_on_hit", "value": (4, 8), "tier": 2},
    "life_leech3": {"name": "Носферату", "stat": "life_on_hit", "value": (6, 12), "tier": 3},
    "life_leech4": {"name": "Графа Дракулы", "stat": "life_on_hit", "value": (8, 16), "tier": 4},
    "life_leech5": {"name": "Бога Крови", "stat": "life_on_hit", "value": (10, 20), "tier": 5},
    
    # Оглушение
    "stun": {"name": "Грома", "stat": "stun_multiplier", "value": (10, 20), "tier": 1},
    "stun2": {"name": "Землетрясения", "stat": "stun_multiplier", "value": (15, 30), "tier": 2},
    "stun3": {"name": "Разрушителя", "stat": "stun_multiplier", "value": (20, 40), "tier": 3},
}

# ============= ФЛАСКИ =============

FLASKS = {
    "small_life": {
        "name": "Малая бутылка здоровья",
        "emoji": "🧪",
        "heal": 40,
        "uses": 3,
        "rarity": ItemRarity.NORMAL
    },
    "small_mana": {
        "name": "Малая бутылка маны",
        "emoji": "🧪",
        "heal": 30,
        "uses": 3,
        "rarity": ItemRarity.NORMAL
    },
    "medium_life": {
        "name": "Средняя бутылка здоровья",
        "emoji": "🧪✨",
        "heal": 65,
        "uses": 3,
        "rarity": ItemRarity.MAGIC
    },
    "large_life": {
        "name": "Большая бутылка здоровья",
        "emoji": "🧪🌟",
        "heal": 90,
        "uses": 3,
        "rarity": ItemRarity.RARE
    },
    "divine_life": {
        "name": "Божественная бутылка",
        "emoji": "🧪💫",
        "heal": 120,
        "uses": 3,
        "rarity": ItemRarity.UNIQUE
    }
}
