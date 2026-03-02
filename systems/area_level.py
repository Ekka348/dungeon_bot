import random

# ============= ЕДИНЫЙ РЕЕСТР ЛОКАЦИЙ =============

class AreaRegistry:
    """Единый реестр всех локаций игры"""
    
    LOCATIONS = {
        # Акт 1: Падший (The Fallen) - ID 1-7
        1: {
            "id": 1,
            "name": "Вход в бездну",
            "name_en": "Abyss Entrance",
            "description": "Тебя сбросили в темницу за преступления, которых ты не совершал. Холодный камень встречает твое падение.",
            "act": 1,
            "min_level": 1,
            "max_level": 3,
            "zone_level": 1,
            "next_location": 2,
            "biome": "dungeon_entrance",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 8,
            "max_events": 12
        },
        2: {
            "id": 2,
            "name": "Убежище отчаявшихся",
            "name_en": "Despair's Haven",
            "description": "Среди тьмы ты находишь импровизированное убежище. Здесь живут такие же отверженные, как и ты.",
            "act": 1,
            "min_level": 1,
            "max_level": 2,
            "zone_level": 1,
            "next_location": 3,
            "biome": "safe_haven",
            "is_safe": True
        },
        3: {
            "id": 3,
            "name": "Кости катакомб",
            "name_en": "Bone Catacombs",
            "description": "Древние захоронения, где покоятся те, кто умер в этих темницах.",
            "act": 1,
            "min_level": 2,
            "max_level": 4,
            "zone_level": 3,
            "next_location": 4,
            "biome": "catacombs",
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 12,
            "max_events": 16
        },
        4: {
            "id": 4,
            "name": "Червивые туннели",
            "name_en": "Worm-eaten Tunnels",
            "description": "Огромные ходы, прорытые гигантскими существами. Стены пульсируют, словно живые.",
            "act": 1,
            "min_level": 3,
            "max_level": 5,
            "zone_level": 4,
            "next_location": 5,
            "biome": "worm_tunnels",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 12,
            "max_events": 16
        },
        5: {
            "id": 5,
            "name": "Гномьи чертоги",
            "name_en": "Dwarven Halls",
            "description": "Забытые залы древних гномов. Механизмы все еще работают, создавая жуткий скрежет.",
            "act": 1,
            "min_level": 4,
            "max_level": 6,
            "zone_level": 5,
            "next_location": 6,
            "biome": "dwarven_halls",
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 14,
            "max_events": 18
        },
        6: {
            "id": 6,
            "name": "Тюрьма скорби",
            "name_en": "Prison of Sorrow",
            "description": "Главная тюрьма подземелья. Камеры переполнены обезумевшими заключенными.",
            "act": 1,
            "min_level": 5,
            "max_level": 7,
            "zone_level": 6,
            "next_location": 7,
            "biome": "prison",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 16,
            "max_events": 20
        },
        7: {
            "id": 7,
            "name": "Грот сирен",
            "name_en": "Siren's Grotto",
            "description": "Подземное озеро, освещенное биолюминесценцией. Сирены поют свои жуткие песни.",
            "act": 1,
            "min_level": 6,
            "max_level": 8,
            "zone_level": 7,
            "next_location": None,
            "biome": "grotto",
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 16,
            "max_events": 20,
            "has_boss": True
        },
        
        # Акт 2: Пески забвения (Sands of Oblivion) - ID 8-14
        8: {
            "id": 8,
            "name": "Врата пустыни",
            "name_en": "Desert Gates",
            "description": "Ты выходишь из подземелья и попадаешь в бескрайнюю пустыню. Ворота в пески забвения.",
            "act": 2,
            "min_level": 8,
            "max_level": 10,
            "zone_level": 9,
            "next_location": 9,
            "biome": "desert",
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 15,
            "max_events": 20
        },
        9: {
            "id": 9,
            "name": "Оазис",
            "name_en": "Oasis",
            "description": "Среди песков ты находишь оазис с чистой водой и пальмами.",
            "act": 2,
            "min_level": 9,
            "max_level": 11,
            "zone_level": 10,
            "next_location": 10,
            "biome": "oasis",
            "is_safe": True
        },
        10: {
            "id": 10,
            "name": "Гробницы фараонов",
            "name_en": "Pharaoh's Tombs",
            "description": "Древние гробницы, полные ловушек и проклятий. Мумии оживают, чтобы защитить свои сокровища.",
            "act": 2,
            "min_level": 10,
            "max_level": 12,
            "zone_level": 11,
            "next_location": 11,
            "biome": "tombs",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 18,
            "max_events": 24
        },
        14: {
            "id": 14,
            "name": "Чертоги Анубиса",
            "name_en": "Halls of Anubis",
            "description": "Святилище Анубиса, где тебя ждет Повелитель песков.",
            "act": 2,
            "min_level": 14,
            "max_level": 16,
            "zone_level": 15,
            "next_location": None,
            "biome": "temple",
            "monster_density": 0.7,
            "event_density": 0.3,
            "min_events": 20,
            "max_events": 25,
            "has_boss": True
        }
    }
    
    # Монстры для каждой локации (оставляем как в Act1, но добавляем в реестр)
    LOCATION_MONSTERS = {}
    
    @classmethod
    def get_location(cls, location_id):
        """Безопасно получает локацию по ID"""
        return cls.LOCATIONS.get(location_id)
    
    @classmethod
    def get_location_name(cls, location_id):
        """Безопасно получает название локации"""
        location = cls.get_location(location_id)
        return location["name"] if location else "Неизвестная локация"
    
    @classmethod
    def get_location_description(cls, location_id):
        """Безопасно получает описание локации"""
        location = cls.get_location(location_id)
        return location["description"] if location else "Описание отсутствует"
    
    @classmethod
    def get_act_by_location(cls, location_id):
        """Получает акт по локации"""
        location = cls.get_location(location_id)
        return location["act"] if location else 1
    
    @classmethod
    def get_area_level(cls, location_id):
        """Получает текущий уровень локации (со случайным разбросом)"""
        location = cls.get_location(location_id)
        if not location:
            return 1
        return random.randint(location["min_level"], location["max_level"])
    
    @classmethod
    def get_base_area_level(cls, location_id):
        """Получает базовый уровень локации"""
        location = cls.get_location(location_id)
        return location["zone_level"] if location else 1
    
    @classmethod
    def get_locations_by_act(cls, act):
        """Получает все локации акта"""
        return [(loc_id, loc_data) for loc_id, loc_data in cls.LOCATIONS.items() 
                if loc_data["act"] == act]
    
    @classmethod
    def is_safe_zone(cls, location_id):
        """Проверяет, является ли локация безопасной зоной"""
        location = cls.get_location(location_id)
        return location.get("is_safe", False) if location else False
    
    @classmethod
    def has_boss(cls, location_id):
        """Проверяет, есть ли в локации босс"""
        location = cls.get_location(location_id)
        return location.get("has_boss", False) if location else False


# ============= СИСТЕМА УРОВНЯ МОНСТРОВ =============

class MonsterLevelSystem:
    """Система уровня монстров"""
    
    RARITY_LEVEL_BONUS = {
        "common": 0,
        "magic": 2,
        "rare": 4,
        "boss": 8,
        "unique": 10
    }
    
    EXPERIENCE_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.5,
        "rare": 2.5,
        "boss": 5.0,
        "unique": 10.0
    }
    
    HEALTH_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.3,
        "rare": 1.8,
        "boss": 3.0,
        "unique": 5.0
    }
    
    @classmethod
    def get_monster_level(cls, area_level, monster_rarity):
        """Рассчитывает уровень монстра"""
        bonus = cls.RARITY_LEVEL_BONUS.get(monster_rarity, 0)
        return max(1, area_level + bonus)
    
    @classmethod
    def get_item_level(cls, area_level, monster_rarity, monster_level=None):
        """Рассчитывает уровень предмета"""
        base_ilvl = area_level
        rarity_bonus = {
            "common": 0,
            "magic": 2,
            "rare": 5,
            "boss": 10,
            "unique": 15
        }.get(monster_rarity, 0)
        
        if monster_level:
            base_ilvl = max(base_ilvl, monster_level)
        
        variance = random.randint(-1, 2)
        return max(1, base_ilvl + rarity_bonus + variance)


# ============= КАЛЬКУЛЯТОР СЛОЖНОСТИ =============

class DifficultyCalculator:
    """Калькулятор сложности на основе разницы уровней"""
    
    def __init__(self, player_level, area_level):
        self.player_level = player_level
        self.area_level = area_level
        self.level_diff = area_level - player_level
    
    def get_difficulty_tier(self):
        """Получает уровень сложности"""
        if self.level_diff <= -5:
            return "trivial", 0.3
        elif self.level_diff <= -2:
            return "easy", 0.6
        elif self.level_diff <= 0:
            return "normal", 1.0
        elif self.level_diff <= 2:
            return "hard", 1.5
        elif self.level_diff <= 5:
            return "very_hard", 2.0
        else:
            return "deadly", 3.0
    
    def get_difficulty_name(self):
        """Получает название сложности"""
        tier, _ = self.get_difficulty_tier()
        names = {
            "trivial": "🟢 Тривиально",
            "easy": "🟢 Легко",
            "normal": "🟡 Нормально",
            "hard": "🟠 Сложно",
            "very_hard": "🔴 Очень сложно",
            "deadly": "💀 Смертельно"
        }
        return names.get(tier, "🟡 Нормально")
