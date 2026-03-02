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
        11: {
            "id": 11,
            "name": "Пески времени",
            "name_en": "Sands of Time",
            "description": "Бескрайние пески, где время течет иначе.",
            "act": 2,
            "min_level": 11,
            "max_level": 13,
            "zone_level": 12,
            "next_location": 12,
            "biome": "desert",
            "monster_density": 0.75,
            "event_density": 0.25,
            "min_events": 18,
            "max_events": 22
        },
        12: {
            "id": 12,
            "name": "Храм солнца",
            "name_en": "Sun Temple",
            "description": "Древний храм, посвященный богу солнца.",
            "act": 2,
            "min_level": 12,
            "max_level": 14,
            "zone_level": 13,
            "next_location": 13,
            "biome": "temple",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 20,
            "max_events": 25
        },
        13: {
            "id": 13,
            "name": "Город призраков",
            "name_en": "Ghost Town",
            "description": "Заброшенный город, населенный призраками.",
            "act": 2,
            "min_level": 13,
            "max_level": 15,
            "zone_level": 14,
            "next_location": 14,
            "biome": "ruins",
            "monster_density": 0.8,
            "event_density": 0.2,
            "min_events": 20,
            "max_events": 25
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
    
    @classmethod
    def get_next_location(cls, location_id):
        """Получает следующую локацию"""
        location = cls.get_location(location_id)
        if location and location.get("next_location"):
            return cls.get_location(location["next_location"])
        return None
    
    @classmethod
    def get_min_events(cls, location_id):
        """Получает минимальное количество событий"""
        location = cls.get_location(location_id)
        return location.get("min_events", 10) if location else 10
    
    @classmethod
    def get_max_events(cls, location_id):
        """Получает максимальное количество событий"""
        location = cls.get_location(location_id)
        return location.get("max_events", 15) if location else 15
    
    @classmethod
    def get_monster_density(cls, location_id):
        """Получает плотность монстров"""
        location = cls.get_location(location_id)
        return location.get("monster_density", 0.7) if location else 0.7
    
    @classmethod
    def get_event_density(cls, location_id):
        """Получает плотность событий"""
        location = cls.get_location(location_id)
        return location.get("event_density", 0.3) if location else 0.3


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
    
    DAMAGE_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.2,
        "rare": 1.5,
        "boss": 2.0,
        "unique": 2.5
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
    
    @classmethod
    def get_experience_reward(cls, base_exp, monster_level, player_level, rarity):
        """Рассчитывает награду опытом"""
        exp = base_exp * cls.EXPERIENCE_MULTIPLIER.get(rarity, 1.0)
        
        level_diff = monster_level - player_level
        
        if level_diff > 0:
            exp *= (1.0 + level_diff * 0.2)
        elif level_diff < -5:
            exp *= max(0.5, 1.0 + level_diff * 0.1)
        
        return int(exp)
    
    @classmethod
    def get_gold_reward(cls, base_gold, monster_level, area_level, rarity):
        """Рассчитывает награду золотом"""
        gold = base_gold * cls.EXPERIENCE_MULTIPLIER.get(rarity, 1.0)
        gold *= (1.0 + area_level * 0.1)
        return int(gold)
    
    @classmethod
    def scale_monster_stats(cls, base_stats, monster_level, base_level, rarity):
        """Масштабирует характеристики монстра"""
        level_diff = monster_level - base_level
        level_mult = 1.0 + (level_diff * 0.1)
        rarity_mult = cls.HEALTH_MULTIPLIER.get(rarity, 1.0)
        damage_mult = cls.DAMAGE_MULTIPLIER.get(rarity, 1.0)
        
        scaled_stats = {}
        for stat, value in base_stats.items():
            if stat == "base_hp" or stat == "hp":
                scaled_stats[stat] = int(value * level_mult * rarity_mult)
            elif stat == "damage" or stat == "damage_range":
                if isinstance(value, tuple):
                    min_dmg = int(value[0] * level_mult * damage_mult)
                    max_dmg = int(value[1] * level_mult * damage_mult)
                    scaled_stats[stat] = (min_dmg, max_dmg)
                else:
                    scaled_stats[stat] = int(value * level_mult * damage_mult)
            elif stat in ["accuracy", "defense"]:
                scaled_stats[stat] = int(value * level_mult)
            else:
                scaled_stats[stat] = value
        
        return scaled_stats


# ============= КЛАСС ЛОКАЦИИ =============

class Area:
    """Класс локации"""
    
    def __init__(self, location_id):
        self.id = location_id
        self.data = AreaRegistry.get_location(location_id) or {}
        self.current_level = AreaRegistry.get_area_level(location_id)
    
    @property
    def name(self):
        return self.data.get("name", "Неизвестная локация")
    
    @property
    def name_en(self):
        return self.data.get("name_en", "Unknown")
    
    @property
    def act(self):
        return self.data.get("act", 1)
    
    @property
    def min_level(self):
        return self.data.get("min_level", 1)
    
    @property
    def max_level(self):
        return self.data.get("max_level", 1)
    
    @property
    def zone_level(self):
        return self.data.get("zone_level", 1)
    
    @property
    def is_safe(self):
        return self.data.get("is_safe", False)
    
    @property
    def has_boss(self):
        return self.data.get("has_boss", False)
    
    @property
    def next_location(self):
        return self.data.get("next_location")
    
    @property
    def monster_density(self):
        return self.data.get("monster_density", 0.7)
    
    @property
    def event_density(self):
        return self.data.get("event_density", 0.3)
    
    @property
    def min_events(self):
        return self.data.get("min_events", 10)
    
    @property
    def max_events(self):
        return self.data.get("max_events", 15)
    
    def get_monster_level(self, rarity="common"):
        """Получает уровень монстра в этой локации"""
        return MonsterLevelSystem.get_monster_level(self.current_level, rarity)
    
    def get_item_level(self, rarity="common", monster_level=None):
        """Получает уровень предмета для лута"""
        return MonsterLevelSystem.get_item_level(self.current_level, rarity, monster_level)
    
    def get_info(self):
        """Получает информацию о локации"""
        info = [f"📍 {self.name}"]
        info.append(f"📊 Уровень: {self.current_level} ({self.min_level}-{self.max_level})")
        info.append(f"📈 Акт: {self.act}")
        
        if self.is_safe:
            info.append("🛡️ Безопасная зона")
        if self.has_boss:
            info.append("👑 Есть босс")
        
        return "\n".join(info)


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
    
    def get_exp_multiplier(self):
        """Получает множитель опыта"""
        _, mult = self.get_difficulty_tier()
        return mult
    
    def get_damage_multiplier(self, is_player=True):
        """Получает множитель урона"""
        if is_player:
            if self.level_diff > 0:
                return max(0.5, 1.0 - self.level_diff * 0.1)
            else:
                return min(1.5, 1.0 + abs(self.level_diff) * 0.1)
        else:
            if self.level_diff > 0:
                return 1.0 + self.level_diff * 0.1
            else:
                return max(0.5, 1.0 + self.level_diff * 0.05)
    
    def get_defense_multiplier(self):
        """Получает множитель защиты"""
        if self.level_diff > 0:
            return max(0.5, 1.0 - self.level_diff * 0.05)
        else:
            return min(1.5, 1.0 + abs(self.level_diff) * 0.1)


# ============= ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ =============

class AreaLevelSystem:
    """Устаревший класс для обратной совместимости"""
    
    AREA_LEVELS = AreaRegistry.LOCATIONS
    
    @classmethod
    def get_area_level(cls, location_id):
        return AreaRegistry.get_area_level(location_id)
    
    @classmethod
    def get_base_area_level(cls, location_id):
        return AreaRegistry.get_base_area_level(location_id)
    
    @classmethod
    def get_area_name(cls, location_id):
        return AreaRegistry.get_location_name(location_id)
    
    @classmethod
    def get_act_by_location(cls, location_id):
        return AreaRegistry.get_act_by_location(location_id)
    
    @classmethod
    def get_monster_level(cls, area_level, monster_rarity):
        return MonsterLevelSystem.get_monster_level(area_level, monster_rarity)
    
    @classmethod
    def get_item_level(cls, area_level, monster_rarity, monster_level=None):
        return MonsterLevelSystem.get_item_level(area_level, monster_rarity, monster_level)
    
    @classmethod
    def get_experience_reward(cls, base_exp, monster_level, player_level, rarity):
        return MonsterLevelSystem.get_experience_reward(base_exp, monster_level, player_level, rarity)
    
    @classmethod
    def get_gold_reward(cls, base_gold, monster_level, area_level, rarity):
        return MonsterLevelSystem.get_gold_reward(base_gold, monster_level, area_level, rarity)
    
    @classmethod
    def scale_monster_stats(cls, base_stats, monster_level, base_level, rarity):
        return MonsterLevelSystem.scale_monster_stats(base_stats, monster_level, base_level, rarity)
    
    @classmethod
    def is_safe_zone(cls, location_id):
        return AreaRegistry.is_safe_zone(location_id)
    
    @classmethod
    def has_boss(cls, location_id):
        return AreaRegistry.has_boss(location_id)
    
    @classmethod
    def get_locations_by_act(cls, act):
        return AreaRegistry.get_locations_by_act(act)


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_area_level_system():
    """Тест системы"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМЫ УРОВНЯ ЛОКАЦИИ")
    print("=" * 50)
    
    for loc_id in [1, 3, 5, 7]:
        area_level = AreaRegistry.get_area_level(loc_id)
        name = AreaRegistry.get_location_name(loc_id)
        print(f"  {name}: {area_level}")
    
    print("\n🔹 Уровни монстров:")
    for rarity in ["common", "magic", "rare", "boss"]:
        monster_level = MonsterLevelSystem.get_monster_level(5, rarity)
        print(f"  {rarity}: {monster_level}")
    
    print("\n🔹 Масштабирование монстра:")
    base_stats = {
        "base_hp": 50,
        "damage": (5, 10),
        "accuracy": 70,
        "defense": 5
    }
    
    scaled = MonsterLevelSystem.scale_monster_stats(base_stats, 8, 5, "rare")
    print(f"  Редкий монстр (ур.8): HP {scaled['base_hp']}, урон {scaled['damage']}")


if __name__ == "__main__":
    test_area_level_system()
