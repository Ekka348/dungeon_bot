import random
import math
from models.item import Item, ItemRarity, ItemType, MeleeWeapon, Flask, generate_melee_weapon, generate_flask
from data.items import FLASKS
from data.weapons import WEAPON_BASES, UNIQUE_WEAPONS

# ============= ТИПЫ ЛУТА =============

class LootType:
    GOLD = "gold"
    WEAPON = "weapon"
    ARMOR = "armor"
    FLASK = "flask"
    CURRENCY = "currency"
    QUEST_ITEM = "quest_item"
    CONSUMABLE = "consumable"
    GEM = "gem"
    JEWEL = "jewel"
    MAP = "map"


# ============= КЛАСС ПРЕДМЕТА ЛУТА =============

class LootItem:
    """Предмет лута"""
    
    def __init__(self, loot_type, item=None, amount=1, chance=100):
        self.type = loot_type
        self.item = item
        self.amount = amount
        self.chance = chance
        self.is_currency = loot_type == LootType.CURRENCY
        self.is_quest = loot_type == LootType.QUEST_ITEM
    
    def get_name(self):
        """Возвращает имя предмета"""
        if self.item:
            if isinstance(self.item, Item):
                return self.item.get_name_colored()
            return str(self.item)
        elif self.type == LootType.GOLD:
            return f"💰 {self.amount} золота"
        elif self.type == LootType.CURRENCY:
            return f"💎 {self.amount} валюты"
        else:
            return f"Предмет x{self.amount}"
    
    def get_description(self):
        """Возвращает описание"""
        if self.item and isinstance(self.item, Item):
            return self.item.get_detailed_info()
        return self.get_name()


# ============= ТАБЛИЦЫ ЛУТА =============

class LootTable:
    """Таблица лута с весами"""
    
    def __init__(self, name):
        self.name = name
        self.entries = []  # (item, weight, min_count, max_count)
        self.total_weight = 0
    
    def add_entry(self, item, weight=1, min_count=1, max_count=1):
        """Добавляет запись в таблицу"""
        self.entries.append((item, weight, min_count, max_count))
        self.total_weight += weight
    
    def roll(self, luck=0):
        """Бросает кубик на выпадение предмета"""
        if not self.entries:
            return None
        
        roll = random.randint(1, self.total_weight)
        current = 0
        
        for item, weight, min_count, max_count in self.entries:
            current += weight
            if roll <= current:
                count = random.randint(min_count, max_count)
                return LootItem(LootType.CURRENCY, item, count)
        
        return None
    
    def roll_multiple(self, count=1, luck=0):
        """Бросает кубик несколько раз"""
        results = []
        for _ in range(count):
            result = self.roll(luck)
            if result:
                results.append(result)
        return results


# ============= ОСНОВНАЯ СИСТЕМА ЛУТА =============

class LootSystem:
    """Система генерации лута"""
    
    def __init__(self):
        # Таблицы лута для разных редкостей
        self.common_table = LootTable("Обычный лут")
        self.magic_table = LootTable("Магический лут")
        self.rare_table = LootTable("Редкий лут")
        self.boss_table = LootTable("Лут босса")
        self.chest_tables = {}
        
        # Инициализация таблиц
        self._init_tables()
    
    def _init_tables(self):
        """Инициализирует таблицы лута"""
        
        # Обычный лут
        self.common_table.add_entry("gold", 100, 5, 15)
        self.common_table.add_entry("small_flask", 30, 1, 1)
        self.common_table.add_entry("rusty_weapon", 20, 1, 1)
        
        # Магический лут
        self.magic_table.add_entry("gold", 80, 15, 30)
        self.magic_table.add_entry("medium_flask", 40, 1, 1)
        self.magic_table.add_entry("magic_weapon", 30, 1, 1)
        self.magic_table.add_entry("currency_shard", 20, 1, 3)
        
        # Редкий лут
        self.rare_table.add_entry("gold", 60, 30, 60)
        self.rare_table.add_entry("large_flask", 30, 1, 1)
        self.rare_table.add_entry("rare_weapon", 40, 1, 1)
        self.rare_table.add_entry("currency", 25, 1, 2)
        self.rare_table.add_entry("gem", 15, 1, 1)
        
        # Лут босса
        self.boss_table.add_entry("gold", 100, 100, 300)
        self.boss_table.add_entry("divine_flask", 50, 1, 1)
        self.boss_table.add_entry("rare_weapon", 80, 1, 2)
        self.boss_table.add_entry("unique_weapon", 20, 1, 1)
        self.boss_table.add_entry("currency", 60, 2, 5)
        self.boss_table.add_entry("gem", 40, 1, 2)
        self.boss_table.add_entry("map", 30, 1, 1)
    
    def generate_loot(self, enemy_rarity, area_level, monster_level, location_id=None):
        """Генерирует лут с врага"""
        loot = []
        
        # Определяем базовый шанс выпадения
        base_chance = {
            "common": 70,
            "magic": 90,
            "rare": 100,
            "boss": 100
        }.get(enemy_rarity, 50)
        
        # Бонус за уровень локации
        level_bonus = min(20, area_level // 2)
        drop_chance = min(100, base_chance + level_bonus)
        
        # Проверяем, выпал ли лут
        if random.randint(1, 100) > drop_chance:
            return []  # Нет лута
        
        # Количество предметов зависит от редкости
        quantity = {
            "common": random.randint(1, 2),
            "magic": random.randint(1, 3),
            "rare": random.randint(2, 4),
            "boss": random.randint(3, 6)
        }.get(enemy_rarity, 1)
        
        # Генерируем предметы
        for _ in range(quantity):
            item = self._generate_loot_item(enemy_rarity, area_level, monster_level, location_id)
            if item:
                loot.append(item)
        
        # Всегда добавляем золото
        gold = self._generate_gold(enemy_rarity, area_level)
        loot.append(LootItem(LootType.GOLD, amount=gold))
        
        return loot
    
    def _generate_loot_item(self, enemy_rarity, area_level, monster_level, location_id=None):
        """Генерирует один предмет лута"""
        
        # Item level зависит от уровня локации и монстра
        item_level = self._calculate_item_level(area_level, monster_level, enemy_rarity)
        
        # Выбираем тип предмета
        item_type_roll = random.random()
        
        if item_type_roll < 0.6:  # 60% оружие
            return self._generate_weapon(item_level, enemy_rarity)
        elif item_type_roll < 0.8:  # 20% фласка
            return self._generate_flask(item_level, enemy_rarity)
        else:  # 20% другое (пока просто золото)
            return None
    
    def _calculate_item_level(self, area_level, monster_level, rarity):
        """Рассчитывает уровень предмета"""
        # Базовый уровень = уровень локации
        base_ilvl = area_level
        
        # Бонус за уровень монстра
        monster_bonus = (monster_level - area_level) // 2
        
        # Бонус за редкость
        rarity_bonus = {
            "common": 0,
            "magic": 2,
            "rare": 5,
            "boss": 10
        }.get(rarity, 0)
        
        # Случайный разброс
        variance = random.randint(-2, 3)
        
        ilvl = base_ilvl + monster_bonus + rarity_bonus + variance
        return max(1, ilvl)
    
    def _generate_weapon(self, item_level, rarity):
        """Генерирует оружие"""
        weapon = generate_melee_weapon(item_level, rarity)
        if weapon:
            return LootItem(LootType.WEAPON, weapon)
        return None
    
    def _generate_flask(self, item_level, rarity):
        """Генерирует фласку"""
        flask = generate_flask()
        if flask:
            return LootItem(LootType.FLASK, flask)
        return None
    
    def _generate_gold(self, enemy_rarity, area_level):
        """Генерирует золото"""
        base_gold = {
            "common": 5,
            "magic": 15,
            "rare": 30,
            "boss": 100
        }.get(enemy_rarity, 5)
        
        # Масштабирование с уровнем
        gold = random.randint(base_gold, base_gold * 2) * (1 + area_level // 5)
        return gold
    
    def generate_chest_loot(self, chest_rarity, area_level):
        """Генерирует лут из сундука"""
        loot = []
        
        # Количество предметов
        quantity = {
            "common": random.randint(1, 2),
            "magic": random.randint(2, 3),
            "rare": random.randint(3, 5)
        }.get(chest_rarity, 1)
        
        # Золото
        gold_base = {
            "common": 15,
            "magic": 40,
            "rare": 80
        }.get(chest_rarity, 10)
        
        gold = random.randint(gold_base, gold_base * 2) * (1 + area_level // 5)
        loot.append(LootItem(LootType.GOLD, amount=gold))
        
        # Предметы
        for _ in range(quantity):
            # Шанс на предмет
            if random.random() < 0.4:  # 40% шанс на предмет в сундуке
                item_level = area_level + random.randint(1, 3)
                
                if random.random() < 0.7:  # 70% оружие
                    weapon = generate_melee_weapon(item_level, chest_rarity)
                    if weapon:
                        loot.append(LootItem(LootType.WEAPON, weapon))
                else:  # 30% фласка
                    flask = generate_flask()
                    if flask:
                        loot.append(LootItem(LootType.FLASK, flask))
        
        return loot


# ============= СИСТЕМА ВЫПАДЕНИЯ УНИКАЛЬНЫХ ПРЕДМЕТОВ =============

class UniqueLootSystem:
    """Система для уникальных предметов"""
    
    def __init__(self):
        # Шансы выпадения уникальных предметов
        self.base_chance = 0.01  # 1% базовый шанс
        self.unique_pool = []
        self._init_unique_pool()
    
    def _init_unique_pool(self):
        """Инициализирует пул уникальных предметов"""
        for unique_id in UNIQUE_WEAPONS:
            self.unique_pool.append({
                "id": unique_id,
                "name": UNIQUE_WEAPONS[unique_id]["name"],
                "weight": 100,  # Все одинаковый вес
                "min_level": UNIQUE_WEAPONS[unique_id].get("requirements", {}).get("level", 1)
            })
    
    def roll_for_unique(self, area_level, monster_rarity):
        """Пытается выкинуть уникальный предмет"""
        # Шанс зависит от редкости монстра и уровня локации
        rarity_mult = {
            "common": 1,
            "magic": 3,
            "rare": 5,
            "boss": 10
        }.get(monster_rarity, 1)
        
        level_bonus = area_level / 100  # +1% за 100 уровня
        chance = self.base_chance * rarity_mult * (1 + level_bonus)
        
        if random.random() < chance:
            return self._select_unique(area_level)
        return None
    
    def _select_unique(self, area_level):
        """Выбирает подходящий уникальный предмет"""
        available = [u for u in self.unique_pool if u["min_level"] <= area_level]
        if not available:
            return None
        
        # Выбор с учетом весов
        weights = [u["weight"] for u in available]
        return random.choices(available, weights=weights)[0]["id"]


# ============= СИСТЕМА КАЧЕСТВА ЛУТА =============

class LootQualitySystem:
    """Система качества лута (влияет на шансы)"""
    
    def __init__(self, player):
        self.player = player
        self.quality_multiplier = 1.0
        
        # Факторы, влияющие на качество
        self.factors = {
            "luck": 0,  # Удача
            "rarity_find": 0,  # Поиск редкости
            "quantity_find": 0  # Поиск количества
        }
        
        self._update_factors()
    
    def _update_factors(self):
        """Обновляет факторы на основе экипировки игрока"""
        # Здесь будет логика расчета от экипировки
        pass
    
    def apply_quality(self, base_chance):
        """Применяет качество к шансу"""
        return base_chance * self.quality_multiplier
    
    def apply_quantity(self, base_quantity):
        """Применяет качество к количеству"""
        quantity_mult = 1 + self.factors["quantity_find"] / 100
        return int(base_quantity * quantity_mult)


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_loot_generation():
    """Тест генерации лута"""
    print("=" * 50)
    print("ТЕСТ ГЕНЕРАЦИИ ЛУТА")
    print("=" * 50)
    
    loot_system = LootSystem()
    
    # Тест для разных редкостей
    for rarity in ["common", "magic", "rare", "boss"]:
        print(f"\n🔹 {rarity.upper()} враг (ур. 5):")
        print("-" * 30)
        
        loot = loot_system.generate_loot(rarity, 5, 5)
        
        if not loot:
            print("  Нет лута")
        else:
            for item in loot:
                print(f"  {item.get_name()}")
    
    # Тест сундуков
    print("\n🔹 СУНДУКИ (ур. 5):")
    for chest_type in ["common", "magic", "rare"]:
        print(f"\n  {chest_type.capitalize()} сундук:")
        chest_loot = loot_system.generate_chest_loot(chest_type, 5)
        for item in chest_loot:
            print(f"    {item.get_name()}")


def test_loot_scaling():
    """Тест масштабирования лута"""
    print("=" * 50)
    print("ТЕСТ МАСШТАБИРОВАНИЯ ЛУТА")
    print("=" * 50)
    
    loot_system = LootSystem()
    
    for area_level in [1, 5, 10, 15]:
        print(f"\n🔹 Уровень локации: {area_level}")
        print("-" * 30)
        
        # Считаем среднее золото за 10 убийств
        total_gold = 0
        for _ in range(10):
            loot = loot_system.generate_loot("common", area_level, area_level)
            for item in loot:
                if item.type == LootType.GOLD:
                    total_gold += item.amount
        
        avg_gold = total_gold / 10
        print(f"  Среднее золото: {avg_gold:.0f}")
        
        # Проверяем уровень предметов
        weapon_count = 0
        for _ in range(20):
            loot = loot_system.generate_loot("rare", area_level, area_level)
            for item in loot:
                if item.type == LootType.WEAPON and item.item:
                    weapon_count += 1
                    print(f"  Оружие: {item.item.name} (Ур. {item.item.item_level})")
                    break  # Только одно для примера


def test_unique_loot():
    """Тест выпадения уникальных предметов"""
    print("=" * 50)
    print("ТЕСТ УНИКАЛЬНЫХ ПРЕДМЕТОВ")
    print("=" * 50)
    
    unique_system = UniqueLootSystem()
    
    # Симуляция 1000 убийств боссов
    unique_count = 0
    for i in range(1000):
        unique_id = unique_system.roll_for_unique(10, "boss")
        if unique_id:
            unique_count += 1
            if unique_count <= 3:  # Покажем первые 3
                print(f"\n  🎉 На {i} убийстве выпало: {unique_id}")
    
    chance = (unique_count / 1000) * 100
    print(f"\n📊 Шанс выпадения: {chance:.2f}%")


def test_loot_distribution():
    """Тест распределения лута"""
    print("=" * 50)
    print("ТЕСТ РАСПРЕДЕЛЕНИЯ ЛУТА")
    print("=" * 50)
    
    loot_system = LootSystem()
    
    distributions = {
        "common": {"total": 0, "weapons": 0, "flasks": 0, "gold_total": 0},
        "magic": {"total": 0, "weapons": 0, "flasks": 0, "gold_total": 0},
        "rare": {"total": 0, "weapons": 0, "flasks": 0, "gold_total": 0},
        "boss": {"total": 0, "weapons": 0, "flasks": 0, "gold_total": 0}
    }
    
    # Симуляция 100 убийств каждой редкости
    for rarity in distributions.keys():
        for _ in range(100):
            loot = loot_system.generate_loot(rarity, 5, 5)
            distributions[rarity]["total"] += len(loot)
            
            for item in loot:
                if item.type == LootType.WEAPON:
                    distributions[rarity]["weapons"] += 1
                elif item.type == LootType.FLASK:
                    distributions[rarity]["flasks"] += 1
                elif item.type == LootType.GOLD:
                    distributions[rarity]["gold_total"] += item.amount
    
    # Вывод статистики
    for rarity, stats in distributions.items():
        print(f"\n🔹 {rarity.upper()}:")
        print(f"  Всего предметов: {stats['total']}")
        if stats['total'] > 0:
            weapon_percent = (stats['weapons'] / stats['total']) * 100
            flask_percent = (stats['flasks'] / stats['total']) * 100
            print(f"  Оружие: {stats['weapons']} ({weapon_percent:.1f}%)")
            print(f"  Фласки: {stats['flasks']} ({flask_percent:.1f}%)")
            print(f"  Среднее золото: {stats['gold_total'] / 100:.0f}")


if __name__ == "__main__":
    test_loot_generation()
    print("\n")
    test_loot_scaling()
    print("\n")
    test_unique_loot()
    print("\n")
    test_loot_distribution()
