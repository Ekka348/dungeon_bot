import random

# ============= АКТ 1: ЛОКАЦИИ, МОНСТРЫ И КВЕСТЫ =============

class Act1:
    """Первый акт игры: Падший (The Fallen)"""
    
    # ============= ЛОКАЦИИ АКТА 1 =============
    LOCATIONS = {
        1: {
            "id": 1,
            "name": "Вход в бездну",
            "name_en": "Abyss Entrance",
            "description": "Тебя сбросили в темницу за преступления, которых ты не совершал. Холодный камень встречает твое падение. Вокруг лишь тьма и звуки капающей воды. Нужно найти выход.",
            "area_level": 1,
            "area_level_range": (1, 3),
            "biome": "dungeon_entrance",
            "next_location": 2,  # Следующая локация - убежище
            "monster_density": 0.7,  # 70% монстры, 30% сундуки
            "event_density": 0.3,
            "min_events": 5,
            "max_events": 5,  # Фиксированное количество
            "only_common_monsters": True,  # Только обычные монстры
            "only_common_chests": True,  # Только обычные сундуки
            "only_common_loot": True  # Только обычный лут
        },
        2: {
            "id": 2,
            "name": "Убежище отчаявшихся",
            "name_en": "Despair's Haven",
            "description": "Среди тьмы ты находишь импровизированное убежище. Здесь живут такие же отверженные, как и ты. Небольшой очаг, несколько палаток из тряпья и старый колодец - их единственная надежда на выживание.",
            "area_level": 1,
            "area_level_range": (1, 2),
            "biome": "safe_haven",
            "next_location": 3,
            "is_safe": True
        },
        3: {
            "id": 3,
            "name": "Кости катакомб",
            "name_en": "Bone Catacombs",
            "description": "Древние захоронения, где покоятся те, кто умер в этих темницах. Скелеты поднимаются из куч костей, не желая отпускать живых.",
            "area_level": 2,
            "area_level_range": (2, 4),
            "biome": "catacombs",
            "next_location": 4,
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 12,
            "max_events": 16
        },
        4: {
            "id": 4,
            "name": "Червивые туннели",
            "name_en": "Worm-eaten Tunnels",
            "description": "Огромные ходы, прорытые гигантскими существами. Стены пульсируют, словно живые. Здесь правят черви, пауки и другая подземная мерзость.",
            "area_level": 3,
            "area_level_range": (3, 5),
            "biome": "worm_tunnels",
            "next_location": 5,
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 12,
            "max_events": 16
        },
        5: {
            "id": 5,
            "name": "Гномьи чертоги",
            "name_en": "Dwarven Halls",
            "description": "Забытые залы древних гномов. Механизмы все еще работают, создавая жуткий скрежет. Орки облюбовали эти залы для своих темных ритуалов.",
            "area_level": 4,
            "area_level_range": (4, 6),
            "biome": "dwarven_halls",
            "next_location": 6,
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 14,
            "max_events": 18
        },
        6: {
            "id": 6,
            "name": "Тюрьма скорби",
            "name_en": "Prison of Sorrow",
            "description": "Главная тюрьма подземелья. Камеры переполнены обезумевшими заключенными. Кадавры и скелеты патрулируют коридоры. Надзиратель не дремлет.",
            "area_level": 5,
            "area_level_range": (5, 7),
            "biome": "prison",
            "next_location": 7,
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 16,
            "max_events": 20
        },
        7: {
            "id": 7,
            "name": "Грот сирен",
            "name_en": "Siren's Grotto",
            "description": "Подземное озеро, освещенное биолюминесценцией. Сирены поют свои жуткие песни, заманивая путников в воду. В глубинах ждет древний ужас.",
            "area_level": 6,
            "area_level_range": (6, 8),
            "biome": "grotto",
            "next_location": None,
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 16,
            "max_events": 20,
            "has_boss": True
        }
    }
    
    # ============= МОНСТРЫ ДЛЯ КАЖДОЙ ЛОКАЦИИ =============
    
    # Локация 1: Вход в бездну - только обычные монстры
    LOCATION1_MONSTERS = {
        "common": [
            {
                "name": "Гниющий узник",
                "name_en": "Rotten Prisoner",
                "base_hp": 20,
                "damage": (3, 6),
                "accuracy": 50,
                "defense": 1,
                "base_exp": 8,
                "emoji": "🧟",
                "image": "images/act1/rotten_prisoner.jpg",
                "description": "Бывший заключенный, умерший от голода. Теперь бродит по коридорам.",
                "spawn_weight": 40
            },
            {
                "name": "Большая крыса",
                "name_en": "Giant Rat",
                "base_hp": 15,
                "damage": (2, 5),
                "accuracy": 60,
                "defense": 0,
                "base_exp": 6,
                "emoji": "🐀",
                "image": "images/act1/giant_rat.jpg",
                "description": "Распухшая от падали крыса, совсем не боится людей.",
                "spawn_weight": 35
            },
            {
                "name": "Падальщик",
                "name_en": "Scavenger",
                "base_hp": 18,
                "damage": (3, 5),
                "accuracy": 55,
                "defense": 1,
                "base_exp": 7,
                "emoji": "🦇",
                "image": "images/act1/scavenger.jpg",
                "description": "Существо, питающееся останками. Быстрое и юркое.",
                "spawn_weight": 25
            }
        ],
        # В первой локации нет магических и редких монстров
        "magic": [],
        "rare": []
    }
    
    # Локация 3: Кости катакомб - скелеты и нежить
    LOCATION3_MONSTERS = {
        "common": [
            {
                "name": "Костяной страж",
                "name_en": "Bone Guardian",
                "base_hp": 30,
                "damage": (5, 9),
                "accuracy": 60,
                "defense": 2,
                "base_exp": 15,
                "emoji": "💀",
                "image": "images/act1/bone_guardian.jpg",
                "description": "Скелет воина, охраняющий гробницы вечность.",
                "spawn_weight": 35
            },
            {
                "name": "Блуждающий череп",
                "name_en": "Wandering Skull",
                "base_hp": 22,
                "damage": (4, 7),
                "accuracy": 65,
                "defense": 1,
                "base_exp": 12,
                "emoji": "💀👻",
                "image": "images/act1/wandering_skull.jpg",
                "description": "Череп, парящий в воздухе и клацающий зубами.",
                "spawn_weight": 30
            },
            {
                "name": "Склепный жук",
                "name_en": "Tomb Beetle",
                "base_hp": 25,
                "damage": (4, 8),
                "accuracy": 70,
                "defense": 3,
                "base_exp": 14,
                "emoji": "🪲",
                "image": "images/act1/tomb_beetle.jpg",
                "description": "Огромный жук, питающийся костным мозгом.",
                "spawn_weight": 35
            }
        ],
        "magic": [
            {
                "name": "Костяной жрец",
                "name_en": "Bone Priest",
                "base_hp": 45,
                "damage": (6, 12),
                "accuracy": 65,
                "defense": 3,
                "base_exp": 25,
                "emoji": "💀🔮",
                "image": "images/act1/bone_priest.jpg",
                "description": "Скелет в рваной мантии, призывающий падальщиков.",
                "spawn_weight": 50
            },
            {
                "name": "Склепный паук",
                "name_en": "Tomb Spider",
                "base_hp": 40,
                "damage": (7, 11),
                "accuracy": 75,
                "defense": 2,
                "base_exp": 22,
                "emoji": "🕷️",
                "image": "images/act1/tomb_spider.jpg",
                "description": "Паук, свивший гнездо в чьем-то черепе.",
                "spawn_weight": 50
            }
        ],
        "rare": [
            {
                "name": "Капитан стражи",
                "name_en": "Captain of the Guard",
                "base_hp": 70,
                "damage": (10, 18),
                "accuracy": 70,
                "defense": 5,
                "base_exp": 40,
                "emoji": "💀⚔️",
                "image": "images/act1/captain_guard.jpg",
                "description": "Бывший капитан стражи, теперь вечный страж катакомб.",
                "spawn_weight": 100
            }
        ]
    }
    
    # Локация 4: Червивые туннели - черви, пауки, жуки
    LOCATION4_MONSTERS = {
        "common": [
            {
                "name": "Огромный червь",
                "name_en": "Giant Worm",
                "base_hp": 40,
                "damage": (6, 12),
                "accuracy": 60,
                "defense": 3,
                "base_exp": 22,
                "emoji": "🪱",
                "image": "images/act1/giant_worm.jpg",
                "description": "Слепой, но чувствует вибрацию почвы.",
                "spawn_weight": 30
            },
            {
                "name": "Туннельный крот",
                "name_en": "Tunnel Mole",
                "base_hp": 45,
                "damage": (5, 11),
                "accuracy": 55,
                "defense": 5,
                "base_exp": 20,
                "emoji": "🐭",
                "image": "images/act1/tunnel_mole.jpg",
                "description": "Огромный крот с мощными когтями.",
                "spawn_weight": 25
            },
            {
                "name": "Ловчий паук",
                "name_en": "Hunter Spider",
                "base_hp": 30,
                "damage": (7, 13),
                "accuracy": 75,
                "defense": 2,
                "base_exp": 24,
                "emoji": "🕷️",
                "image": "images/act1/hunter_spider.jpg",
                "description": "Плетет липкую паутину в темных углах.",
                "spawn_weight": 25
            },
            {
                "name": "Многоножка-мутант",
                "name_en": "Mutant Centipede",
                "base_hp": 35,
                "damage": (5, 10),
                "accuracy": 65,
                "defense": 2,
                "base_exp": 21,
                "emoji": "🐛",
                "image": "images/act1/mutant_centipede.jpg",
                "description": "Ядовитая многоножка, покрытая слизью.",
                "spawn_weight": 20
            }
        ],
        "magic": [
            {
                "name": "Червь-короед",
                "name_en": "Bark Worm",
                "base_hp": 55,
                "damage": (9, 16),
                "accuracy": 65,
                "defense": 4,
                "base_exp": 35,
                "emoji": "🪱🌿",
                "image": "images/act1/bark_worm.jpg",
                "description": "Покрыт панцирем, как кора дерева.",
                "spawn_weight": 50
            },
            {
                "name": "Паучиха-матка",
                "name_en": "Spider Queen",
                "base_hp": 50,
                "damage": (8, 15),
                "accuracy": 70,
                "defense": 3,
                "base_exp": 38,
                "emoji": "🕷️🥚",
                "image": "images/act1/spider_queen.jpg",
                "description": "Носит на спине кокон с яйцами.",
                "spawn_weight": 50
            }
        ],
        "rare": [
            {
                "name": "Король червей",
                "name_en": "Worm King",
                "base_hp": 90,
                "damage": (12, 22),
                "accuracy": 68,
                "defense": 7,
                "base_exp": 60,
                "emoji": "🪱👑",
                "image": "images/act1/worm_king.jpg",
                "description": "Огромный червь с короной из хитина.",
                "spawn_weight": 100
            }
        ]
    }
    
    # Локация 5: Гномьи чертоги - орки, механизмы
    LOCATION5_MONSTERS = {
        "common": [
            {
                "name": "Орк-рабочий",
                "name_en": "Orc Worker",
                "base_hp": 45,
                "damage": (7, 13),
                "accuracy": 60,
                "defense": 4,
                "base_exp": 28,
                "emoji": "👹",
                "image": "images/act1/orc_worker.jpg",
                "description": "Носит тяжелый молот, ломает гномьи механизмы.",
                "spawn_weight": 35
            },
            {
                "name": "Гномий автоматон",
                "name_en": "Dwarven Automaton",
                "base_hp": 55,
                "damage": (8, 14),
                "accuracy": 70,
                "defense": 8,
                "base_exp": 32,
                "emoji": "🤖",
                "image": "images/act1/dwarven_automaton.jpg",
                "description": "Механизм, сошедший с ума после веков без хозяина.",
                "spawn_weight": 30
            },
            {
                "name": "Орк-шаман",
                "name_en": "Orc Shaman",
                "base_hp": 40,
                "damage": (5, 12),
                "accuracy": 65,
                "defense": 2,
                "base_exp": 30,
                "emoji": "👹🔮",
                "image": "images/act1/orc_shaman.jpg",
                "description": "Бормочет проклятия и кидается склянками с ядом.",
                "spawn_weight": 35
            }
        ],
        "magic": [
            {
                "name": "Орк-берсерк",
                "name_en": "Orc Berserker",
                "base_hp": 65,
                "damage": (12, 20),
                "accuracy": 65,
                "defense": 5,
                "base_exp": 45,
                "emoji": "👹⚔️",
                "image": "images/act1/orc_berserker.jpg",
                "description": "Впадает в ярость и атакует все, что движется.",
                "spawn_weight": 60
            },
            {
                "name": "Ржавый голем",
                "name_en": "Rust Golem",
                "base_hp": 80,
                "damage": (10, 18),
                "accuracy": 55,
                "defense": 12,
                "base_exp": 48,
                "emoji": "🗿⚙️",
                "image": "images/act1/rust_golem.jpg",
                "description": "Гномий голем, покрытый ржавчиной.",
                "spawn_weight": 40
            }
        ],
        "rare": [
            {
                "name": "Орк-машинист",
                "name_en": "Orc Machinist",
                "base_hp": 95,
                "damage": (14, 25),
                "accuracy": 68,
                "defense": 8,
                "base_exp": 70,
                "emoji": "👹⚙️",
                "image": "images/act1/orc_machinist.jpg",
                "description": "Взломал гномьи механизмы и использует их против врагов.",
                "spawn_weight": 100
            }
        ]
    }
    
    # Локация 6: Тюрьма скорби - кадавры, скелеты, заключенные
    LOCATION6_MONSTERS = {
        "common": [
            {
                "name": "Обезумевший заключенный",
                "name_en": "Insane Prisoner",
                "base_hp": 50,
                "damage": (8, 15),
                "accuracy": 65,
                "defense": 3,
                "base_exp": 35,
                "emoji": "👤💢",
                "image": "images/act1/insane_prisoner.jpg",
                "description": "Сломленный разумом, он видит врага в каждом.",
                "spawn_weight": 25
            },
            {
                "name": "Тюремный кадавр",
                "name_en": "Prison Cadaver",
                "base_hp": 60,
                "damage": (7, 14),
                "accuracy": 60,
                "defense": 5,
                "base_exp": 38,
                "emoji": "🧟",
                "image": "images/act1/prison_cadaver.jpg",
                "description": "Тело умершего в кандалах, все еще бредущее по коридорам.",
                "spawn_weight": 25
            },
            {
                "name": "Надзиратель-скелет",
                "name_en": "Warden Skeleton",
                "base_hp": 55,
                "damage": (9, 16),
                "accuracy": 70,
                "defense": 4,
                "base_exp": 40,
                "emoji": "💀🔑",
                "image": "images/act1/warden_skeleton.jpg",
                "description": "Скелет с ключами и дубиной, все еще охраняющий камеры.",
                "spawn_weight": 25
            },
            {
                "name": "Цепной призрак",
                "name_en": "Chain Ghost",
                "base_hp": 45,
                "damage": (10, 18),
                "accuracy": 75,
                "defense": 1,
                "base_exp": 42,
                "emoji": "👻⛓️",
                "image": "images/act1/chain_ghost.jpg",
                "description": "Призрак, умерший в цепях. Гремит кандалами.",
                "spawn_weight": 25
            }
        ],
        "magic": [
            {
                "name": "Палач-кадавр",
                "name_en": "Executioner Cadaver",
                "base_hp": 80,
                "damage": (15, 25),
                "accuracy": 68,
                "defense": 6,
                "base_exp": 60,
                "emoji": "🧟⚔️",
                "image": "images/act1/executioner_cadaver.jpg",
                "description": "Бывший палач, теперь сам стал нежитью, но не оставил топор.",
                "spawn_weight": 60
            },
            {
                "name": "Кровавый призрак",
                "name_en": "Blood Ghost",
                "base_hp": 65,
                "damage": (12, 22),
                "accuracy": 80,
                "defense": 2,
                "base_exp": 58,
                "emoji": "👻🩸",
                "image": "images/act1/blood_ghost.jpg",
                "description": "Призрак, истекающий призрачной кровью.",
                "spawn_weight": 40
            }
        ],
        "rare": [
            {
                "name": "Смотритель темниц",
                "name_en": "Dungeon Keeper",
                "base_hp": 120,
                "damage": (18, 30),
                "accuracy": 72,
                "defense": 10,
                "base_exp": 90,
                "emoji": "👹🔗",
                "image": "images/act1/dungeon_keeper.jpg",
                "description": "Главный надзиратель, не умерший, но ставший чем-то иным.",
                "spawn_weight": 100
            }
        ]
    }
    
    # Локация 7: Грот сирен - морские твари
    LOCATION7_MONSTERS = {
        "common": [
            {
                "name": "Сирена-певица",
                "name_en": "Siren Singer",
                "base_hp": 55,
                "damage": (9, 17),
                "accuracy": 75,
                "defense": 3,
                "base_exp": 45,
                "emoji": "🧜‍♀️",
                "image": "images/act1/siren_singer.jpg",
                "description": "Поет, зачаровывая путников. Голос проникает в разум.",
                "spawn_weight": 30
            },
            {
                "name": "Мерзкий сквиг",
                "name_en": "Foul Squig",
                "base_hp": 60,
                "damage": (10, 18),
                "accuracy": 65,
                "defense": 5,
                "base_exp": 48,
                "emoji": "🐙",
                "image": "images/act1/foul_squig.jpg",
                "description": "Маленький осьминог с острым клювом.",
                "spawn_weight": 25
            },
            {
                "name": "Глубинный краб",
                "name_en": "Deep Crab",
                "base_hp": 70,
                "damage": (8, 16),
                "accuracy": 60,
                "defense": 10,
                "base_exp": 50,
                "emoji": "🦀",
                "image": "images/act1/deep_crab.jpg",
                "description": "Краб с панцирем, покрытым водорослями и ракушками.",
                "spawn_weight": 20
            },
            {
                "name": "Скользкий угорь",
                "name_en": "Slippery Eel",
                "base_hp": 45,
                "damage": (11, 19),
                "accuracy": 80,
                "defense": 2,
                "base_exp": 46,
                "emoji": "🐍",
                "image": "images/act1/slippery_eel.jpg",
                "description": "Бьет током при прикосновении.",
                "spawn_weight": 25
            }
        ],
        "magic": [
            {
                "name": "Сирена-заклинательница",
                "name_en": "Siren Enchantress",
                "base_hp": 75,
                "damage": (12, 22),
                "accuracy": 78,
                "defense": 4,
                "base_exp": 65,
                "emoji": "🧜‍♀️✨",
                "image": "images/act1/siren_enchantress.jpg",
                "description": "Ее песня вызывает галлюцинации.",
                "spawn_weight": 55
            },
            {
                "name": "Спрут-ловец",
                "name_en": "Hunter Octopus",
                "base_hp": 85,
                "damage": (14, 24),
                "accuracy": 70,
                "defense": 8,
                "base_exp": 68,
                "emoji": "🐙🎣",
                "image": "images/act1/hunter_octopus.jpg",
                "description": "Щупальца тянутся из темной воды.",
                "spawn_weight": 45
            }
        ],
        "rare": [
            {
                "name": "Древний страж глубин",
                "name_en": "Ancient Deep Guardian",
                "base_hp": 150,
                "damage": (18, 30),
                "accuracy": 72,
                "defense": 12,
                "base_exp": 120,
                "emoji": "🐙👁️",
                "image": "images/act1/deep_guardian.jpg",
                "description": "Древнее существо, охраняющее вход в логово спрута.",
                "spawn_weight": 100
            }
        ]
    }
    
    # ============= БОСС АКТА 1 =============
    ACT1_BOSS = {
        "name": "Древний спрут",
        "name_en": "Ancient Kraken",
        "base_hp": 300,
        "damage": (25, 45),
        "accuracy": 80,
        "defense": 18,
        "base_exp": 300,
        "emoji": "🐙🔥",
        "image": "images/act1/act1_boss.jpg",
        "description": "Гигантский спрут, древний хозяин этих вод. Его щупальца пробивают камень, а глаза светятся злобным умом.",
        "phases": [
            {"name": "Фаза 1: Спрут", "hp_percent": 100, "damage_mult": 1.0},
            {"name": "Фаза 2: Ярость глубин", "hp_percent": 50, "damage_mult": 1.5, "adds": ["Мерзкий сквиг", "Мерзкий сквиг"]},
            {"name": "Фаза 3: Предсмертный танец", "hp_percent": 20, "damage_mult": 2.0, "speed_mult": 1.3}
        ]
    }
    
    # ============= NPC В УБЕЖИЩЕ =============
    HAVEN_NPCS = [
        {
            "id": "morley",
            "name": "Старик Морли",
            "title": "Выживший",
            "emoji": "👴",
            "dialogue": {
                "first": "О, еще один бедолага... Добро пожаловать в наш скорбный приют. Мы все здесь отверженные. Я Морли, сижу здесь уже... сколько лет? Потерял счет. Держи это, пригодится в пути.",
                "idle": "Колодец восстанавливает силы, если что. Вода там... странная, но помогает.",
                "quest": "В тюрьме остались выжившие. Если найдешь их, приведи сюда. Мы должны держаться вместе."
            },
            "has_quest": True,
            "quest_id": "side_quest1"
        },
        {
            "id": "greg",
            "name": "Торговец Грег",
            "title": "Скупщик",
            "emoji": "🛒",
            "dialogue": {
                "first": "Товар есть? Деньги есть? У меня есть все, что нужно выжившему. Нашел в катакомбах... ну, не спрашивай где.",
                "idle": "Заходи, если что-то нужно. Или если хочешь что-то продать."
            },
            "is_merchant": True,
            "shop_items": ["rusted_sword", "spiked_club", "glass_dagger"]
        },
        {
            "id": "brock",
            "name": "Кузнец Брок",
            "title": "Бывший оружейник",
            "emoji": "⚒️",
            "dialogue": {
                "first": "Ха! Живой! Я Брок, кую что могу из того хлама, что нахожу в туннелях. Могу и тебе сварганить что-нибудь... за монету, конечно.",
                "idle": "У меня есть пара неплохих клинков. Сам проверял на местных тварях."
            },
            "is_blacksmith": True,
            "shop_items": ["copper_sword", "stone_hammer"]
        },
        {
            "id": "ellie",
            "name": "Безумная Элли",
            "title": "Провидица",
            "emoji": "🔮",
            "dialogue": {
                "first": "Я вижу... вижу твою судьбу! Ты пройдешь через тьму и выйдешь к свету! Но сначала... принеси мне кое-что из туннелей. Я заплачу.",
                "idle": "Глубины зовут... слышишь? Они шепчут...",
                "quest1": "Мой амулет... я потеряла его в Костях катакомб. Без него я не могу видеть будущее. Найди его, прошу.",
                "quest2": "Надзиратель тюрьмы мучает души заключенных. Освободи их, убей его.",
                "quest3": "Я видела видение - выход через Грот сирен. Убей древнего спрута и выйди на свободу."
            },
            "has_quest": True,
            "quest_ids": ["quest1", "quest2", "quest3"]
        }
    ]
    
    # ============= КВЕСТЫ АКТА 1 =============
    QUESTS = {
        "quest1": {
            "id": "quest1",
            "name": "Потерянный амулет",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Элли потеряла свой амулет где-то в Костях катакомб. Без него она не может видеть будущее. Найди амулет.",
            "objectives": [
                {"type": "find_item", "item": "amulet", "location": 3, "progress": 0, "required": 1}
            ],
            "rewards": {
                "exp": 100,
                "gold": 50
            },
            "next_quest": "quest2"
        },
        "quest2": {
            "id": "quest2",
            "name": "Проклятие надзирателя",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Надзиратель тюрьмы мучает души заключенных. Элли просит освободить их, убив надзирателя.",
            "objectives": [
                {"type": "kill_boss", "boss": "Смотритель темниц", "location": 6, "progress": 0, "required": 1}
            ],
            "rewards": {
                "exp": 200,
                "gold": 150,
                "item": "unique_ring"
            },
            "next_quest": "quest3"
        },
        "quest3": {
            "id": "quest3",
            "name": "Выход наружу",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Элли видела видение - выход через Грот сирен. Убей древнего спрута и выйди на свободу.",
            "objectives": [
                {"type": "kill_boss", "boss": "Древний спрут", "location": 7, "progress": 0, "required": 1}
            ],
            "rewards": {
                "exp": 500,
                "gold": 300,
                "item": "unique_weapon"
            },
            "is_final": True
        },
        "side_quest1": {
            "id": "side_quest1",
            "name": "Помоги выжившим",
            "giver": "Старик Морли",
            "giver_id": "morley",
            "description": "В тюрьме остались выжившие. Морли просит найти их и привести в убежище.",
            "objectives": [
                {"type": "rescue", "target": "prisoners", "location": 6, "progress": 0, "required": 3}
            ],
            "rewards": {
                "exp": 150,
                "gold": 100
            }
        },
        "side_quest2": {
            "id": "side_quest2",
            "name": "Червивая проблема",
            "giver": "Торговец Грег",
            "giver_id": "greg",
            "description": "Черви расплодились в туннелях и мешают Грегу собирать хлам. Убей 10 червей.",
            "objectives": [
                {"type": "kill_monsters", "monster": "Огромный червь", "location": 4, "progress": 0, "required": 10}
            ],
            "rewards": {
                "exp": 120,
                "gold": 80
            }
        }
    }
    
    # ============= ТОВАРЫ В УБЕЖИЩЕ =============
    MERCHANT_ITEMS = {
        "rusted_sword": {
            "name": "Ржавый меч",
            "type": "weapon",
            "base": "rusted_sword",
            "price": 50,
            "min_level": 1,
            "description": "Старый, но еще острый меч.",
            "emoji": "⚔️"
        },
        "spiked_club": {
            "name": "Дубинка с шипами",
            "type": "weapon",
            "base": "spiked_club",
            "price": 60,
            "min_level": 1,
            "description": "Простое, но эффективное оружие.",
            "emoji": "🔨"
        },
        "glass_dagger": {
            "name": "Стеклянный кинжал",
            "type": "weapon",
            "base": "glass_dagger",
            "price": 45,
            "min_level": 1,
            "description": "Хрупкий, но острый.",
            "emoji": "🗡️"
        },
        "copper_sword": {
            "name": "Медный меч",
            "type": "weapon",
            "base": "copper_sword",
            "price": 120,
            "min_level": 2,
            "description": "Неплохой меч из меди.",
            "emoji": "⚔️"
        },
        "stone_hammer": {
            "name": "Каменный молот",
            "type": "weapon",
            "base": "stone_hammer",
            "price": 150,
            "min_level": 2,
            "description": "Тяжелый, но мощный.",
            "emoji": "🔨"
        }
    }
    
    # ============= МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ =============
    
    @classmethod
    def get_location_by_id(cls, location_id):
        """Получает локацию по ID"""
        return cls.LOCATIONS.get(location_id)
    
    @classmethod
    def get_first_location(cls):
        """Получает первую локацию акта"""
        return cls.LOCATIONS.get(1)
    
    @classmethod
    def get_haven_location(cls):
        """Получает убежище"""
        return cls.LOCATIONS.get(2)
    
    @classmethod
    def get_final_location(cls):
        """Получает финальную локацию акта"""
        return cls.LOCATIONS.get(7)
    
    @classmethod
    def get_location_monsters(cls, location_id, rarity="common"):
        """Получает монстров для конкретной локации"""
        location_monsters_map = {
            1: cls.LOCATION1_MONSTERS,
            3: cls.LOCATION3_MONSTERS,
            4: cls.LOCATION4_MONSTERS,
            5: cls.LOCATION5_MONSTERS,
            6: cls.LOCATION6_MONSTERS,
            7: cls.LOCATION7_MONSTERS
        }
        
        monsters_dict = location_monsters_map.get(location_id, {})
        return monsters_dict.get(rarity, [])
    
    @classmethod
    def get_random_monster(cls, location_id, rarity="common"):
        """Получает случайного монстра из локации с учетом весов"""
        monsters = cls.get_location_monsters(location_id, rarity)
        if not monsters:
            return None
        
        # Выбор с учетом весов
        weights = [m.get("spawn_weight", 100) for m in monsters]
        return random.choices(monsters, weights=weights)[0]
    
    @classmethod
    def generate_location_events(cls, location_id):
        """Генерирует события для локации"""
        location = cls.get_location_by_id(location_id)
        if not location or location.get("is_safe"):
            return []
        
        events = []
        num_events = location.get("min_events", 10)  # Используем фиксированное количество
        
        monster_density = location.get("monster_density", 0.7)
        
        # Проверяем флаги для первой локации
        only_common = location.get("only_common_monsters", False)
        only_common_chests = location.get("only_common_chests", False)
        
        for _ in range(num_events):
            if random.random() < monster_density:
                # Генерируем монстра
                if only_common:
                    # Только обычные монстры
                    rarity = "common"
                else:
                    # Обычное распределение редкости
                    rarity_roll = random.random()
                    if rarity_roll < 0.7:
                        rarity = "common"
                    elif rarity_roll < 0.95:
                        rarity = "magic"
                    else:
                        rarity = "rare"
                
                monster = cls.get_random_monster(location_id, rarity)
                if monster:
                    events.append({
                        "type": "battle",
                        "location_id": location_id,
                        "location_name": location["name"],
                        "monster": monster.copy(),
                        "rarity": rarity,
                        "completed": False
                    })
            else:
                # Генерируем сундук
                if only_common_chests:
                    chest_rarity = "common"
                else:
                    rarity_roll = random.random()
                    if rarity_roll < 0.7:
                        chest_rarity = "common"
                    elif rarity_roll < 0.95:
                        chest_rarity = "magic"
                    else:
                        chest_rarity = "rare"
                
                events.append({
                    "type": "chest",
                    "rarity": chest_rarity,
                    "location_id": location_id,
                    "location_name": location["name"],
                    "completed": False
                })
        
        return events
    
    @classmethod
    def get_npc_by_id(cls, npc_id):
        """Получает NPC по ID"""
        for npc in cls.HAVEN_NPCS:
            if npc["id"] == npc_id:
                return npc
        return None
    
    @classmethod
    def get_quest_by_id(cls, quest_id):
        """Получает квест по ID"""
        return cls.QUESTS.get(quest_id)
    
    @classmethod
    def get_merchant_item(cls, item_id):
        """Получает товар по ID"""
        return cls.MERCHANT_ITEMS.get(item_id)
    
    @classmethod
    def get_available_quests(cls, player_level=1):
        """Получает доступные квесты для игрока"""
        available = []
        for quest_id, quest in cls.QUESTS.items():
            # Здесь можно добавить проверку на уровень и предыдущие квесты
            available.append(quest)
        return available
    
    @classmethod
    def check_quest_objective(cls, quest, objective_type, target, location_id=None):
        """Проверяет выполнение цели квеста"""
        for obj in quest["objectives"]:
            if obj["type"] == objective_type:
                if objective_type == "kill_boss" and obj["boss"] == target:
                    return True
                elif objective_type == "kill_monsters" and obj["monster"] == target:
                    return True
                elif objective_type == "find_item" and obj["item"] == target and obj["location"] == location_id:
                    return True
                elif objective_type == "rescue" and obj["target"] == target and obj["location"] == location_id:
                    return True
        return False
    
    @classmethod
    def update_quest_progress(cls, quest, objective_type, target, amount=1):
        """Обновляет прогресс квеста"""
        for obj in quest["objectives"]:
            if obj["type"] == objective_type:
                if objective_type == "kill_boss" and obj["boss"] == target:
                    obj["progress"] = min(obj["progress"] + amount, obj["required"])
                    return obj["progress"] >= obj["required"]
                elif objective_type == "kill_monsters" and obj["monster"] == target:
                    obj["progress"] = min(obj["progress"] + amount, obj["required"])
                    return obj["progress"] >= obj["required"]
                elif objective_type == "find_item" and obj["item"] == target:
                    obj["progress"] = min(obj["progress"] + amount, obj["required"])
                    return obj["progress"] >= obj["required"]
                elif objective_type == "rescue" and obj["target"] == target:
                    obj["progress"] = min(obj["progress"] + amount, obj["required"])
                    return obj["progress"] >= obj["required"]
        return False
    
    @classmethod
    def is_quest_completed(cls, quest):
        """Проверяет, выполнен ли квест"""
        for obj in quest["objectives"]:
            if obj["progress"] < obj["required"]:
                return False
        return True
    
    @classmethod
    def get_quest_rewards(cls, quest_id):
        """Получает награды за квест"""
        quest = cls.get_quest_by_id(quest_id)
        if quest:
            return quest.get("rewards", {})
        return {}
    
    @classmethod
    def get_next_quest(cls, quest_id):
        """Получает следующий квест после текущего"""
        quest = cls.get_quest_by_id(quest_id)
        if quest and "next_quest" in quest:
            return cls.get_quest_by_id(quest["next_quest"])
        return None
    
    @classmethod
    def generate_act1_dungeon(cls):
        """Генерирует полное подземелье для акта 1"""
        dungeon = []
        
        # Локация 1: Вход в бездну
        location1_events = cls.generate_location_events(1)
        dungeon.extend(location1_events)
        
        # После последнего события первой локации автоматический переход в убежище
        # (без дополнительной кнопки перехода)
        
        # Локация 3: Кости катакомб
        location3_events = cls.generate_location_events(3)
        dungeon.extend(location3_events)
        
        # Переход к локации 4
        dungeon.append({
            "type": "transition",
            "to_location": 4,
            "message": "Кости заканчиваются, стены становятся мягкими и влажными. Туннели червей...",
            "completed": False
        })
        
        # Локация 4: Червивые туннели
        location4_events = cls.generate_location_events(4)
        dungeon.extend(location4_events)
        
        # Переход к локации 5
        dungeon.append({
            "type": "transition",
            "to_location": 5,
            "message": "Туннели расширяются, появляются грубые каменные стены. Гномьи чертоги...",
            "completed": False
        })
        
        # Локация 5: Гномьи чертоги
        location5_events = cls.generate_location_events(5)
        dungeon.extend(location5_events)
        
        # Переход к локации 6
        dungeon.append({
            "type": "transition",
            "to_location": 6,
            "message": "Запах смерти становится невыносимым. Впереди тюрьма...",
            "completed": False
        })
        
        # Локация 6: Тюрьма скорби
        location6_events = cls.generate_location_events(6)
        dungeon.extend(location6_events)
        
        # Переход к локации 7
        dungeon.append({
            "type": "transition",
            "to_location": 7,
            "message": "Слышен шум воды. Подземное озеро...",
            "completed": False
        })
        
        # Локация 7: Грот сирен
        location7_events = cls.generate_location_events(7)
        dungeon.extend(location7_events)
        
        # Добавляем босса
        dungeon.append({
            "type": "boss",
            "location_id": 7,
            "location_name": cls.LOCATIONS[7]["name"],
            "boss": cls.ACT1_BOSS.copy(),
            "area_level": 8,
            "completed": False
        })
        
        return dungeon
