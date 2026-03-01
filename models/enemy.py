import random
from data.act1 import Act1

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
        self.max_hp = self.hp
        
        # Модификаторы для редких врагов
        self.modifiers = []
        self._add_rarity_modifiers()
        
        # Временные эффекты
        self.buffs = []  # [(name, duration, effect)]
        self.debuffs = []  # [(name, duration, effect)]
        
        # Статистика боя
        self.turns_taken = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        
        # Награды (кроме опыта)
        self.gold_min = int(base_exp * 0.5)
        self.gold_max = int(base_exp * 1.5)
    
    def _scale_stats(self):
        """Масштабирует характеристики в зависимости от уровня локации и редкости"""
        # Базовый множитель от уровня локации
        level_mult = 1 + (self.area_level - 1) * 0.15  # +15% за уровень
        
        # Множитель от редкости
        rarity_mult = {
            "common": 1.0,
            "magic": 1.3,
            "rare": 1.8,
            "boss": 3.0
        }.get(self.rarity, 1.0)
        
        # Итоговый множитель
        total_mult = level_mult * rarity_mult
        
        # Масштабируем характеристики
        self.max_hp = int(self.base_hp * total_mult)
        self.damage_min = int(self.damage_range[0] * total_mult)
        self.damage_max = int(self.damage_range[1] * total_mult)
        self.accuracy = min(95, int(self.base_accuracy * (1 + (self.area_level - 1) * 0.02)))
        self.defense = int(self.base_defense * (1 + (self.area_level - 1) * 0.1))
        self.exp_reward = int(self.base_exp * total_mult)
        
        # Золото тоже масштабируется
        self.gold_min = int(self.base_exp * 0.5 * total_mult)
        self.gold_max = int(self.base_exp * 1.5 * total_mult)
    
    def _add_rarity_modifiers(self):
        """Добавляет модификаторы в зависимости от редкости"""
        if self.rarity == "magic":
            # Магические враги получают один случайный модификатор
            self.modifiers.append(self._get_random_modifier())
        elif self.rarity == "rare":
            # Редкие враги получают 2-3 модификатора
            num_mods = random.randint(2, 3)
            for _ in range(num_mods):
                self.modifiers.append(self._get_random_modifier())
        elif self.rarity == "boss":
            # Боссы получают 3-4 модификатора и особые способности
            num_mods = random.randint(3, 4)
            for _ in range(num_mods):
                self.modifiers.append(self._get_random_modifier())
    
    def _get_random_modifier(self):
        """Возвращает случайный модификатор для врага"""
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
            },
            {
                "name": "Кровавый",
                "effect": "life_leech",
                "value": 0.2,
                "description": "Вампиризм 20%"
            },
            {
                "name": "Неуязвимый",
                "effect": "damage_reduction",
                "value": 0.5,
                "description": "Снижение получаемого урона"
            },
            {
                "name": "Яростный",
                "effect": "rage",
                "value": 1.5,
                "description": "Урон увеличивается с потерей HP"
            },
            {
                "name": "Призыватель",
                "effect": "summon",
                "value": 2,
                "description": "Призывает союзников в бою"
            }
        ]
        return random.choice(modifiers)
    
    # ============= БОЕВЫЕ МЕТОДЫ =============
    
    def attack(self):
        """Выполняет атаку и возвращает урон"""
        # Базовый урон
        damage = random.randint(self.damage_min, self.damage_max)
        
        # Применяем модификаторы
        for mod in self.modifiers:
            if mod["effect"] == "damage_mult":
                damage = int(damage * mod["value"])
            elif mod["effect"] == "poison" and random.random() < 0.3:
                # Добавляем эффект отравления
                self.buffs.append(("poison_attack", 1, {"poison_damage": mod["value"]}))
        
        self.turns_taken += 1
        return damage
    
    def take_damage(self, damage):
        """Получает урон"""
        # Применяем модификаторы защиты
        actual_damage = damage
        for mod in self.modifiers:
            if mod["effect"] == "damage_reduction":
                actual_damage = int(actual_damage * mod["value"])
        
        # Учитываем защиту
        reduced_damage = max(1, actual_damage - self.defense // 3)
        
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
        
        # Цвет в зависимости от процента здоровья
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
        """Возвращает строку с модификаторами врага"""
        if not self.modifiers:
            return ""
        
        mod_emojis = {
            "hp_mult": "❤️",
            "damage_mult": "⚔️",
            "defense_mult": "🛡️",
            "accuracy_bonus": "🎯",
            "speed_mult": "⚡",
            "poison": "☠️",
            "life_leech": "🩸",
            "damage_reduction": "🔰",
            "rage": "😤",
            "summon": "👥"
        }
        
        mods = []
        for mod in self.modifiers:
            emoji = mod_emojis.get(mod["effect"], "✨")
            mods.append(f"{emoji} {mod['name']}")
        
        return " | ".join(mods)
    
    def get_rarity_color(self):
        """Возвращает цвет редкости врага"""
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
        return random.randint(self.gold_min, self.gold_max)
    
    def get_exp_reward(self):
        """Возвращает награду опытом"""
        return self.exp_reward
    
    # ============= МЕТОДЫ ДЛЯ БОССОВ =============
    
    def apply_phase_change(self, phase):
        """Применяет изменения для фазы босса"""
        if "damage_mult" in phase:
            self.damage_min = int(self.damage_min * phase["damage_mult"])
            self.damage_max = int(self.damage_max * phase["damage_mult"])
        
        if "speed_mult" in phase:
            # Здесь будет изменение скорости
            pass
        
        if "adds" in phase:
            # Здесь будет призыв дополнительных врагов
            pass
    
    # ============= МЕТОДЫ ВРЕМЕННЫХ ЭФФЕКТОВ =============
    
    def add_buff(self, name, duration, effect):
        """Добавляет временный бафф"""
        self.buffs.append([name, duration, effect])
    
    def add_debuff(self, name, duration, effect):
        """Добавляет временный дебафф"""
        self.debuffs.append([name, duration, effect])
    
    def update_effects(self):
        """Обновляет длительность эффектов"""
        # Обновляем баффы
        new_buffs = []
        for buff in self.buffs:
            buff[1] -= 1
            if buff[1] > 0:
                new_buffs.append(buff)
            else:
                self._remove_buff_effect(buff[2])
        self.buffs = new_buffs
        
        # Обновляем дебаффы
        new_debuffs = []
        for debuff in self.debuffs:
            debuff[1] -= 1
            if debuff[1] > 0:
                new_debuffs.append(debuff)
            else:
                self._remove_debuff_effect(debuff[2])
        self.debuffs = new_debuffs
    
    def _remove_buff_effect(self, effect):
        """Убирает эффект баффа"""
        pass
    
    def _remove_debuff_effect(self, effect):
        """Убирает эффект дебаффа"""
        pass
    
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
            # Случайная редкость
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
            f"📈 Уровень локации: {self.area_level}\n"
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


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_enemy_creation():
    """Тест создания врагов"""
    print("=" * 50)
    print("ТЕСТ СОЗДАНИЯ ВРАГОВ")
    print("=" * 50)
    
    # Создаем обычного врага
    common_enemy = Enemy(
        name="Гниющий узник",
        base_hp=20,
        damage_range=(3, 6),
        accuracy=50,
        defense=1,
        base_exp=8,
        emoji="🧟",
        rarity="common",
        area_level=1
    )
    
    print("Обычный враг:")
    print(common_enemy.get_stats_string())
    print()
    
    # Создаем магического врага
    magic_enemy = Enemy(
        name="Гниющий узник-калека",
        base_hp=35,
        damage_range=(4, 8),
        accuracy=55,
        defense=2,
        base_exp=15,
        emoji="🧟⚡",
        rarity="magic",
        area_level=2
    )
    
    print("Магический враг:")
    print(magic_enemy.get_stats_string())
    print()
    
    # Создаем редкого врага
    rare_enemy = Enemy(
        name="Тюремный надзиратель",
        base_hp=50,
        damage_range=(6, 12),
        accuracy=65,
        defense=4,
        base_exp=25,
        emoji="👹🔑",
        rarity="rare",
        area_level=3
    )
    
    print("Редкий враг:")
    print(rare_enemy.get_stats_string())


def test_enemy_scaling():
    """Тест масштабирования врагов"""
    print("=" * 50)
    print("ТЕСТ МАСШТАБИРОВАНИЯ")
    print("=" * 50)
    
    base_monster = {
        "name": "Тестовый монстр",
        "base_hp": 30,
        "damage": (5, 10),
        "accuracy": 60,
        "defense": 2,
        "base_exp": 15,
        "emoji": "👾"
    }
    
    for area_level in [1, 3, 5, 7]:
        print(f"\nУровень локации: {area_level}")
        print("-" * 30)
        
        for rarity in ["common", "magic", "rare"]:
            enemy = Enemy.from_monster_data(base_monster, area_level, rarity)
            print(f"{rarity.capitalize()}: HP {enemy.max_hp}, Урон {enemy.damage_min}-{enemy.damage_max}, "
                  f"Защита {enemy.defense}, Опыт {enemy.exp_reward}")


def test_battle_simulation():
    """Тест симуляции боя"""
    print("=" * 50)
    print("ТЕСТ БОЕВОЙ СИСТЕМЫ")
    print("=" * 50)
    
    # Создаем врага
    enemy = Enemy(
        name="Огромный червь",
        base_hp=40,
        damage_range=(6, 12),
        accuracy=60,
        defense=3,
        base_exp=22,
        emoji="🪱",
        rarity="magic",
        area_level=3
    )
    
    print("Начальное состояние:")
    print(enemy.get_battle_string())
    print()
    
    # Симулируем несколько ударов
    total_damage = 0
    for i in range(1, 6):
        damage = random.randint(10, 20)
        actual = enemy.take_damage(damage)
        total_damage += actual
        print(f"Удар {i}: нанесено {actual} урона")
        print(f"  {enemy.get_hp_bar()}")
        
        if not enemy.is_alive():
            print(f"\nВраг побежден! Всего урона: {total_damage}")
            print(f"Награда: {enemy.get_exp_reward()} опыта, {enemy.get_gold_reward()} золота")
            break


if __name__ == "__main__":
    test_enemy_creation()
    print("\n")
    test_enemy_scaling()
    print("\n")
    test_battle_simulation()
