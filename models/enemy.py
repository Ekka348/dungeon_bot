import random
from data.act1 import Act1
from systems.area_level import MonsterLevelSystem

# ============= МОДЕЛЬ ВРАГА =============

class Enemy:
    """Класс врага"""
    
    def __init__(self, name, base_hp, damage_range, accuracy, defense, base_exp, emoji, rarity="common", 
                 area_level=1, image_path=None, description=""):
        self.name = name
        self.rarity = rarity
        self.area_level = area_level
        self.emoji = emoji
        self.image_path = image_path
        self.description = description
        
        # Базовые характеристики
        self.base_hp = base_hp
        self.damage_range = damage_range
        self.base_accuracy = accuracy
        self.base_defense = defense
        self.base_exp = base_exp
        
        # Масштабирование в зависимости от уровня локации и редкости
        self._scale_stats()
        
        # Текущее состояние
        self.hp = self.max_hp
        self.max_hp = self.max_hp
        
        # Уровень монстра
        self.monster_level = self._calculate_monster_level()
        
        # Модификаторы для редких врагов
        self.modifiers = []
        self._add_rarity_modifiers()
        
        # Временные эффекты
        self.buffs = []
        self.debuffs = []
        
        # Статистика боя
        self.turns_taken = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        
        # Награды
        self.gold_min = int(base_exp * 0.5)
        self.gold_max = int(base_exp * 1.5)
    
    def _scale_stats(self):
        """Масштабирует характеристики"""
        # Базовый множитель от уровня локации
        level_mult = 1 + (self.area_level - 1) * 0.15
        
        # Множитель от редкости
        rarity_mult = {
            "common": 1.0,
            "magic": 1.3,
            "rare": 1.8,
            "boss": 3.0
        }.get(self.rarity, 1.0)
        
        damage_mult = {
            "common": 1.0,
            "magic": 1.2,
            "rare": 1.5,
            "boss": 2.0
        }.get(self.rarity, 1.0)
        
        # Итоговый множитель
        total_mult = level_mult * rarity_mult
        damage_total_mult = level_mult * damage_mult
        
        # Масштабируем характеристики
        self.max_hp = int(self.base_hp * total_mult)
        self.damage_min = int(self.damage_range[0] * damage_total_mult)
        self.damage_max = int(self.damage_range[1] * damage_total_mult)
        self.accuracy = min(95, int(self.base_accuracy * (1 + (self.area_level - 1) * 0.02)))
        self.defense = int(self.base_defense * (1 + (self.area_level - 1) * 0.1))
        self.exp_reward = int(self.base_exp * total_mult)
        
        self.gold_min = int(self.base_exp * 0.5 * total_mult)
        self.gold_max = int(self.base_exp * 1.5 * total_mult)
    
    def _calculate_monster_level(self):
        """Рассчитывает уровень монстра"""
        return MonsterLevelSystem.get_monster_level(self.area_level, self.rarity)
    
    def _add_rarity_modifiers(self):
        """Добавляет модификаторы в зависимости от редкости"""
        if self.rarity == "magic":
            self.modifiers.append(self._get_random_modifier())
        elif self.rarity == "rare":
            num_mods = random.randint(2, 3)
            for _ in range(num_mods):
                self.modifiers.append(self._get_random_modifier())
        elif self.rarity == "boss":
            num_mods = random.randint(3, 4)
            for _ in range(num_mods):
                self.modifiers.append(self._get_random_modifier())
    
    def _get_random_modifier(self):
        """Возвращает случайный модификатор"""
        modifiers = [
            {
                "name": "Крепкий",
                "effect": "hp_mult",
                "value": 1.5,
                "description": "Увеличенное здоровье"
            },
            {
                "name": "Сильный",
                "effect": "damage_mult",
                "value": 1.3,
                "description": "Увеличенный урон"
            },
            {
                "name": "Бронированный",
                "effect": "defense_mult",
                "value": 2.0,
                "description": "Увеличенная защита"
            },
            {
                "name": "Меткий",
                "effect": "accuracy_bonus",
                "value": 15,
                "description": "Повышенная точность"
            },
            {
                "name": "Быстрый",
                "effect": "speed_mult",
                "value": 1.3,
                "description": "Увеличенная скорость атаки"
            },
            {
                "name": "Ядовитый",
                "effect": "poison",
                "value": 3,
                "description": "Атаки отравляют цель"
            }
        ]
        return random.choice(modifiers)
    
    # ============= БОЕВЫЕ МЕТОДЫ =============
    
    def attack(self):
        """Выполняет атаку"""
        damage = random.randint(self.damage_min, self.damage_max)
        
        for mod in self.modifiers:
            if mod["effect"] == "damage_mult":
                damage = int(damage * mod["value"])
        
        self.turns_taken += 1
        self.damage_dealt += damage
        return damage
    
    def take_damage(self, damage):
        """Получает урон"""
        # Учитываем защиту
        reduced_damage = max(1, damage - self.defense // 3)
        
        self.hp -= reduced_damage
        self.damage_taken += reduced_damage
        
        if self.hp < 0:
            self.hp = 0
        
        return reduced_damage
    
    def is_alive(self):
        """Проверяет, жив ли враг"""
        return self.hp > 0
    
    def get_hp_percent(self):
        """Возвращает процент здоровья"""
        return int((self.hp / self.max_hp) * 100)
    
    def get_hp_bar(self, length=10):
        """Возвращает визуальную полоску здоровья"""
        filled = int((self.hp / self.max_hp) * length)
        bar = "█" * filled + "░" * (length - filled)
        
        hp_percent = self.get_hp_percent()
        if hp_percent > 66:
            color = "🟢"
        elif hp_percent > 33:
            color = "🟡"
        else:
            color = "🔴"
        
        return f"{color} {bar} {self.hp}/{self.max_hp}"
    
    # ============= МЕТОДЫ ДЛЯ МОДИФИКАТОРОВ =============
    
    def get_modifiers_string(self):
        """Возвращает строку с модификаторами"""
        if not self.modifiers:
            return ""
        
        mod_emojis = {
            "hp_mult": "❤️",
            "damage_mult": "⚔️",
            "defense_mult": "🛡️",
            "accuracy_bonus": "🎯",
            "speed_mult": "⚡",
            "poison": "☠️",
        }
        
        mods = []
        for mod in self.modifiers:
            emoji = mod_emojis.get(mod["effect"], "✨")
            mods.append(f"{emoji} {mod['name']}")
        
        return " | ".join(mods)
    
    def get_rarity_color(self):
        """Возвращает цвет редкости"""
        colors = {
            "common": "🟢",
            "magic": "🟣",
            "rare": "🟡",
            "boss": "⚫"
        }
        return colors.get(self.rarity, "⚪")
    
    def get_rarity_name(self):
        """Возвращает название редкости"""
        names = {
            "common": "Обычный",
            "magic": "Магический",
            "rare": "Редкий",
            "boss": "БОСС"
        }
        return names.get(self.rarity, "Обычный")
    
    # ============= МЕТОДЫ НАГРАД =============
    
    def get_gold_reward(self):
        """Возвращает случайное количество золота"""
        return MonsterLevelSystem.get_gold_reward(
            self.base_exp, self.monster_level, self.area_level, self.rarity
        )
    
    def get_exp_reward(self):
        """Возвращает награду опытом"""
        return MonsterLevelSystem.get_experience_reward(
            self.base_exp, self.monster_level, 1, self.rarity
        )
    
    # ============= МЕТОДЫ СОЗДАНИЯ =============
    
    @classmethod
    def from_monster_data(cls, monster_data, area_level, rarity="common"):
        """Создает врага из данных монстра"""
        return cls(
            name=monster_data["name"],
            base_hp=monster_data["base_hp"],
            damage_range=monster_data["damage"],
            accuracy=monster_data["accuracy"],
            defense=monster_data["defense"],
            base_exp=monster_data["base_exp"],
            emoji=monster_data["emoji"],
            rarity=rarity,
            area_level=area_level,
            image_path=monster_data.get("image"),
            description=monster_data.get("description", "")
        )
    
    @classmethod
    def from_location(cls, location_id, area_level, rarity=None):
        """Создает случайного врага из локации"""
        if rarity is None:
            roll = random.random()
            if roll < 0.7:
                rarity = "common"
            elif roll < 0.95:
                rarity = "magic"
            else:
                rarity = "rare"
        
        monster_data = Act1.get_random_monster(location_id, rarity)
        if not monster_data:
            return None
        
        return cls.from_monster_data(monster_data, area_level, rarity)
    
    @classmethod
    def create_boss(cls, boss_data, area_level=8):
        """Создает босса"""
        return cls(
            name=boss_data["name"],
            base_hp=boss_data["base_hp"],
            damage_range=boss_data["damage"],
            accuracy=boss_data["accuracy"],
            defense=boss_data["defense"],
            base_exp=boss_data["base_exp"],
            emoji=boss_data["emoji"],
            rarity="boss",
            area_level=area_level,
            image_path=boss_data.get("image"),
            description=boss_data.get("description", "")
        )
    
    # ============= МЕТОДЫ ОТОБРАЖЕНИЯ =============
    
    def get_battle_string(self):
        """Возвращает строку для отображения в бою"""
        text = (
            f"{self.emoji} **{self.name}** {self.get_rarity_color()}\n"
            f"{self.get_hp_bar()}\n"
        )
        
        if self.modifiers:
            text += f"\n✨ {self.get_modifiers_string()}\n"
        
        if self.description and self.rarity in ["rare", "boss"]:
            text += f"\n_{self.description}_\n"
        
        return text
    
    def get_stats_string(self):
        """Возвращает полную статистику врага"""
        text = (
            f"📊 **{self.name}** {self.get_rarity_color()}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"❤️ HP: {self.hp}/{self.max_hp}\n"
            f"⚔️ Урон: {self.damage_min}-{self.damage_max}\n"
            f"🎯 Точность: {self.accuracy}%\n"
            f"🛡️ Защита: {self.defense}\n"
            f"✨ Редкость: {self.get_rarity_name()}\n"
            f"📈 Уровень: {self.area_level}\n"
        )
        
        if self.modifiers:
            text += f"\n✨ **Модификаторы:**\n"
            for mod in self.modifiers:
                text += f"  • {mod['name']}: {mod['description']}\n"
        
        return text
    
    def get_brief_string(self):
        """Возвращает краткую информацию о враге"""
        hp_percent = self.get_hp_percent()
        hp_indicator = "🟢" if hp_percent > 66 else "🟡" if hp_percent > 33 else "🔴"
        
        return f"{self.emoji} {self.name} {self.get_rarity_color()} {hp_indicator} {self.hp}/{self.max_hp}"
