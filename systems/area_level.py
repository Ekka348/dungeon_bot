import random
import math

# ============= СИСТЕМА УРОВНЯ ЛОКАЦИИ =============

class AreaLevelSystem:
    """Система уровня локации (как в Path of Exile)"""
    
    # Таблица уровней локаций для разных актов
    AREA_LEVELS = {
        # Акт 1: Падший (The Fallen)
        1: {
            "name": "Вход в бездну",
            "name_en": "Abyss Entrance",
            "min_level": 1,
            "max_level": 3,
            "monster_level": 1,
            "zone_level": 1,
            "act": 1
        },
        2: {
            "name": "Убежище отчаявшихся",
            "name_en": "Despair's Haven",
            "min_level": 1,
            "max_level": 2,
            "monster_level": 1,
            "zone_level": 1,
            "act": 1,
            "is_safe": True
        },
        3: {
            "name": "Кости катакомб",
            "name_en": "Bone Catacombs",
            "min_level": 2,
            "max_level": 4,
            "monster_level": 3,
            "zone_level": 3,
            "act": 1
        },
        4: {
            "name": "Червивые туннели",
            "name_en": "Worm-eaten Tunnels",
            "min_level": 3,
            "max_level": 5,
            "monster_level": 4,
            "zone_level": 4,
            "act": 1
        },
        5: {
            "name": "Гномьи чертоги",
            "name_en": "Dwarven Halls",
            "min_level": 4,
            "max_level": 6,
            "monster_level": 5,
            "zone_level": 5,
            "act": 1
        },
        6: {
            "name": "Тюрьма скорби",
            "name_en": "Prison of Sorrow",
            "min_level": 5,
            "max_level": 7,
            "monster_level": 6,
            "zone_level": 6,
            "act": 1
        },
        7: {
            "name": "Грот сирен",
            "name_en": "Siren's Grotto",
            "min_level": 6,
            "max_level": 8,
            "monster_level": 8,
            "zone_level": 7,
            "act": 1,
            "has_boss": True
        },
        
        # Акт 2: Пески забвения (Sands of Oblivion)
        8: {
            "name": "Врата пустыни",
            "name_en": "Desert Gates",
            "min_level": 8,
            "max_level": 10,
            "monster_level": 9,
            "zone_level": 9,
            "act": 2
        },
        9: {
            "name": "Оазис",
            "name_en": "Oasis",
            "min_level": 9,
            "max_level": 11,
            "monster_level": 10,
            "zone_level": 10,
            "act": 2,
            "is_safe": True
        },
        10: {
            "name": "Гробницы фараонов",
            "name_en": "Pharaoh's Tombs",
            "min_level": 10,
            "max_level": 12,
            "monster_level": 11,
            "zone_level": 11,
            "act": 2
        },
        11: {
            "name": "Пески времени",
            "name_en": "Sands of Time",
            "min_level": 11,
            "max_level": 13,
            "monster_level": 12,
            "zone_level": 12,
            "act": 2
        },
        12: {
            "name": "Храм солнца",
            "name_en": "Sun Temple",
            "min_level": 12,
            "max_level": 14,
            "monster_level": 13,
            "zone_level": 13,
            "act": 2
        },
        13: {
            "name": "Город призраков",
            "name_en": "Ghost Town",
            "min_level": 13,
            "max_level": 15,
            "monster_level": 14,
            "zone_level": 14,
            "act": 2
        },
        14: {
            "name": "Чертоги Анубиса",
            "name_en": "Halls of Anubis",
            "min_level": 14,
            "max_level": 16,
            "monster_level": 16,
            "zone_level": 15,
            "act": 2,
            "has_boss": True
        }
    }
    
    # Модификаторы уровня для разных редкостей
    RARITY_LEVEL_BONUS = {
        "common": 0,      # Обычные монстры на уровне локации
        "magic": 2,       # Магические на 2 уровня выше
        "rare": 4,        # Редкие на 4 уровня выше
        "boss": 8,        # Боссы на 8 уровней выше
        "unique": 10      # Уникальные на 10 уровней выше
    }
    
    # Модификаторы опыта
    EXPERIENCE_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.5,
        "rare": 2.5,
        "boss": 5.0,
        "unique": 10.0
    }
    
    # Модификаторы здоровья
    HEALTH_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.3,
        "rare": 1.8,
        "boss": 3.0,
        "unique": 5.0
    }
    
    # Модификаторы урона
    DAMAGE_MULTIPLIER = {
        "common": 1.0,
        "magic": 1.2,
        "rare": 1.5,
        "boss": 2.0,
        "unique": 2.5
    }
    
    @classmethod
    def get_area_level(cls, location_id):
        """Получает уровень локации"""
        if location_id in cls.AREA_LEVELS:
            data = cls.AREA_LEVELS[location_id]
            # Можно сделать случайный разброс в пределах min-max
            return random.randint(data["min_level"], data["max_level"])
        return location_id  # fallback
    
    @classmethod
    def get_base_area_level(cls, location_id):
        """Получает базовый уровень локации (без разброса)"""
        if location_id in cls.AREA_LEVELS:
            return cls.AREA_LEVELS[location_id]["zone_level"]
        return location_id
    
    @classmethod
    def get_area_name(cls, location_id):
        """Получает название локации"""
        if location_id in cls.AREA_LEVELS:
            return cls.AREA_LEVELS[location_id]["name"]
        return f"Неизвестная локация {location_id}"
    
    @classmethod
    def get_act_by_location(cls, location_id):
        """Получает акт по локации"""
        if location_id in cls.AREA_LEVELS:
            return cls.AREA_LEVELS[location_id]["act"]
        return 1
    
    @classmethod
    def get_monster_level(cls, area_level, monster_rarity):
        """Рассчитывает уровень монстра на основе уровня локации и редкости"""
        bonus = cls.RARITY_LEVEL_BONUS.get(monster_rarity, 0)
        monster_level = area_level + bonus
        
        # Монстры не могут быть ниже 1 уровня
        return max(1, monster_level)
    
    @classmethod
    def get_monster_stats_multiplier(cls, monster_level, base_level):
        """Получает множитель характеристик монстра"""
        # Разница в уровнях
        level_diff = monster_level - base_level
        
        # Каждый уровень дает +10% к характеристикам
        multiplier = 1.0 + (level_diff * 0.1)
        
        return multiplier
    
    @classmethod
    def scale_monster_stats(cls, base_stats, monster_level, base_level, rarity):
        """Масштабирует характеристики монстра"""
        level_mult = cls.get_monster_stats_multiplier(monster_level, base_level)
        rarity_mult = cls.HEALTH_MULTIPLIER.get(rarity, 1.0)
        
        scaled_stats = {}
        for stat, value in base_stats.items():
            if stat == "hp":
                scaled_stats[stat] = int(value * level_mult * rarity_mult)
            elif stat == "damage":
                if isinstance(value, tuple):
                    min_dmg = int(value[0] * level_mult * rarity_mult)
                    max_dmg = int(value[1] * level_mult * rarity_mult)
                    scaled_stats[stat] = (min_dmg, max_dmg)
                else:
                    scaled_stats[stat] = int(value * level_mult * rarity_mult)
            elif stat in ["accuracy", "defense"]:
                scaled_stats[stat] = int(value * level_mult)
            else:
                scaled_stats[stat] = value
        
        return scaled_stats
    
    @classmethod
    def get_experience_reward(cls, base_exp, monster_level, player_level, rarity):
        """Рассчитывает награду опытом"""
        # Базовая награда с учетом редкости
        exp = base_exp * cls.EXPERIENCE_MULTIPLIER.get(rarity, 1.0)
        
        # Модификатор за разницу в уровнях
        level_diff = monster_level - player_level
        
        if level_diff > 0:
            # Монстр выше уровнем - больше опыта
            exp *= (1.0 + level_diff * 0.2)
        elif level_diff < -5:
            # Монстр слишком низкого уровня - меньше опыта
            exp *= max(0.5, 1.0 + level_diff * 0.1)
        
        return int(exp)
    
    @classmethod
    def get_gold_reward(cls, base_gold, monster_level, area_level, rarity):
        """Рассчитывает награду золотом"""
        # Базовая награда с учетом редкости
        gold = base_gold * cls.EXPERIENCE_MULTIPLIER.get(rarity, 1.0)
        
        # Модификатор за уровень локации
        gold *= (1.0 + area_level * 0.1)
        
        return int(gold)
    
    @classmethod
    def get_item_level(cls, area_level, monster_rarity, monster_level=None):
        """Рассчитывает уровень предмета (item level) для лута"""
        # База - уровень локации
        base_ilvl = area_level
        
        # Бонус за редкость
        rarity_bonus = {
            "common": 0,
            "magic": 2,
            "rare": 5,
            "boss": 10,
            "unique": 15
        }.get(monster_rarity, 0)
        
        # Если есть уровень монстра, используем его
        if monster_level:
            base_ilvl = max(base_ilvl, monster_level)
        
        # Случайный разброс
        variance = random.randint(-1, 2)
        
        ilvl = base_ilvl + rarity_bonus + variance
        return max(1, ilvl)
    
    @classmethod
    def is_safe_zone(cls, location_id):
        """Проверяет, является ли локация безопасной зоной"""
        if location_id in cls.AREA_LEVELS:
            return cls.AREA_LEVELS[location_id].get("is_safe", False)
        return False
    
    @classmethod
    def has_boss(cls, location_id):
        """Проверяет, есть ли в локации босс"""
        if location_id in cls.AREA_LEVELS:
            return cls.AREA_LEVELS[location_id].get("has_boss", False)
        return False
    
    @classmethod
    def get_locations_by_act(cls, act):
        """Получает все локации акта"""
        locations = []
        for loc_id, loc_data in cls.AREA_LEVELS.items():
            if loc_data["act"] == act:
                locations.append((loc_id, loc_data))
        return sorted(locations, key=lambda x: x[0])
    
    @classmethod
    def get_level_range_string(cls, location_id):
        """Получает строку с диапазоном уровней"""
        if location_id in cls.AREA_LEVELS:
            data = cls.AREA_LEVELS[location_id]
            return f"{data['min_level']}-{data['max_level']}"
        return "?"
    
    @classmethod
    def get_area_info_string(cls, location_id):
        """Получает информацию о локации"""
        if location_id not in cls.AREA_LEVELS:
            return "Неизвестная локация"
        
        data = cls.AREA_LEVELS[location_id]
        info = [f"📍 {data['name']}"]
        info.append(f"📊 Уровень: {data['zone_level']} ({data['min_level']}-{data['max_level']})")
        info.append(f"📈 Акт: {data['act']}")
        
        if data.get("is_safe"):
            info.append("🛡️ Безопасная зона")
        if data.get("has_boss"):
            info.append("👑 Есть босс")
        
        return "\n".join(info)


# ============= КЛАСС ДЛЯ ЛОКАЦИИ =============

class Area:
    """Класс локации"""
    
    def __init__(self, location_id):
        self.id = location_id
        self.data = AreaLevelSystem.AREA_LEVELS.get(location_id, {})
        self.current_level = AreaLevelSystem.get_area_level(location_id)
        
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
    
    def get_monster_level(self, rarity="common"):
        """Получает уровень монстра в этой локации"""
        return AreaLevelSystem.get_monster_level(self.current_level, rarity)
    
    def get_item_level(self, rarity="common", monster_level=None):
        """Получает уровень предмета для лута"""
        return AreaLevelSystem.get_item_level(self.current_level, rarity, monster_level)
    
    def get_info(self):
        """Получает информацию о локации"""
        return AreaLevelSystem.get_area_info_string(self.id)


# ============= КЛАСС ДЛЯ РАСЧЕТА СЛОЖНОСТИ =============

class DifficultyCalculator:
    """Калькулятор сложности"""
    
    def __init__(self, player_level, area_level):
        self.player_level = player_level
        self.area_level = area_level
        self.level_diff = area_level - player_level
    
    def get_difficulty_tier(self):
        """Получает уровень сложности"""
        if self.level_diff <= -5:
            return "trivial", 0.3  # Очень легко
        elif self.level_diff <= -2:
            return "easy", 0.6      # Легко
        elif self.level_diff <= 0:
            return "normal", 1.0    # Нормально
        elif self.level_diff <= 2:
            return "hard", 1.5      # Сложно
        elif self.level_diff <= 5:
            return "very_hard", 2.0 # Очень сложно
        else:
            return "deadly", 3.0    # Смертельно
    
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
            # Игрок наносит меньше урона сильным врагам
            if self.level_diff > 0:
                return max(0.5, 1.0 - self.level_diff * 0.1)
            else:
                return min(1.5, 1.0 + abs(self.level_diff) * 0.1)
        else:
            # Враг наносит больше урона слабым игрокам
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


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_area_level_system():
    """Тест системы уровня локации"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМЫ УРОВНЯ ЛОКАЦИИ")
    print("=" * 50)
    
    # Тест получения уровня локации
    print("\n🔹 Уровни локаций:")
    for loc_id in [1, 3, 5, 7]:
        area_level = AreaLevelSystem.get_area_level(loc_id)
        name = AreaLevelSystem.get_area_name(loc_id)
        print(f"  {name}: {area_level}")
    
    # Тест уровня монстров
    print("\n🔹 Уровни монстров (локация 5, ур. 5):")
    for rarity in ["common", "magic", "rare", "boss"]:
        monster_level = AreaLevelSystem.get_monster_level(5, rarity)
        print(f"  {rarity}: {monster_level}")
    
    # Тест уровня предметов
    print("\n🔹 Уровни предметов (локация 7, ур. 8):")
    for rarity in ["common", "magic", "rare", "boss", "unique"]:
        item_level = AreaLevelSystem.get_item_level(8, rarity)
        print(f"  {rarity}: {item_level}")
    
    # Тест масштабирования
    print("\n🔹 Масштабирование монстра (базовый ур. 3):")
    base_stats = {
        "hp": 50,
        "damage": (5, 10),
        "accuracy": 70,
        "defense": 5
    }
    
    for rarity in ["common", "magic", "rare", "boss"]:
        monster_level = AreaLevelSystem.get_monster_level(5, rarity)
        scaled = AreaLevelSystem.scale_monster_stats(base_stats, monster_level, 3, rarity)
        print(f"\n  {rarity} (ур. {monster_level}):")
        print(f"    HP: {scaled['hp']}")
        print(f"    Урон: {scaled['damage']}")
        print(f"    Защита: {scaled['defense']}")


def test_difficulty_calculator():
    """Тест калькулятора сложности"""
    print("=" * 50)
    print("ТЕСТ КАЛЬКУЛЯТОРА СЛОЖНОСТИ")
    print("=" * 50)
    
    test_cases = [
        (10, 5),   # Игрок выше на 5
        (10, 8),   # Игрок выше на 2
        (10, 10),  # Равны
        (10, 12),  # Игрок ниже на 2
        (10, 15),  # Игрок ниже на 5
        (10, 18),  # Игрок ниже на 8
    ]
    
    for player_level, area_level in test_cases:
        print(f"\n🔸 Игрок {player_level} vs Локация {area_level}")
        calc = DifficultyCalculator(player_level, area_level)
        
        diff_name = calc.get_difficulty_name()
        exp_mult = calc.get_exp_multiplier()
        player_damage_mult = calc.get_damage_multiplier(is_player=True)
        enemy_damage_mult = calc.get_damage_multiplier(is_player=False)
        
        print(f"  Сложность: {diff_name}")
        print(f"  Множитель опыта: x{exp_mult:.1f}")
        print(f"  Урон игрока: x{player_damage_mult:.1f}")
        print(f"  Урон врага: x{enemy_damage_mult:.1f}")


def test_experience_calculation():
    """Тест расчета опыта"""
    print("=" * 50)
    print("ТЕСТ РАСЧЕТА ОПЫТА")
    print("=" * 50)
    
    base_exp = 100
    
    for player_level in [5, 10, 15]:
        print(f"\n🔸 Игрок уровень {player_level}:")
        print("-" * 30)
        
        for monster_level in [5, 8, 10, 12, 15, 20]:
            for rarity in ["common", "magic", "rare", "boss"]:
                exp = AreaLevelSystem.get_experience_reward(base_exp, monster_level, player_level, rarity)
                if exp > 0:
                    print(f"  Монстр ур.{monster_level} ({rarity}): {exp} опыта")


if __name__ == "__main__":
    test_area_level_system()
    print("\n")
    test_difficulty_calculator()
    print("\n")
    test_experience_calculation()
