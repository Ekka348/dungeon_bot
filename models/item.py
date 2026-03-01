import random
from enum import Enum
from data.items import PREFIXES, SUFFIXES, FLASKS
from data.weapons import WEAPON_BASES, UNIQUE_WEAPONS

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

class WeaponType:
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


# ============= БАЗОВЫЙ КЛАСС ПРЕДМЕТА =============

class Item:
    """Базовый класс для всех предметов"""
    
    def __init__(self, name, item_type, rarity=ItemRarity.NORMAL, item_level=1):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.item_level = item_level
        self.emoji = self._get_emoji()
        self.affixes = []  # [(affix_type, affix_data)]
        self.stats = {}  # {stat_name: value}
        self.description = ""
        self.value = 0  # Цена продажи
        
        # Качество (0-20%)
        self.quality = 0
        
        # Флаг для уникальных предметов
        self.is_unique = (rarity == ItemRarity.UNIQUE)
    
    def _get_emoji(self):
        """Возвращает эмодзи для типа предмета"""
        emoji_map = {
            ItemType.WEAPON: "⚔️",
            ItemType.HELMET: "⛑️",
            ItemType.ARMOR: "🛡️",
            ItemType.GLOVES: "🧤",
            ItemType.BOOTS: "👢",
            ItemType.BELT: "🔗",
            ItemType.RING: "💍",
            ItemType.AMULET: "📿",
            ItemType.FLASK: "🧪"
        }
        return emoji_map.get(self.item_type, "📦")
    
    def add_affix(self, affix_data, affix_type):
        """Добавляет аффикс к предмету"""
        self.affixes.append((affix_type, affix_data))
        
        # Генерируем значение в зависимости от уровня предмета
        base_value = random.randint(affix_data["value"][0], affix_data["value"][1])
        scaled_value = self._scale_affix_value(base_value, affix_data.get("tier", 1))
        
        # Добавляем к статам
        stat_name = affix_data["stat"]
        self.stats[stat_name] = self.stats.get(stat_name, 0) + scaled_value
    
    def _scale_affix_value(self, base_value, tier):
        """Масштабирует значение аффикса в зависимости от уровня предмета"""
        # Чем выше уровень предмета и тир, тем больше значение
        level_mult = 1 + (self.item_level - 1) * 0.1
        tier_mult = 1 + (tier - 1) * 0.2
        return int(base_value * level_mult * tier_mult)
    
    def get_rarity_emoji(self):
        """Возвращает эмодзи редкости"""
        rarity_emojis = {
            ItemRarity.NORMAL: "⚪",
            ItemRarity.MAGIC: "🔵",
            ItemRarity.RARE: "🟡",
            ItemRarity.UNIQUE: "🔴"
        }
        return rarity_emojis.get(self.rarity, "⚪")
    
    def get_rarity_name(self):
        """Возвращает название редкости"""
        rarity_names = {
            ItemRarity.NORMAL: "Обычный",
            ItemRarity.MAGIC: "Магический",
            ItemRarity.RARE: "Редкий",
            ItemRarity.UNIQUE: "Уникальный"
        }
        return rarity_names.get(self.rarity, "Обычный")
    
    def get_type_name(self):
        """Возвращает название типа предмета"""
        type_names = {
            ItemType.WEAPON: "Оружие",
            ItemType.HELMET: "Шлем",
            ItemType.ARMOR: "Броня",
            ItemType.GLOVES: "Перчатки",
            ItemType.BOOTS: "Сапоги",
            ItemType.BELT: "Пояс",
            ItemType.RING: "Кольцо",
            ItemType.AMULET: "Амулет",
            ItemType.FLASK: "Фласка"
        }
        return type_names.get(self.item_type, "Предмет")
    
    def get_name_colored(self):
        """Возвращает цветное имя для инвентаря"""
        return f"{self.get_rarity_emoji()}{self.emoji} {self.name}"
    
    def get_detailed_info(self):
        """Возвращает подробную информацию о предмете"""
        lines = []
        
        # Заголовок
        lines.append(f"{self.get_rarity_emoji()} **{self.name}**")
        lines.append(f"└ {self.get_rarity_name()} {self.emoji} {self.get_type_name()} (Ур. {self.item_level})")
        lines.append("")
        
        # Базовые характеристики (переопределяется в наследниках)
        lines.append(self._get_base_stats_string())
        
        # Качество
        if self.quality > 0:
            lines.append(f"✨ Качество: +{self.quality}%")
        
        # Аффиксы
        if self.affixes:
            lines.append("\n**Модификаторы:**")
            for affix_type, affix_data in self.affixes:
                prefix_suffix = "🔺 Префикс" if affix_type == AffixType.PREFIX else "🔻 Суффикс"
                value = self.stats.get(affix_data["stat"], 0)
                
                # Красивое название стата
                stat_names = {
                    "damage": "⚔️ Урон",
                    "max_hp": "❤️ Здоровье",
                    "defense": "🛡️ Защита",
                    "attack_speed": "⚡ Скорость атаки",
                    "accuracy": "🎯 Точность",
                    "crit_chance": "🔥 Шанс крита",
                    "crit_multiplier": "💥 Множитель крита",
                    "life_regen": "🌿 Регенерация",
                    "life_on_hit": "🩸 Вампиризм",
                    "stun_multiplier": "😵 Оглушение",
                    "fire_res": "🔥 Сопротивление огню",
                    "cold_res": "❄️ Сопротивление холоду",
                    "lightning_res": "⚡ Сопротивление молнии",
                    "elemental_damage": "✨ Стихийный урон",
                    "range_bonus": "📏 Дальность",
                    "block_chance": "🛡️ Шанс блока"
                }
                
                stat_name = stat_names.get(affix_data["stat"], affix_data["stat"])
                lines.append(f"  {prefix_suffix}: {affix_data['name']}")
                lines.append(f"    {stat_name}: +{value}")
        
        # Описание для уникальных предметов
        if self.is_unique and self.description:
            lines.append(f"\n*{self.description}*")
        
        return "\n".join(lines)
    
    def _get_base_stats_string(self):
        """Возвращает строку с базовыми характеристиками"""
        return "**Характеристики:**\n  • База предмета"
    
    def calculate_value(self):
        """Рассчитывает стоимость предмета"""
        base_value = self.item_level * 5
        
        # Бонус за редкость
        rarity_mult = {
            ItemRarity.NORMAL: 1,
            ItemRarity.MAGIC: 2,
            ItemRarity.RARE: 4,
            ItemRarity.UNIQUE: 10
        }.get(self.rarity, 1)
        
        # Бонус за качество
        quality_bonus = 1 + self.quality / 100
        
        # Бонус за аффиксы
        affix_bonus = 1 + len(self.affixes) * 0.2
        
        self.value = int(base_value * rarity_mult * quality_bonus * affix_bonus)
        return self.value


# ============= КЛАСС ОРУЖИЯ =============

class MeleeWeapon(Item):
    """Класс для оружия ближнего боя"""
    
    def __init__(self, weapon_id, rarity=ItemRarity.NORMAL, item_level=1, quality=0):
        base = WEAPON_BASES[weapon_id]
        
        super().__init__(base["name"], ItemType.WEAPON, rarity, item_level)
        
        self.weapon_id = weapon_id
        self.weapon_type = base["type"]
        self.quality = quality
        self.tier = base.get("tier", 1)
        self.emoji = base.get("emoji", "⚔️")
        
        # Базовые характеристики
        self.base_damage_min = base["damage_range"][0]
        self.base_damage_max = base["damage_range"][1]
        self.attack_speed = base.get("attack_speed", 1.2)
        self.crit_chance = base.get("crit_chance", 5)
        self.accuracy = base.get("accuracy", 0)
        self.life_on_hit = base.get("life_on_hit", 0)
        self.stun_multiplier = base.get("stun_multiplier", 1.0)
        self.range_bonus = base.get("range_bonus", 0)
        self.elemental_damage = base.get("elemental_damage", 0)
        self.block_chance = base.get("block_chance", 0)
        
        # Требования
        self.requirements = base.get("requirements", {})
        
        # Неявные модификаторы
        self.implicit = base.get("implicit", "")
        
        # Масштабирование с уровнем
        self._scale_with_level()
    
    def _scale_with_level(self):
        """Масштабирует характеристики оружия с уровнем"""
        level_mult = 1 + (self.item_level - 1) * 0.1
        
        self.base_damage_min = int(self.base_damage_min * level_mult)
        self.base_damage_max = int(self.base_damage_max * level_mult)
        
        # Требования тоже растут
        for stat in self.requirements:
            self.requirements[stat] = int(self.requirements[stat] * (0.8 + self.item_level * 0.05))
    
    def get_damage_range(self):
        """Возвращает диапазон урона с учетом качества и аффиксов"""
        # Бонус качества (0.5% урона за 1% качества)
        quality_bonus = 1 + (self.quality / 100 * 0.5)
        
        # Бонус от аффиксов
        damage_bonus = self.stats.get("damage", 0) / 100
        
        min_damage = int(self.base_damage_min * (1 + damage_bonus) * quality_bonus)
        max_damage = int(self.base_damage_max * (1 + damage_bonus) * quality_bonus)
        
        return min_damage, max_damage
    
    def _get_base_stats_string(self):
        """Возвращает строку с базовыми характеристиками оружия"""
        min_dmg, max_dmg = self.get_damage_range()
        avg_dmg = (min_dmg + max_dmg) // 2
        dps = int(avg_dmg * self.attack_speed)
        
        # Название типа оружия
        weapon_type_names = {
            WeaponType.ONE_HAND_SWORD: "Одноручный меч",
            WeaponType.THRUSTING_SWORD: "Шпага",
            WeaponType.ONE_HAND_AXE: "Одноручный топор",
            WeaponType.ONE_HAND_MACE: "Одноручная булава",
            WeaponType.CLAW: "Коготь",
            WeaponType.DAGGER: "Кинжал",
            WeaponType.SCEPTRE: "Скипетр",
            WeaponType.TWO_HAND_SWORD: "Двуручный меч",
            WeaponType.TWO_HAND_AXE: "Двуручный топор",
            WeaponType.TWO_HAND_MACE: "Двуручная булава",
            WeaponType.STAFF: "Посох",
            WeaponType.QUARTERSTAFF: "Боевой шест",
            WeaponType.SPEAR: "Копье",
            WeaponType.FLAIL: "Цеп"
        }
        type_name = weapon_type_names.get(self.weapon_type, "Оружие")
        
        lines = [
            f"**Тип:** {type_name} (Тир {self.tier})",
            f"**Уровень предмета:** {self.item_level}",
            f"**Характеристики:**",
            f"  ⚔️ Урон: {min_dmg}-{max_dmg} (ср. {avg_dmg})",
            f"  ⚡ Скорость: {self.attack_speed:.2f} атак/сек",
            f"  📊 DPS: {dps}",
            f"  💥 Шанс крита: {self.crit_chance + self.stats.get('crit_chance', 0)}%"
        ]
        
        if self.accuracy:
            lines.append(f"  🎯 Точность: +{self.accuracy + self.stats.get('accuracy', 0)}")
        if self.life_on_hit or 'life_on_hit' in self.stats:
            total_loh = self.life_on_hit + self.stats.get('life_on_hit', 0)
            lines.append(f"  🩸 Вампиризм: {total_loh} HP/удар")
        if self.stun_multiplier > 1 or 'stun_multiplier' in self.stats:
            mult = self.stun_multiplier * (1 + self.stats.get('stun_multiplier', 0) / 100)
            lines.append(f"  😵 Оглушение: x{mult:.1f}")
        if self.range_bonus:
            lines.append(f"  📏 Дальность: +{self.range_bonus}")
        if self.elemental_damage:
            lines.append(f"  🔥 Стихийный урон: +{self.elemental_damage}%")
        if self.block_chance:
            lines.append(f"  🛡️ Шанс блока: {self.block_chance}%")
        
        # Неявный модификатор
        if self.implicit:
            lines.append(f"  ✨ Особое: {self.implicit}")
        
        lines.append("")
        
        # Требования
        if self.requirements:
            req_text = "**Требования:** "
            req_parts = []
            if "str" in self.requirements:
                req_parts.append(f"💪 {self.requirements['str']}")
            if "dex" in self.requirements:
                req_parts.append(f"🏹 {self.requirements['dex']}")
            if "int" in self.requirements:
                req_parts.append(f"📚 {self.requirements['int']}")
            lines.append(" | ".join(req_parts))
        
        return "\n".join(lines)
    
    def get_requirements_string(self):
        """Возвращает строку с требованиями"""
        if not self.requirements:
            return "Нет требований"
        
        reqs = []
        if "str" in self.requirements:
            reqs.append(f"💪 {self.requirements['str']}")
        if "dex" in self.requirements:
            reqs.append(f"🏹 {self.requirements['dex']}")
        if "int" in self.requirements:
            reqs.append(f"📚 {self.requirements['int']}")
        
        return " | ".join(reqs)


# ============= КЛАСС УНИКАЛЬНОГО ОРУЖИЯ =============

class UniqueWeapon(MeleeWeapon):
    """Класс для уникального оружия"""
    
    def __init__(self, unique_id, item_level=1):
        data = UNIQUE_WEAPONS[unique_id]
        base_data = WEAPON_BASES[data["base"]]
        
        super().__init__(data["base"], ItemRarity.UNIQUE, item_level)
        
        self.name = data["name"]
        self.emoji = data.get("emoji", base_data.get("emoji", "⚔️"))
        self.description = data["description"]
        self.fixed_mods = data["fixed_mods"]
        
        # Переопределяем базовые характеристики
        self.base_damage_min = data["damage_range"][0]
        self.base_damage_max = data["damage_range"][1]
        self.attack_speed = data.get("attack_speed", base_data.get("attack_speed", 1.2))
        self.crit_chance = data.get("crit_chance", base_data.get("crit_chance", 5))
        
        # Требования
        self.requirements = data.get("requirements", base_data.get("requirements", {}))
        
        # Масштабирование с уровнем
        self._scale_with_level()
        
        # Добавляем фиксированные моды как аффиксы
        for stat, value in self.fixed_mods.items():
            self.stats[stat] = self.stats.get(stat, 0) + value
    
    def _scale_with_level(self):
        """Масштабирует уникальное оружие с уровнем"""
        level_mult = 1 + (self.item_level - 1) * 0.05  # Уникальное растет медленнее
        
        self.base_damage_min = int(self.base_damage_min * level_mult)
        self.base_damage_max = int(self.base_damage_max * level_mult)
        
        # Масштабируем фиксированные моды
        scaled_mods = {}
        for stat, value in self.fixed_mods.items():
            if isinstance(value, (int, float)):
                scaled_mods[stat] = int(value * level_mult)
            else:
                scaled_mods[stat] = value
        self.fixed_mods = scaled_mods
        
        # Требования тоже растут
        for stat in self.requirements:
            self.requirements[stat] = int(self.requirements[stat] * (0.9 + self.item_level * 0.03))
    
    def get_damage_range(self):
        """Возвращает диапазон урона с учетом фиксированных модов"""
        min_dmg, max_dmg = super().get_damage_range()
        
        if "damage" in self.fixed_mods:
            min_dmg += self.fixed_mods["damage"]
            max_dmg += self.fixed_mods["damage"]
        
        return min_dmg, max_dmg
    
    def _get_base_stats_string(self):
        """Возвращает строку с базовыми характеристиками уникального оружия"""
        stats_str = super()._get_base_stats_string()
        
        # Добавляем информацию об уникальных модах
        lines = stats_str.split("\n")
        lines.append("")
        lines.append("**Уникальные свойства:**")
        
        for stat, value in self.fixed_mods.items():
            if stat == "damage":
                lines.append(f"  ⚔️ Доп. урон: +{value}")
            elif stat == "cold_damage":
                lines.append(f"  ❄️ Холодный урон: +{value}%")
            elif stat == "fire_damage":
                lines.append(f"  🔥 Огненный урон: +{value}%")
            elif stat == "lightning_damage":
                lines.append(f"  ⚡ Молниеносный урон: +{value}%")
            elif stat == "freeze_chance":
                lines.append(f"  ❄️ Шанс заморозки: +{value}%")
            elif stat == "life_on_hit":
                lines.append(f"  🩸 Вампиризм: +{value}")
            elif stat == "crit_chance":
                lines.append(f"  🔥 Шанс крита: +{value}%")
            elif stat == "crit_multiplier":
                lines.append(f"  💥 Множитель крита: +{value}%")
            elif stat == "attack_speed":
                lines.append(f"  ⚡ Скорость атаки: +{value}")
            elif stat == "range_bonus":
                lines.append(f"  📏 Дальность: +{value}")
            elif stat == "stun_multiplier":
                lines.append(f"  😵 Оглушение: x{value}")
            else:
                lines.append(f"  ✨ {stat}: +{value}")
        
        return "\n".join(lines)


# ============= КЛАСС ФЛАСКИ =============

class Flask(Item):
    """Класс для фласок здоровья"""
    
    def __init__(self, flask_type):
        flask_data = FLASKS[flask_type]
        
        super().__init__(flask_data["name"], ItemType.FLASK, flask_data["rarity"])
        
        self.flask_type = flask_type
        self.flask_data = flask_data
        self.current_uses = flask_data["uses"]
        self.emoji = flask_data.get("emoji", "🧪")
    
    def use(self):
        """Использовать фласку"""
        if self.current_uses > 0:
            self.current_uses -= 1
            return self.flask_data["heal"]
        return 0
    
    def get_status(self):
        """Возвращает короткий статус для боя"""
        charges = "█" * self.current_uses + "░" * (self.flask_data["uses"] - self.current_uses)
        return f"{self.get_rarity_emoji()}{self.emoji} {self.flask_data['heal']}HP [{charges}]"
    
    def _get_base_stats_string(self):
        """Возвращает строку с характеристиками фласки"""
        heal_emoji = "💚" if self.flask_data["heal"] < 50 else "💛" if self.flask_data["heal"] < 100 else "❤️"
        charges_emoji = "🔋" * self.current_uses + "⚪" * (self.flask_data["uses"] - self.current_uses)
        
        return (
            f"**Параметры:**\n"
            f"  {heal_emoji} Лечение: +{self.flask_data['heal']} HP\n"
            f"  {charges_emoji} Заряды: {self.current_uses}/{self.flask_data['uses']}"
        )
    
    def get_detailed_info(self):
        """Возвращает подробную информацию о фласке"""
        lines = []
        
        lines.append(f"{self.get_rarity_emoji()} **{self.name}**")
        lines.append(f"└ {self.get_rarity_name()} {self.emoji} Фласка")
        lines.append("")
        lines.append(self._get_base_stats_string())
        
        return "\n".join(lines)


# ============= ФУНКЦИИ ГЕНЕРАЦИИ =============

def generate_melee_weapon(item_level, monster_rarity="common", force_tier=None):
    """Генерирует случайное оружие ближнего боя"""
    
    # Словарь оружия по тирам
    tier_weapons = {
        1: ["rusted_sword", "driftwood_club", "rusty_hatchet", "nail_claw", 
            "glass_dagger", "driftwood_sceptre", "driftwood_maul", "wooden_staff",
            "bamboo_staff", "wooden_spear", "corroded_blade", "stone_axe"],
        2: ["copper_sword", "spiked_club", "jade_axe", "chain_flail",
            "stone_hammer", "poison_dagger"],
        3: ["saber", "boarding_axe", "shark_claw", "bronze_sceptre", 
            "bastard_sword", "jade_chopper", "great_maul", "iron_staff",
            "iron_quarterstaff", "iron_spear"],
        4: ["broad_sword", "pirate_cutlass", "cleaver", "war_hammer",
            "assassin_dagger", "iron_sceptre", "war_flail"],
        5: ["war_sword", "plated_mace", "carpenter_axe", "eagle_claw",
            "ritual_sceptre", "claymore", "labrys", "brass_hammer", 
            "mystic_staff", "monk_staff", "javelin"],
        6: ["ancient_sword", "gladius", "ceremonial_mace", "battle_axe",
            "gut_ripper", "morning_star"],
        7: ["elegant_sword", "decorative_axe", "glimmer_mace", "demon_claw",
            "crystal_sceptre", "executioner_sword", "ezomite_axe", "gavel",
            "harpoon"],
        8: ["twilight_blade", "estoc", "savage_axe", "vision_mace",
            "imperial_dagger", "dragon_staff", "wind_staff", "holy_flail"],
        9: ["gem_sword", "worm_mace", "ghost_axe", "void_claw",
            "void_sceptre", "lion_sword", "vaal_axe", "colossus_hammer",
            "dragonspine_spear"],
        10: ["eternal_sword", "tiger_hook", "demon_axe", "dragon_mace",
             "sai", "alternating_sceptre", "despot_axe"]
    }
    
    # Определяем максимальный доступный тир на основе ilvl
    max_tier_by_ilvl = min(10, max(1, item_level // 5))
    
    if force_tier:
        tier = min(force_tier, max_tier_by_ilvl)
    else:
        # Случайный тир, но не выше максимального
        possible_tiers = list(range(1, max_tier_by_ilvl + 1))
        weights = [1/(t**2) for t in possible_tiers]  # Более высокие тиры реже
        total = sum(weights)
        weights = [w/total for w in weights]
        tier = random.choices(possible_tiers, weights=weights)[0]
    
    # Выбираем случайное оружие этого тира
    weapons_of_tier = tier_weapons.get(tier, tier_weapons[1])
    weapon_id = random.choice(weapons_of_tier)
    
    # Определяем редкость предмета
    rarity_bonus = {
        "common": 0,
        "magic": 10,
        "rare": 20,
        "boss": 30
    }.get(monster_rarity, 0)
    
    rarity_roll = random.random() * 100 + rarity_bonus
    
    if rarity_roll < 50:
        item_rarity = ItemRarity.NORMAL
    elif rarity_roll < 80:
        item_rarity = ItemRarity.MAGIC
    elif rarity_roll < 95:
        item_rarity = ItemRarity.RARE
    else:
        # Шанс на уникальное оружие
        unique_chance = min(30, item_level // 2)
        if random.random() * 100 < unique_chance:
            unique_id = random.choice(list(UNIQUE_WEAPONS.keys()))
            return UniqueWeapon(unique_id, item_level)
        else:
            item_rarity = ItemRarity.RARE
    
    weapon = MeleeWeapon(weapon_id, item_rarity, item_level)
    
    # Добавляем качество (0-20%)
    quality_chance = 0.3 + (item_level / 200)
    if random.random() < quality_chance:
        max_quality = min(20, 5 + item_level // 5)
        weapon.quality = random.randint(5, max_quality)
    
    # Добавляем аффиксы
    if item_rarity == ItemRarity.MAGIC:
        # Магические: 1 аффикс
        if random.choice([True, False]):
            affix = random.choice(list(PREFIXES.values()))
            weapon.add_affix(affix, AffixType.PREFIX)
        else:
            affix = random.choice(list(SUFFIXES.values()))
            weapon.add_affix(affix, AffixType.SUFFIX)
    
    elif item_rarity == ItemRarity.RARE:
        # Редкие: 2-4 аффикса
        num_affixes = random.randint(2, min(4, 2 + item_level // 10))
        for _ in range(num_affixes):
            if random.choice([True, False]):
                # Выбираем аффикс подходящего тира
                possible_prefixes = [a for a in PREFIXES.values() if a["tier"] <= max_tier_by_ilvl]
                if possible_prefixes:
                    affix = random.choice(possible_prefixes)
                    weapon.add_affix(affix, AffixType.PREFIX)
            else:
                possible_suffixes = [a for a in SUFFIXES.values() if a["tier"] <= max_tier_by_ilvl]
                if possible_suffixes:
                    affix = random.choice(possible_suffixes)
                    weapon.add_affix(affix, AffixType.SUFFIX)
    
    # Генерируем имя на основе аффиксов
    if weapon.affixes:
        prefixes = [a for t, a in weapon.affixes if t == AffixType.PREFIX]
        suffixes = [a for t, a in weapon.affixes if t == AffixType.SUFFIX]
        
        name_parts = []
        if prefixes:
            name_parts.append(random.choice(prefixes)["name"])
        name_parts.append(WEAPON_BASES[weapon_id]["name"])
        if suffixes:
            name_parts.append(random.choice(suffixes)["name"])
        
        weapon.name = " ".join(name_parts)
    
    return weapon


def generate_flask():
    """Генерирует случайную фласку"""
    roll = random.random() * 100
    
    if roll < 60:
        flask_type = "small_life"
    elif roll < 85:
        flask_type = "medium_life"
    elif roll < 97:
        flask_type = "large_life"
    else:
        flask_type = "divine_life"
    
    return Flask(flask_type)


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_item_generation():
    """Тест генерации предметов"""
    print("=" * 50)
    print("ТЕСТ ГЕНЕРАЦИИ ПРЕДМЕТОВ")
    print("=" * 50)
    
    # Обычное оружие
    print("\n🔹 Обычное оружие (ilvl 5):")
    weapon = generate_melee_weapon(5, "common")
    print(weapon.get_detailed_info())
    
    # Магическое оружие
    print("\n🔸 Магическое оружие (ilvl 10):")
    weapon = generate_melee_weapon(10, "magic")
    print(weapon.get_detailed_info())
    
    # Редкое оружие
    print("\n🔹 Редкое оружие (ilvl 15):")
    weapon = generate_melee_weapon(15, "rare")
    print(weapon.get_detailed_info())
    
    # Уникальное оружие
    print("\n🔸 Уникальное оружие:")
    unique = UniqueWeapon("soul_ripper", 20)
    print(unique.get_detailed_info())
    
    # Фласка
    print("\n🧪 Фласка:")
    flask = generate_flask()
    print(flask.get_detailed_info())


def test_weapon_scaling():
    """Тест масштабирования оружия"""
    print("=" * 50)
    print("ТЕСТ МАСШТАБИРОВАНИЯ ОРУЖИЯ")
    print("=" * 50)
    
    base_weapon_id = "copper_sword"
    
    for ilvl in [1, 10, 20, 30]:
        print(f"\nУровень предмета: {ilvl}")
        print("-" * 30)
        
        weapon = MeleeWeapon(base_weapon_id, ItemRarity.RARE, ilvl)
        min_dmg, max_dmg = weapon.get_damage_range()
        print(f"Урон: {min_dmg}-{max_dmg}")
        print(f"Требования: {weapon.get_requirements_string()}")


if __name__ == "__main__":
    test_item_generation()
    print("\n")
    test_weapon_scaling()
