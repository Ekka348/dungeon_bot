from data.items import WeaponType

# ============= БАЗОВЫЕ ХАРАКТЕРИСТИКИ ОРУЖИЯ =============

WEAPON_BASES = {
    # ============= ОДНОРУЧНЫЕ МЕЧИ =============
    "rusted_sword": {
        "name": "Ржавый меч",
        "emoji": "⚔️",
        "damage_range": (4, 8),
        "attack_speed": 1.5,
        "crit_chance": 5,
        "accuracy": 20,
        "requirements": {"str": 10, "dex": 10},
        "tier": 1,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "copper_sword": {
        "name": "Медный меч",
        "emoji": "⚔️",
        "damage_range": (6, 12),
        "attack_speed": 1.45,
        "crit_chance": 5,
        "accuracy": 25,
        "requirements": {"str": 20, "dex": 20},
        "tier": 2,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "saber": {
        "name": "Сабля",
        "emoji": "⚔️",
        "damage_range": (8, 16),
        "attack_speed": 1.5,
        "crit_chance": 5,
        "accuracy": 30,
        "requirements": {"str": 30, "dex": 40},
        "tier": 3,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "broad_sword": {
        "name": "Широкий меч",
        "emoji": "⚔️",
        "damage_range": (12, 22),
        "attack_speed": 1.35,
        "crit_chance": 5,
        "accuracy": 35,
        "requirements": {"str": 50, "dex": 35},
        "tier": 4,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "war_sword": {
        "name": "Воинский меч",
        "emoji": "⚔️",
        "damage_range": (15, 28),
        "attack_speed": 1.4,
        "crit_chance": 5,
        "accuracy": 40,
        "requirements": {"str": 68, "dex": 51},
        "tier": 5,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "ancient_sword": {
        "name": "Древний меч",
        "emoji": "⚔️",
        "damage_range": (18, 32),
        "attack_speed": 1.38,
        "crit_chance": 5.5,
        "accuracy": 45,
        "requirements": {"str": 80, "dex": 60},
        "tier": 6,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "elegant_sword": {
        "name": "Элегантный меч",
        "emoji": "⚔️",
        "damage_range": (22, 38),
        "attack_speed": 1.45,
        "crit_chance": 6,
        "accuracy": 50,
        "requirements": {"str": 95, "dex": 85},
        "tier": 7,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "twilight_blade": {
        "name": "Закатный клинок",
        "emoji": "⚔️",
        "damage_range": (26, 44),
        "attack_speed": 1.42,
        "crit_chance": 6.5,
        "accuracy": 55,
        "requirements": {"str": 115, "dex": 100},
        "tier": 8,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "gem_sword": {
        "name": "Самоцветный меч",
        "emoji": "⚔️",
        "damage_range": (30, 50),
        "attack_speed": 1.4,
        "crit_chance": 7,
        "accuracy": 60,
        "requirements": {"str": 135, "dex": 115},
        "tier": 9,
        "type": WeaponType.ONE_HAND_SWORD
    },
    "eternal_sword": {
        "name": "Меч вечного",
        "emoji": "⚔️✨",
        "damage_range": (35, 58),
        "attack_speed": 1.45,
        "crit_chance": 7.5,
        "accuracy": 70,
        "requirements": {"str": 158, "dex": 132},
        "tier": 10,
        "type": WeaponType.ONE_HAND_SWORD
    },
    
    # ============= ШПАГИ/РАПИРЫ =============
    "pirate_cutlass": {
        "name": "Пиратский тесак",
        "emoji": "⚔️",
        "damage_range": (10, 20),
        "attack_speed": 1.55,
        "crit_chance": 6,
        "accuracy": 45,
        "requirements": {"dex": 62},
        "implicit": "15% шанс кровотечения",
        "tier": 4,
        "type": WeaponType.THRUSTING_SWORD
    },
    "gladius": {
        "name": "Гладиус",
        "emoji": "⚔️",
        "damage_range": (14, 26),
        "attack_speed": 1.5,
        "crit_chance": 6.5,
        "accuracy": 50,
        "requirements": {"dex": 86},
        "implicit": "20% шанс кровотечения",
        "tier": 6,
        "type": WeaponType.THRUSTING_SWORD
    },
    "estoc": {
        "name": "Эсток",
        "emoji": "⚔️",
        "damage_range": (20, 34),
        "attack_speed": 1.48,
        "crit_chance": 7,
        "accuracy": 55,
        "requirements": {"dex": 104},
        "implicit": "+30% множитель крита",
        "tier": 8,
        "type": WeaponType.THRUSTING_SWORD
    },
    "tiger_hook": {
        "name": "Тигровый крюк",
        "emoji": "⚔️",
        "damage_range": (28, 46),
        "attack_speed": 1.52,
        "crit_chance": 7.5,
        "accuracy": 60,
        "requirements": {"dex": 142},
        "implicit": "25% шанс кровотечения",
        "tier": 10,
        "type": WeaponType.THRUSTING_SWORD
    },
    
    # ============= ОДНОРУЧНЫЕ ТОПОРЫ =============
    "rusty_hatchet": {
        "name": "Ржавый топорик",
        "emoji": "🪓",
        "damage_range": (5, 10),
        "attack_speed": 1.35,
        "crit_chance": 5,
        "requirements": {"str": 16, "dex": 10},
        "tier": 1,
        "type": WeaponType.ONE_HAND_AXE
    },
    "jade_axe": {
        "name": "Нефритовый топор",
        "emoji": "🪓",
        "damage_range": (8, 16),
        "attack_speed": 1.32,
        "crit_chance": 5,
        "requirements": {"str": 29, "dex": 17},
        "tier": 2,
        "type": WeaponType.ONE_HAND_AXE
    },
    "boarding_axe": {
        "name": "Абордажный топор",
        "emoji": "🪓",
        "damage_range": (12, 22),
        "attack_speed": 1.3,
        "crit_chance": 5,
        "requirements": {"str": 45, "dex": 26},
        "tier": 3,
        "type": WeaponType.ONE_HAND_AXE
    },
    "cleaver": {
        "name": "Секач",
        "emoji": "🪓",
        "damage_range": (16, 28),
        "attack_speed": 1.28,
        "crit_chance": 5,
        "requirements": {"str": 62, "dex": 35},
        "tier": 4,
        "type": WeaponType.ONE_HAND_AXE
    },
    "carpenter_axe": {
        "name": "Плотничий топор",
        "emoji": "🪓",
        "damage_range": (20, 34),
        "attack_speed": 1.3,
        "crit_chance": 5,
        "requirements": {"str": 80, "dex": 45},
        "tier": 5,
        "type": WeaponType.ONE_HAND_AXE
    },
    "battle_axe": {
        "name": "Боевой топор",
        "emoji": "🪓",
        "damage_range": (25, 42),
        "attack_speed": 1.25,
        "crit_chance": 5.5,
        "requirements": {"str": 98, "dex": 54},
        "tier": 6,
        "type": WeaponType.ONE_HAND_AXE
    },
    "decorative_axe": {
        "name": "Украшенный топор",
        "emoji": "🪓",
        "damage_range": (27, 50),
        "attack_speed": 1.2,
        "crit_chance": 5,
        "requirements": {"str": 80, "dex": 23},
        "tier": 7,
        "type": WeaponType.ONE_HAND_AXE
    },
    "savage_axe": {
        "name": "Жестокий топор",
        "emoji": "🪓",
        "damage_range": (35, 58),
        "attack_speed": 1.22,
        "crit_chance": 5.5,
        "requirements": {"str": 125, "dex": 70},
        "tier": 8,
        "type": WeaponType.ONE_HAND_AXE
    },
    "ghost_axe": {
        "name": "Призрачный топор",
        "emoji": "🪓👻",
        "damage_range": (42, 68),
        "attack_speed": 1.28,
        "crit_chance": 6,
        "requirements": {"str": 148, "dex": 86},
        "tier": 9,
        "type": WeaponType.ONE_HAND_AXE
    },
    "demon_axe": {
        "name": "Бесовской топор",
        "emoji": "🪓👹",
        "damage_range": (50, 80),
        "attack_speed": 1.25,
        "crit_chance": 6.5,
        "requirements": {"str": 172, "dex": 99},
        "tier": 10,
        "type": WeaponType.ONE_HAND_AXE
    },
    
    # ============= ОДНОРУЧНЫЕ БУЛАВЫ =============
    "driftwood_club": {
        "name": "Дубинка из плавника",
        "emoji": "🔨",
        "damage_range": (4, 7),
        "attack_speed": 1.45,
        "crit_chance": 5,
        "requirements": {"str": 10},
        "tier": 1,
        "type": WeaponType.ONE_HAND_MACE
    },
    "spiked_club": {
        "name": "Шипастая дубинка",
        "emoji": "🔨",
        "damage_range": (11, 19),
        "attack_speed": 1.45,
        "crit_chance": 5,
        "requirements": {"str": 16},
        "tier": 2,
        "type": WeaponType.ONE_HAND_MACE
    },
    "stone_hammer": {
        "name": "Каменный молот",
        "emoji": "🔨",
        "damage_range": (19, 30),
        "attack_speed": 1.45,
        "crit_chance": 5,
        "requirements": {"str": 29},
        "tier": 3,
        "type": WeaponType.ONE_HAND_MACE
    },
    "war_hammer": {
        "name": "Воинский молот",
        "emoji": "🔨",
        "damage_range": (25, 40),
        "attack_speed": 1.4,
        "crit_chance": 5,
        "requirements": {"str": 45},
        "tier": 4,
        "type": WeaponType.ONE_HAND_MACE
    },
    "plated_mace": {
        "name": "Булава с пластинами",
        "emoji": "🔨",
        "damage_range": (32, 50),
        "attack_speed": 1.35,
        "crit_chance": 5,
        "requirements": {"str": 62},
        "tier": 5,
        "type": WeaponType.ONE_HAND_MACE
    },
    "ceremonial_mace": {
        "name": "Церемониальная булава",
        "emoji": "🔨✨",
        "damage_range": (38, 60),
        "attack_speed": 1.38,
        "crit_chance": 5.5,
        "requirements": {"str": 80},
        "tier": 6,
        "type": WeaponType.ONE_HAND_MACE
    },
    "glimmer_mace": {
        "name": "Сверкающая булава",
        "emoji": "🔨🌟",
        "damage_range": (44, 70),
        "attack_speed": 1.4,
        "crit_chance": 6,
        "requirements": {"str": 98},
        "tier": 7,
        "type": WeaponType.ONE_HAND_MACE
    },
    "vision_mace": {
        "name": "Булава видений",
        "emoji": "🔨👁️",
        "damage_range": (52, 82),
        "attack_speed": 1.35,
        "crit_chance": 6.5,
        "requirements": {"str": 118},
        "tier": 8,
        "type": WeaponType.ONE_HAND_MACE
    },
    "worm_mace": {
        "name": "Булава червя",
        "emoji": "🔨🪱",
        "damage_range": (60, 95),
        "attack_speed": 1.3,
        "crit_chance": 6,
        "requirements": {"str": 140},
        "tier": 9,
        "type": WeaponType.ONE_HAND_MACE
    },
    "dragon_mace": {
        "name": "Булава дракона",
        "emoji": "🔨🐉",
        "damage_range": (70, 110),
        "attack_speed": 1.32,
        "crit_chance": 7,
        "requirements": {"str": 165},
        "tier": 10,
        "type": WeaponType.ONE_HAND_MACE
    },
    
    # ============= КОГТИ =============
    "nail_claw": {
        "name": "Коготь-ноготь",
        "emoji": "🐾",
        "damage_range": (5, 12),
        "attack_speed": 1.6,
        "crit_chance": 6,
        "life_on_hit": 3,
        "requirements": {"dex": 22, "int": 12},
        "tier": 1,
        "type": WeaponType.CLAW
    },
    "shark_claw": {
        "name": "Акулий коготь",
        "emoji": "🐾🦈",
        "damage_range": (12, 24),
        "attack_speed": 1.55,
        "crit_chance": 6.5,
        "life_on_hit": 6,
        "requirements": {"dex": 48, "int": 26},
        "tier": 3,
        "type": WeaponType.CLAW
    },
    "eagle_claw": {
        "name": "Орлиный коготь",
        "emoji": "🐾🦅",
        "damage_range": (20, 38),
        "attack_speed": 1.58,
        "crit_chance": 7,
        "life_on_hit": 10,
        "requirements": {"dex": 84, "int": 45},
        "tier": 5,
        "type": WeaponType.CLAW
    },
    "demon_claw": {
        "name": "Демонический коготь",
        "emoji": "🐾👹",
        "damage_range": (32, 56),
        "attack_speed": 1.52,
        "crit_chance": 7.5,
        "life_on_hit": 15,
        "requirements": {"dex": 128, "int": 68},
        "tier": 7,
        "type": WeaponType.CLAW
    },
    "void_claw": {
        "name": "Коготь пустоты",
        "emoji": "🐾🌑",
        "damage_range": (45, 75),
        "attack_speed": 1.54,
        "crit_chance": 8,
        "life_on_hit": 20,
        "requirements": {"dex": 172, "int": 92},
        "tier": 9,
        "type": WeaponType.CLAW
    },
    
    # ============= КИНЖАЛЫ =============
    "glass_dagger": {
        "name": "Стеклянный кинжал",
        "emoji": "🗡️",
        "damage_range": (4, 10),
        "attack_speed": 1.6,
        "crit_chance": 6,
        "accuracy": 60,
        "requirements": {"dex": 15, "int": 15},
        "tier": 1,
        "type": WeaponType.DAGGER
    },
    "poison_dagger": {
        "name": "Отравленный кинжал",
        "emoji": "🗡️☠️",
        "damage_range": (8, 18),
        "attack_speed": 1.55,
        "crit_chance": 6.5,
        "accuracy": 70,
        "requirements": {"dex": 34, "int": 34},
        "tier": 2,
        "type": WeaponType.DAGGER
    },
    "assassin_dagger": {
        "name": "Кинжал убийцы",
        "emoji": "🗡️🔪",
        "damage_range": (14, 28),
        "attack_speed": 1.58,
        "crit_chance": 7,
        "accuracy": 85,
        "requirements": {"dex": 62, "int": 62},
        "tier": 4,
        "type": WeaponType.DAGGER
    },
    "gut_ripper": {
        "name": "Потрошитель",
        "emoji": "🗡️💀",
        "damage_range": (22, 42),
        "attack_speed": 1.54,
        "crit_chance": 7.5,
        "accuracy": 95,
        "requirements": {"dex": 96, "int": 96},
        "tier": 6,
        "type": WeaponType.DAGGER
    },
    "imperial_dagger": {
        "name": "Имперский кинжал",
        "emoji": "🗡️👑",
        "damage_range": (32, 58),
        "attack_speed": 1.52,
        "crit_chance": 8,
        "accuracy": 110,
        "requirements": {"dex": 138, "int": 138},
        "tier": 8,
        "type": WeaponType.DAGGER
    },
    "sai": {
        "name": "Сай",
        "emoji": "🗡️⚡",
        "damage_range": (40, 70),
        "attack_speed": 1.6,
        "crit_chance": 8.5,
        "accuracy": 120,
        "requirements": {"dex": 168, "int": 168},
        "tier": 10,
        "type": WeaponType.DAGGER
    },
    
    # ============= СКИПЕТРЫ =============
    "driftwood_sceptre": {
        "name": "Скипетр из плавника",
        "emoji": "🔱",
        "damage_range": (5, 11),
        "attack_speed": 1.35,
        "crit_chance": 6,
        "elemental_damage": 8,
        "requirements": {"str": 16, "int": 16},
        "tier": 1,
        "type": WeaponType.SCEPTRE
    },
    "bronze_sceptre": {
        "name": "Бронзовый скипетр",
        "emoji": "🔱",
        "damage_range": (9, 19),
        "attack_speed": 1.32,
        "crit_chance": 6,
        "elemental_damage": 12,
        "requirements": {"str": 32, "int": 32},
        "tier": 2,
        "type": WeaponType.SCEPTRE
    },
    "iron_sceptre": {
        "name": "Железный скипетр",
        "emoji": "🔱",
        "damage_range": (14, 28),
        "attack_speed": 1.3,
        "crit_chance": 6,
        "elemental_damage": 16,
        "requirements": {"str": 54, "int": 54},
        "tier": 3,
        "type": WeaponType.SCEPTRE
    },
    "ritual_sceptre": {
        "name": "Ритуальный скипетр",
        "emoji": "🔱🕯️",
        "damage_range": (22, 40),
        "attack_speed": 1.28,
        "crit_chance": 6.5,
        "elemental_damage": 22,
        "requirements": {"str": 84, "int": 84},
        "tier": 5,
        "type": WeaponType.SCEPTRE
    },
    "crystal_sceptre": {
        "name": "Кристальный скипетр",
        "emoji": "🔱💎",
        "damage_range": (34, 60),
        "attack_speed": 1.32,
        "crit_chance": 7,
        "elemental_damage": 30,
        "requirements": {"str": 122, "int": 122},
        "tier": 7,
        "type": WeaponType.SCEPTRE
    },
    "void_sceptre": {
        "name": "Скипетр пустоты",
        "emoji": "🔱🌌",
        "damage_range": (48, 85),
        "attack_speed": 1.3,
        "crit_chance": 7.5,
        "elemental_damage": 40,
        "requirements": {"str": 168, "int": 168},
        "tier": 9,
        "type": WeaponType.SCEPTRE
    },
    "alternating_sceptre": {
        "name": "Альтернирующий скипетр",
        "emoji": "🔱⚡",
        "damage_range": (55, 100),
        "attack_speed": 1.35,
        "crit_chance": 8,
        "elemental_damage": 50,
        "requirements": {"str": 190, "int": 190},
        "tier": 10,
        "type": WeaponType.SCEPTRE
    },
    
    # ============= ДВУРУЧНЫЕ МЕЧИ =============
    "corroded_blade": {
        "name": "Проржавевший клинок",
        "emoji": "⚔️⚔️",
        "damage_range": (12, 24),
        "attack_speed": 1.25,
        "crit_chance": 5,
        "accuracy": 40,
        "requirements": {"str": 32, "dex": 25},
        "tier": 1,
        "type": WeaponType.TWO_HAND_SWORD
    },
    "bastard_sword": {
        "name": "Полуторный меч",
        "emoji": "⚔️⚔️",
        "damage_range": (20, 38),
        "attack_speed": 1.22,
        "crit_chance": 5.5,
        "accuracy": 50,
        "requirements": {"str": 58, "dex": 45},
        "tier": 3,
        "type": WeaponType.TWO_HAND_SWORD
    },
    "claymore": {
        "name": "Клеймор",
        "emoji": "⚔️⚔️",
        "damage_range": (32, 58),
        "attack_speed": 1.18,
        "crit_chance": 5.5,
        "accuracy": 60,
        "requirements": {"str": 92, "dex": 68},
        "tier": 5,
        "type": WeaponType.TWO_HAND_SWORD
    },
    "executioner_sword": {
        "name": "Меч палача",
        "emoji": "⚔️⚔️💀",
        "damage_range": (45, 80),
        "attack_speed": 1.15,
        "crit_chance": 6,
        "accuracy": 70,
        "requirements": {"str": 134, "dex": 96},
        "tier": 7,
        "type": WeaponType.TWO_HAND_SWORD
    },
    "lion_sword": {
        "name": "Львиный меч",
        "emoji": "⚔️⚔️🦁",
        "damage_range": (60, 105),
        "attack_speed": 1.2,
        "crit_chance": 6.5,
        "accuracy": 85,
        "requirements": {"str": 178, "dex": 126},
        "tier": 9,
        "type": WeaponType.TWO_HAND_SWORD
    },
    
    # ============= ДВУРУЧНЫЕ ТОПОРЫ =============
    "stone_axe": {
        "name": "Каменный топор",
        "emoji": "🪓🪓",
        "damage_range": (14, 28),
        "attack_speed": 1.2,
        "crit_chance": 5,
        "requirements": {"str": 40, "dex": 16},
        "tier": 1,
        "type": WeaponType.TWO_HAND_AXE
    },
    "jade_chopper": {
        "name": "Нефритовое рубило",
        "emoji": "🪓🪓",
        "damage_range": (24, 46),
        "attack_speed": 1.18,
        "crit_chance": 5,
        "requirements": {"str": 70, "dex": 29},
        "tier": 3,
        "type": WeaponType.TWO_HAND_AXE
    },
    "labrys": {
        "name": "Лабрис",
        "emoji": "🪓🪓",
        "damage_range": (40, 72),
        "attack_speed": 1.15,
        "crit_chance": 5,
        "requirements": {"str": 110, "dex": 45},
        "tier": 5,
        "type": WeaponType.TWO_HAND_AXE
    },
    "ezomite_axe": {
        "name": "Топор Эзомита",
        "emoji": "🪓🪓",
        "damage_range": (58, 102),
        "attack_speed": 1.12,
        "crit_chance": 5.5,
        "requirements": {"str": 158, "dex": 64},
        "tier": 7,
        "type": WeaponType.TWO_HAND_AXE
    },
    "vaal_axe": {
        "name": "Топор Ваал",
        "emoji": "🪓🪓👹",
        "damage_range": (80, 140),
        "attack_speed": 1.14,
        "crit_chance": 6,
        "requirements": {"str": 202, "dex": 82},
        "tier": 9,
        "type": WeaponType.TWO_HAND_AXE
    },
    "despot_axe": {
        "name": "Топор деспота",
        "emoji": "🪓🪓👑",
        "damage_range": (95, 165),
        "attack_speed": 1.16,
        "crit_chance": 6.5,
        "requirements": {"str": 230, "dex": 95},
        "tier": 10,
        "type": WeaponType.TWO_HAND_AXE
    },
    
    # ============= ДВУРУЧНЫЕ БУЛАВЫ/МОЛОТЫ =============
    "driftwood_maul": {
        "name": "Дубина из плавника",
        "emoji": "🔨🔨",
        "damage_range": (16, 32),
        "attack_speed": 1.15,
        "crit_chance": 5,
        "stun_multiplier": 1.3,
        "requirements": {"str": 42},
        "tier": 1,
        "type": WeaponType.TWO_HAND_MACE
    },
    "great_maul": {
        "name": "Кувалда",
        "emoji": "🔨🔨",
        "damage_range": (30, 58),
        "attack_speed": 1.12,
        "crit_chance": 5,
        "stun_multiplier": 1.4,
        "requirements": {"str": 78},
        "tier": 3,
        "type": WeaponType.TWO_HAND_MACE
    },
    "brass_hammer": {
        "name": "Латунный молот",
        "emoji": "🔨🔨",
        "damage_range": (48, 88),
        "attack_speed": 1.1,
        "crit_chance": 5,
        "stun_multiplier": 1.45,
        "requirements": {"str": 120},
        "tier": 5,
        "type": WeaponType.TWO_HAND_MACE
    },
    "gavel": {
        "name": "Молот судьи",
        "emoji": "🔨🔨⚖️",
        "damage_range": (65, 115),
        "attack_speed": 1.08,
        "crit_chance": 5.5,
        "stun_multiplier": 1.5,
        "requirements": {"str": 168},
        "tier": 7,
        "type": WeaponType.TWO_HAND_MACE
    },
    "colossus_hammer": {
        "name": "Чудовищный молот",
        "emoji": "🔨🔨👹",
        "damage_range": (88, 152),
        "attack_speed": 1.05,
        "crit_chance": 5.5,
        "stun_multiplier": 1.6,
        "requirements": {"str": 215},
        "tier": 9,
        "type": WeaponType.TWO_HAND_MACE
    },
    
    # ============= ПОСОХИ =============
    "wooden_staff": {
        "name": "Деревянный посох",
        "emoji": "🏑",
        "damage_range": (10, 22),
        "attack_speed": 1.25,
        "crit_chance": 6,
        "block_chance": 15,
        "requirements": {"str": 24, "int": 24},
        "tier": 1,
        "type": WeaponType.STAFF
    },
    "iron_staff": {
        "name": "Железный посох",
        "emoji": "🏑",
        "damage_range": (20, 40),
        "attack_speed": 1.22,
        "crit_chance": 6.5,
        "block_chance": 18,
        "requirements": {"str": 52, "int": 52},
        "tier": 3,
        "type": WeaponType.STAFF
    },
    "mystic_staff": {
        "name": "Мистический посох",
        "emoji": "🏑✨",
        "damage_range": (35, 65),
        "attack_speed": 1.2,
        "crit_chance": 7,
        "block_chance": 20,
        "requirements": {"str": 94, "int": 94},
        "tier": 5,
        "type": WeaponType.STAFF
    },
    "dragon_staff": {
        "name": "Драконий посох",
        "emoji": "🏑🐉",
        "damage_range": (55, 98),
        "attack_speed": 1.18,
        "crit_chance": 7.5,
        "block_chance": 22,
        "requirements": {"str": 148, "int": 148},
        "tier": 8,
        "type": WeaponType.STAFF
    },
    
    # ============= ШЕСТЫ/БОЕВЫЕ ПОСОХИ =============
    "bamboo_staff": {
        "name": "Бамбуковый шест",
        "emoji": "🏑🎋",
        "damage_range": (8, 18),
        "attack_speed": 1.5,
        "crit_chance": 6.5,
        "requirements": {"dex": 28, "int": 9},
        "tier": 1,
        "type": WeaponType.QUARTERSTAFF
    },
    "iron_quarterstaff": {
        "name": "Железный шест",
        "emoji": "🏑",
        "damage_range": (18, 38),
        "attack_speed": 1.42,
        "crit_chance": 7,
        "requirements": {"dex": 60, "int": 20},
        "tier": 3,
        "type": WeaponType.QUARTERSTAFF
    },
    "monk_staff": {
        "name": "Шест монаха",
        "emoji": "🏑🧘",
        "damage_range": (30, 58),
        "attack_speed": 1.45,
        "crit_chance": 7.5,
        "requirements": {"dex": 105, "int": 35},
        "tier": 5,
        "type": WeaponType.QUARTERSTAFF
    },
    "wind_staff": {
        "name": "Шест ветра",
        "emoji": "🏑🌪️",
        "damage_range": (48, 88),
        "attack_speed": 1.48,
        "crit_chance": 8,
        "requirements": {"dex": 158, "int": 52},
        "tier": 8,
        "type": WeaponType.QUARTERSTAFF
    },
    
    # ============= КОПЬЯ =============
    "wooden_spear": {
        "name": "Деревянное копье",
        "emoji": "🔱",
        "damage_range": (9, 20),
        "attack_speed": 1.35,
        "crit_chance": 5.5,
        "range_bonus": 1,
        "requirements": {"dex": 30, "str": 15},
        "tier": 1,
        "type": WeaponType.SPEAR
    },
    "iron_spear": {
        "name": "Железное копье",
        "emoji": "🔱",
        "damage_range": (20, 42),
        "attack_speed": 1.32,
        "crit_chance": 6,
        "range_bonus": 1.5,
        "requirements": {"dex": 68, "str": 34},
        "tier": 3,
        "type": WeaponType.SPEAR
    },
    "javelin": {
        "name": "Дротик",
        "emoji": "🔱⚡",
        "damage_range": (35, 68),
        "attack_speed": 1.38,
        "crit_chance": 6.5,
        "range_bonus": 2,
        "requirements": {"dex": 115, "str": 57},
        "tier": 5,
        "type": WeaponType.SPEAR
    },
    "harpoon": {
        "name": "Гарпун",
        "emoji": "🔱🐋",
        "damage_range": (52, 95),
        "attack_speed": 1.3,
        "crit_chance": 6.5,
        "range_bonus": 2.5,
        "requirements": {"dex": 165, "str": 82},
        "tier": 7,
        "type": WeaponType.SPEAR
    },
    "dragonspine_spear": {
        "name": "Копье драконьего хребта",
        "emoji": "🔱🐉",
        "damage_range": (72, 130),
        "attack_speed": 1.34,
        "crit_chance": 7,
        "range_bonus": 3,
        "requirements": {"dex": 210, "str": 105},
        "tier": 9,
        "type": WeaponType.SPEAR
    },
    
    # ============= ЦЕПЫ/КИСТЕНИ =============
    "chain_flail": {
        "name": "Цеп с шипами",
        "emoji": "⛓️🔗",
        "damage_range": (12, 28),
        "attack_speed": 1.28,
        "crit_chance": 5.5,
        "stun_multiplier": 1.2,
        "requirements": {"str": 38, "dex": 13},
        "tier": 2,
        "type": WeaponType.FLAIL
    },
    "war_flail": {
        "name": "Боевой цеп",
        "emoji": "⛓️⚔️",
        "damage_range": (28, 58),
        "attack_speed": 1.24,
        "crit_chance": 6,
        "stun_multiplier": 1.3,
        "requirements": {"str": 85, "dex": 28},
        "tier": 4,
        "type": WeaponType.FLAIL
    },
    "morning_star": {
        "name": "Моргенштерн",
        "emoji": "⛓️⭐",
        "damage_range": (45, 88),
        "attack_speed": 1.2,
        "crit_chance": 6,
        "stun_multiplier": 1.4,
        "requirements": {"str": 140, "dex": 46},
        "tier": 6,
        "type": WeaponType.FLAIL
    },
    "holy_flail": {
        "name": "Священный цеп",
        "emoji": "⛓️✨",
        "damage_range": (62, 115),
        "attack_speed": 1.26,
        "crit_chance": 6.5,
        "stun_multiplier": 1.45,
        "requirements": {"str": 185, "dex": 62},
        "tier": 8,
        "type": WeaponType.FLAIL
    },
}

# ============= УНИКАЛЬНОЕ ОРУЖИЕ =============

UNIQUE_WEAPONS = {
    "frost_breath": {
        "name": "Ледяное дыхание",
        "base": "two_hand_mace",
        "emoji": "🔨❄️",
        "damage_range": (80, 140),
        "attack_speed": 1.1,
        "crit_chance": 7,
        "fixed_mods": {
            "damage": 50,
            "cold_damage": 30,
            "freeze_chance": 15
        },
        "requirements": {"str": 150},
        "description": "Коснись врага - и он станет льдом"
    },
    "soul_ripper": {
        "name": "Потрошитель душ",
        "base": "claw",
        "emoji": "🐾💀",
        "damage_range": (45, 80),
        "attack_speed": 1.6,
        "crit_chance": 9,
        "fixed_mods": {
            "damage": 40,
            "life_on_hit": 25,
            "crit_chance": 10
        },
        "requirements": {"dex": 120, "int": 80},
        "description": "Каждый удар крадет не только жизнь, но и душу"
    },
    "dragonfang": {
        "name": "Клык дракона",
        "base": "spear",
        "emoji": "🔱🐉",
        "damage_range": (70, 130),
        "attack_speed": 1.3,
        "crit_chance": 8,
        "fixed_mods": {
            "damage": 60,
            "fire_damage": 40,
            "range_bonus": 4
        },
        "requirements": {"str": 100, "dex": 150},
        "description": "Копье, выкованное из зуба древнего дракона"
    },
    "thunderstorm": {
        "name": "Грозовой шторм",
        "base": "quarterstaff",
        "emoji": "🏑⚡",
        "damage_range": (50, 95),
        "attack_speed": 1.6,
        "crit_chance": 8.5,
        "fixed_mods": {
            "damage": 35,
            "lightning_damage": 50,
            "attack_speed": 0.3
        },
        "requirements": {"dex": 140, "int": 100},
        "description": "Каждый удар сопровождается раскатом грома"
    },
    "executioner": {
        "name": "Палач",
        "base": "two_hand_axe",
        "emoji": "🪓⚔️",
        "damage_range": (100, 180),
        "attack_speed": 1.1,
        "crit_chance": 7.5,
        "fixed_mods": {
            "damage": 80,
            "crit_multiplier": 50,
            "stun_multiplier": 1.8
        },
        "requirements": {"str": 200},
        "description": "Одно движение - одна голова"
    }
}
