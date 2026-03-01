import math
import random
import time
from enum import Enum
from models.player import Player
from models.quest import QuestManager, QuestStatus
from data.act1 import Act1

# ============= ТИПЫ ПРОГРЕССИИ =============

class ProgressionType(Enum):
    LEVEL = "level"              # Уровень игрока
    ACT = "act"                   # Акт
    LOCATION = "location"         # Локация
    QUEST = "quest"               # Квест
    REPUTATION = "reputation"     # Репутация
    ACHIEVEMENT = "achievement"   # Достижение
    MASTERY = "mastery"           # Мастерство


# ============= КЛАСС УРОВНЯ =============

class LevelSystem:
    """Система уровней игрока"""
    
    def __init__(self, player):
        self.player = player
    
    def get_exp_for_level(self, level):
        """Возвращает опыт, необходимый для уровня"""
        # Формула: 100 * level^2
        return 100 * (level ** 2)
    
    def get_exp_for_next_level(self):
        """Возвращает опыт для следующего уровня"""
        return self.get_exp_for_level(self.player.level)
    
    def get_exp_progress(self):
        """Возвращает прогресс до следующего уровня"""
        current_level_exp = self.get_exp_for_level(self.player.level - 1) if self.player.level > 1 else 0
        next_level_exp = self.get_exp_for_level(self.player.level)
        
        exp_in_level = self.player.exp - current_level_exp
        exp_needed = next_level_exp - current_level_exp
        
        return exp_in_level, exp_needed
    
    def get_exp_percent(self):
        """Возвращает процент прогресса уровня"""
        exp_in_level, exp_needed = self.get_exp_progress()
        if exp_needed == 0:
            return 100
        return int((exp_in_level / exp_needed) * 100)
    
    def get_exp_bar(self, length=10):
        """Возвращает визуальную полоску опыта"""
        percent = self.get_exp_percent()
        filled = int((percent / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"✨ {bar} {percent}%"
    
    def add_exp(self, amount):
        """Добавляет опыт и проверяет повышение уровня"""
        self.player.exp += amount
        levels_gained = 0
        
        while self.player.exp >= self.get_exp_for_level(self.player.level):
            self.level_up()
            levels_gained += 1
        
        return levels_gained
    
    def level_up(self):
        """Повышает уровень игрока"""
        self.player.level += 1
        self.player.max_hp += 10
        self.player.hp = self.player.max_hp
        
        # Повышение атрибутов
        self.player.strength += 2
        self.player.dexterity += 2
        self.player.intelligence += 2
        
        # Небольшое повышение характеристик
        self.player.accuracy += 1
        self.player.crit_chance += 0.5
        
        return self.player.level


# ============= СИСТЕМА АКТОВ =============

class ActSystem:
    """Система актов игры"""
    
    def __init__(self, player):
        self.player = player
        
        # Данные по актам
        self.acts = {
            1: {
                "name": "Падший",
                "name_en": "The Fallen",
                "min_level": 1,
                "max_level": 10,
                "locations": [1, 2, 3, 4, 5, 6, 7],
                "start_location": 1,
                "haven_location": 2,
                "boss_location": 7,
                "boss_name": "Древний спрут",
                "description": "Тебя сбросили в темницу за преступления, которых ты не совершал. Найди выход из подземелья."
            },
            2: {
                "name": "Пески забвения",
                "name_en": "Sands of Oblivion",
                "min_level": 10,
                "max_level": 20,
                "locations": [8, 9, 10, 11, 12, 13, 14],
                "start_location": 8,
                "haven_location": 9,
                "boss_location": 14,
                "boss_name": "Повелитель песков",
                "description": "Ты выбрался из подземелья, но попал в пустыню. Впереди древние гробницы и города-призраки."
            }
        }
    
    def get_current_act(self):
        """Возвращает текущий акт"""
        return self.acts.get(self.player.act, self.acts[1])
    
    def get_act_name(self):
        """Возвращает название текущего акта"""
        act = self.get_current_act()
        return f"Акт {self.player.act}: {act['name']}"
    
    def can_proceed_to_next_act(self):
        """Проверяет, может ли игрок перейти к следующему акту"""
        # Проверка уровня
        if self.player.level < self.get_current_act()["max_level"]:
            return False, "Уровень недостаточно высок"
        
        # Проверка, что игрок убил босса акта
        # Здесь должна быть проверка квеста
        
        return True, "Можно перейти к следующему акту"
    
    def go_to_next_act(self):
        """Переходит к следующему акту"""
        can_proceed, message = self.can_proceed_to_next_act()
        if not can_proceed:
            return False, message
        
        self.player.act += 1
        next_act = self.acts.get(self.player.act)
        
        if next_act:
            self.player.current_location = next_act["start_location"]
            self.player.position_in_location = 0
            self.player.hp = self.player.max_hp
            
            # Сброс фласок
            for flask in self.player.flasks:
                flask.current_uses = flask.flask_data["uses"]
            
            return True, f"Ты перешел в Акт {self.player.act}: {next_act['name']}"
        else:
            return False, "Это был последний акт. Поздравляю с прохождением!"


# ============= СИСТЕМА ЛОКАЦИЙ =============

class LocationSystem:
    """Система локаций"""
    
    def __init__(self, player):
        self.player = player
    
    def get_current_location(self):
        """Возвращает текущую локацию"""
        if self.player.act == 1:
            return Act1.get_location_by_id(self.player.current_location)
        # Для других актов будут свои классы
        return None
    
    def get_location_name(self):
        """Возвращает название текущей локации"""
        location = self.get_current_location()
        if location:
            return location["name"]
        return "Неизвестная локация"
    
    def get_location_description(self):
        """Возвращает описание текущей локации"""
        location = self.get_current_location()
        if location:
            return location["description"]
        return ""
    
    def get_area_level(self):
        """Возвращает уровень локации"""
        location = self.get_current_location()
        if location:
            return location["area_level"]
        return 1
    
    def get_next_location(self):
        """Возвращает следующую локацию"""
        location = self.get_current_location()
        if location and location["next_location"]:
            if self.player.act == 1:
                return Act1.get_location_by_id(location["next_location"])
        return None
    
    def can_move_to_next_location(self, total_events):
        """Проверяет, может ли игрок перейти в следующую локацию"""
        return self.player.is_at_end_of_location(total_events)
    
    def move_to_next_location(self):
        """Переходит в следующую локацию"""
        next_loc = self.get_next_location()
        if next_loc:
            self.player.current_location = next_loc["id"]
            self.player.position_in_location = 0
            return True, f"Ты перешел в {next_loc['name']}"
        return False, "Дальше пути нет"
    
    def is_safe_haven(self):
        """Проверяет, является ли текущая локация убежищем"""
        location = self.get_current_location()
        return location and location.get("is_safe", False)
    
    def is_boss_location(self):
        """Проверяет, есть ли в локации босс"""
        location = self.get_current_location()
        return location and location.get("has_boss", False)


# ============= СИСТЕМА РЕПУТАЦИИ =============

class ReputationSystem:
    """Система репутации с фракциями"""
    
    def __init__(self, player):
        self.player = player
        self.reputation = {
            "haven": 0,      # Жители убежища
            "merchants": 0,  # Торговцы
            "fighters": 0,   # Воины/наемники
            "mages": 0,      # Маги
            "thieves": 0     # Воры/разбойники
        }
        
        # Уровни репутации
        self.levels = {
            0: "Враг",
            500: "Нейтралитет",
            1000: "Знакомый",
            2000: "Друг",
            5000: "Союзник",
            10000: "Герой"
        }
    
    def add_reputation(self, faction, amount):
        """Добавляет репутацию с фракцией"""
        if faction in self.reputation:
            self.reputation[faction] += amount
            return self.get_reputation_level(faction)
        return None
    
    def get_reputation_level(self, faction):
        """Возвращает уровень репутации с фракцией"""
        rep = self.reputation.get(faction, 0)
        
        for threshold, level_name in sorted(self.levels.items()):
            if rep >= threshold:
                current_level = level_name
        
        return current_level
    
    def get_reputation_discount(self, faction):
        """Возвращает скидку у торговцев фракции"""
        rep = self.reputation.get(faction, 0)
        
        if rep >= 10000:
            return 0.7  # 30% скидка
        elif rep >= 5000:
            return 0.8  # 20% скидка
        elif rep >= 2000:
            return 0.85  # 15% скидка
        elif rep >= 1000:
            return 0.9   # 10% скидка
        elif rep >= 500:
            return 0.95  # 5% скидка
        
        return 1.0  # Нет скидки
    
    def get_reputation_string(self):
        """Возвращает строку с репутацией"""
        lines = ["⭐ **РЕПУТАЦИЯ**\n"]
        
        factions = {
            "haven": "🏚️ Убежище",
            "merchants": "🛒 Торговцы",
            "fighters": "⚔️ Воины",
            "mages": "🔮 Маги",
            "thieves": "🗡️ Воры"
        }
        
        for faction, name in factions.items():
            rep = self.reputation.get(faction, 0)
            level = self.get_reputation_level(faction)
            lines.append(f"{name}: {rep} ({level})")
        
        return "\n".join(lines)


# ============= СИСТЕМА ДОСТИЖЕНИЙ =============

class Achievement:
    """Достижение"""
    
    def __init__(self, ach_id, name, description, condition, reward=None):
        self.id = ach_id
        self.name = name
        self.description = description
        self.condition = condition  # Функция проверки
        self.reward = reward or {}
        self.completed = False
        self.completed_at = None


class AchievementSystem:
    """Система достижений"""
    
    def __init__(self, player):
        self.player = player
        self.achievements = {}
        self._init_achievements()
    
    def _init_achievements(self):
        """Инициализирует достижения"""
        
        # Боевые достижения
        self.achievements["first_kill"] = Achievement(
            "first_kill",
            "Первая кровь",
            "Убей своего первого врага",
            lambda p: p.total_kills >= 1,
            {"exp": 50, "gold": 10}
        )
        
        self.achievements["killer_10"] = Achievement(
            "killer_10",
            "Убийца",
            "Убей 10 врагов",
            lambda p: p.total_kills >= 10,
            {"exp": 100, "gold": 50}
        )
        
        self.achievements["killer_100"] = Achievement(
            "killer_100",
            "Массовый убийца",
            "Убей 100 врагов",
            lambda p: p.total_kills >= 100,
            {"exp": 500, "gold": 200}
        )
        
        self.achievements["first_boss"] = Achievement(
            "first_boss",
            "Победитель босса",
            "Убей первого босса",
            lambda p: p.quests.get("quest3", {}).get("status") == "completed",
            {"exp": 200, "gold": 100}
        )
        
        # Прогрессия
        self.achievements["level_5"] = Achievement(
            "level_5",
            "Новичок",
            "Достигни 5 уровня",
            lambda p: p.level >= 5,
            {"exp": 100, "gold": 50}
        )
        
        self.achievements["level_10"] = Achievement(
            "level_10",
            "Опытный",
            "Достигни 10 уровня",
            lambda p: p.level >= 10,
            {"exp": 300, "gold": 150}
        )
        
        self.achievements["level_20"] = Achievement(
            "level_20",
            "Ветеран",
            "Достигни 20 уровня",
            lambda p: p.level >= 20,
            {"exp": 1000, "gold": 500}
        )
        
        # Исследование
        self.achievements["explorer"] = Achievement(
            "explorer",
            "Исследователь",
            "Посети 5 разных локаций",
            lambda p: len(p.visited_locations) >= 5,
            {"exp": 150, "gold": 75}
        )
        
        self.achievements["well_traveled"] = Achievement(
            "well_traveled",
            "Путешественник",
            "Посети все локации акта 1",
            lambda p: len(p.visited_locations) >= 7,
            {"exp": 300, "gold": 150}
        )
        
        # Квесты
        self.achievements["quest_master"] = Achievement(
            "quest_master",
            "Мастер квестов",
            "Выполни все основные квесты акта 1",
            lambda p: all(p.quests[q]["status"] == "completed" for q in ["quest1", "quest2", "quest3"]),
            {"exp": 500, "gold": 250}
        )
        
        self.achievements["helping_hand"] = Achievement(
            "helping_hand",
            "Помощник",
            "Выполни все побочные квесты акта 1",
            lambda p: all(p.quests[q]["status"] == "completed" for q in ["side_quest1", "side_quest2"]),
            {"exp": 300, "gold": 150}
        )
        
        # Экономика
        self.achievements["rich"] = Achievement(
            "rich",
            "Богач",
            "Накопи 1000 золота",
            lambda p: p.gold >= 1000,
            {"exp": 200, "gold": 100}
        )
        
        self.achievements["millionaire"] = Achievement(
            "millionaire",
            "Миллионер",
            "Накопи 10000 золота",
            lambda p: p.gold >= 10000,
            {"exp": 1000, "gold": 500}
        )
        
        # Экипировка
        self.achievements["well_equipped"] = Achievement(
            "well_equipped",
            "Экипированный",
            "Экипируй предмет во все слоты",
            lambda p: all(p.equipped.values()),
            {"exp": 150, "gold": 75}
        )
        
        self.achievements["rare_collector"] = Achievement(
            "rare_collector",
            "Коллекционер",
            "Найди редкий предмет",
            lambda p: any(item.rarity.value == "rare" for item in p.inventory),
            {"exp": 200, "gold": 100}
        )
        
        self.achievements["unique_finder"] = Achievement(
            "unique_finder",
            "Охотник за уникальным",
            "Найди уникальный предмет",
            lambda p: any(item.rarity.value == "unique" for item in p.inventory),
            {"exp": 500, "gold": 250}
        )
    
    def check_achievements(self):
        """Проверяет выполнение достижений"""
        completed = []
        
        for ach_id, achievement in self.achievements.items():
            if not achievement.completed and achievement.condition(self.player):
                achievement.completed = True
                achievement.completed_at = time.time()
                completed.append(achievement)
        
        return completed
    
    def get_achievement_progress(self):
        """Возвращает прогресс достижений"""
        total = len(self.achievements)
        completed = sum(1 for a in self.achievements.values() if a.completed)
        return completed, total
    
    def get_achievements_string(self):
        """Возвращает строку с достижениями"""
        lines = ["🏆 **ДОСТИЖЕНИЯ**\n"]
        
        completed, total = self.get_achievement_progress()
        lines.append(f"Прогресс: {completed}/{total}\n")
        
        # Показываем последние выполненные
        recent = [a for a in self.achievements.values() if a.completed][-5:]
        if recent:
            lines.append("**Недавние:**")
            for ach in recent:
                lines.append(f"  ✅ {ach.name} - {ach.description}")
        
        # Показываем ближайшие
        upcoming = [a for a in self.achievements.values() if not a.completed][:3]
        if upcoming:
            lines.append("\n**В процессе:**")
            for ach in upcoming:
                lines.append(f"  ⏳ {ach.name} - {ach.description}")
        
        return "\n".join(lines)


# ============= СИСТЕМА МАСТЕРСТВА =============

class MasteryNode:
    """Узел мастерства"""
    
    def __init__(self, node_id, name, description, cost, requirements=None, effects=None):
        self.id = node_id
        self.name = name
        self.description = description
        self.cost = cost  # Очки мастерства
        self.requirements = requirements or []  # Требуемые узлы
        self.effects = effects or {}  # Эффекты
        self.unlocked = False


class MasterySystem:
    """Система мастерства (дерево талантов)"""
    
    def __init__(self, player):
        self.player = player
        self.points = 0
        self.nodes = {}
        self._init_tree()
    
    def _init_tree(self):
        """Инициализирует дерево мастерства"""
        
        # Воинское дерево
        self.nodes["warrior_1"] = MasteryNode(
            "warrior_1",
            "Сила воина",
            "Увеличивает силу на 5",
            1,
            effects={"strength": 5}
        )
        
        self.nodes["warrior_2"] = MasteryNode(
            "warrior_2",
            "Крепкая броня",
            "Увеличивает защиту на 3",
            1,
            ["warrior_1"],
            {"defense": 3}
        )
        
        self.nodes["warrior_3"] = MasteryNode(
            "warrior_3",
            "Ярость",
            "Увеличивает урон на 10%",
            2,
            ["warrior_2"],
            {"damage": 10}
        )
        
        self.nodes["warrior_4"] = MasteryNode(
            "warrior_4",
            "Берсерк",
            "Шанс критического удара +5%",
            2,
            ["warrior_3"],
            {"crit_chance": 5}
        )
        
        # Ловкаческое дерево
        self.nodes["rogue_1"] = MasteryNode(
            "rogue_1",
            "Ловкость рук",
            "Увеличивает ловкость на 5",
            1,
            effects={"dexterity": 5}
        )
        
        self.nodes["rogue_2"] = MasteryNode(
            "rogue_2",
            "Точность",
            "Увеличивает точность на 5%",
            1,
            ["rogue_1"],
            {"accuracy": 5}
        )
        
        self.nodes["rogue_3"] = MasteryNode(
            "rogue_3",
            "Уклонение",
            "Шанс уклониться +5%",
            2,
            ["rogue_2"],
            {"dodge": 5}
        )
        
        # Магическое дерево
        self.nodes["mage_1"] = MasteryNode(
            "mage_1",
            "Интеллект",
            "Увеличивает интеллект на 5",
            1,
            effects={"intelligence": 5}
        )
        
        self.nodes["mage_2"] = MasteryNode(
            "mage_2",
            "Магическая защита",
            "Сопротивление стихиям +5%",
            1,
            ["mage_1"],
            {"all_res": 5}
        )
        
        # Общие узлы
        self.nodes["vitality_1"] = MasteryNode(
            "vitality_1",
            "Живучесть",
            "Увеличивает максимальное HP на 20",
            1,
            effects={"max_hp": 20}
        )
        
        self.nodes["vitality_2"] = MasteryNode(
            "vitality_2",
            "Регенерация",
            "Восстанавливает 2 HP в ход",
            2,
            ["vitality_1"],
            {"life_regen": 2}
        )
        
        self.nodes["greed_1"] = MasteryNode(
            "greed_1",
            "Жадность",
            "На 10% больше золота с врагов",
            1,
            effects={"gold_find": 10}
        )
        
        self.nodes["luck_1"] = MasteryNode(
            "luck_1",
            "Удача",
            "На 5% больше шанс найти редкие предметы",
            2,
            effects={"rarity_find": 5}
        )
    
    def add_point(self):
        """Добавляет очко мастерства"""
        self.points += 1
    
    def can_unlock(self, node_id):
        """Проверяет, можно ли разблокировать узел"""
        node = self.nodes.get(node_id)
        if not node or node.unlocked:
            return False
        
        if self.points < node.cost:
            return False
        
        # Проверка требований
        for req_id in node.requirements:
            req_node = self.nodes.get(req_id)
            if not req_node or not req_node.unlocked:
                return False
        
        return True
    
    def unlock_node(self, node_id):
        """Разблокирует узел мастерства"""
        if not self.can_unlock(node_id):
            return False, "Невозможно разблокировать"
        
        node = self.nodes[node_id]
        node.unlocked = True
        self.points -= node.cost
        
        # Применяем эффекты
        for stat, value in node.effects.items():
            if hasattr(self.player, stat):
                current = getattr(self.player, stat)
                setattr(self.player, stat, current + value)
        
        return True, f"Разблокировано: {node.name}"
    
    def get_tree_string(self):
        """Возвращает строку с деревом мастерства"""
        lines = ["🌳 **ДЕРЕВО МАСТЕРСТВА**\n"]
        lines.append(f"✨ Доступно очков: {self.points}\n")
        
        categories = {
            "warrior": "⚔️ Воин",
            "rogue": "🗡️ Разбойник",
            "mage": "🔮 Маг",
            "vitality": "❤️ Живучесть",
            "greed": "💰 Алчность"
        }
        
        for prefix, category_name in categories.items():
            lines.append(f"\n**{category_name}:**")
            for node_id, node in self.nodes.items():
                if node_id.startswith(prefix):
                    status = "✅" if node.unlocked else "🔒" if self.can_unlock(node_id) else "⏳"
                    lines.append(f"  {status} {node.name} ({node.cost}) - {node.description}")
        
        return "\n".join(lines)


# ============= ОСНОВНАЯ СИСТЕМА ПРОГРЕССИИ =============

class ProgressionSystem:
    """Основная система прогрессии"""
    
    def __init__(self, player):
        self.player = player
        self.level = LevelSystem(player)
        self.acts = ActSystem(player)
        self.locations = LocationSystem(player)
        self.reputation = ReputationSystem(player)
        self.achievements = AchievementSystem(player)
        self.mastery = MasterySystem(player)
        self.quest_manager = None  # Будет установлен позже
    
    def set_quest_manager(self, quest_manager):
        """Устанавливает менеджер квестов"""
        self.quest_manager = quest_manager
    
    def update_progression(self):
        """Обновляет прогрессию (вызывается после событий)"""
        results = []
        
        # Проверка достижений
        new_achievements = self.achievements.check_achievements()
        for ach in new_achievements:
            results.append(("achievement", ach))
        
        # Проверка уровня
        # (уже обновляется при добавлении опыта)
        
        # Проверка квестов
        if self.quest_manager:
            # Здесь можно добавить логику
            pass
        
        return results
    
    def get_progression_string(self):
        """Возвращает строку с прогрессией"""
        location = self.locations.get_current_location()
        location_name = location["name"] if location else "Неизвестно"
        
        exp_in_level, exp_needed = self.level.get_exp_progress()
        
        completed_achievements, total_achievements = self.achievements.get_achievement_progress()
        
        return (
            f"📈 **ПРОГРЕССИЯ**\n\n"
            f"{self.acts.get_act_name()}\n"
            f"📍 Локация: {location_name}\n"
            f"👤 Уровень: {self.player.level}\n"
            f"{self.level.get_exp_bar()}\n"
            f"✨ Опыт: {self.player.exp}/{self.level.get_exp_for_level(self.player.level)}\n"
            f"🏆 Достижения: {completed_achievements}/{total_achievements}\n"
            f"🌳 Очки мастерства: {self.mastery.points}\n"
            f"💰 Золото: {self.player.gold}"
        )
    
    def get_detailed_progression(self):
        """Возвращает детальную прогрессию"""
        return (
            f"{self.get_progression_string()}\n\n"
            f"{self.reputation.get_reputation_string()}\n\n"
            f"{self.achievements.get_achievements_string()}\n\n"
            f"{self.mastery.get_tree_string()}"
        )


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_progression_system():
    """Тест системы прогрессии"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМЫ ПРОГРЕССИИ")
    print("=" * 50)
    
    # Создаем тестового игрока
    player = Player()
    progression = ProgressionSystem(player)
    
    print("\n🔹 Начальное состояние:")
    print(progression.get_progression_string())
    
    # Добавляем опыт
    print("\n🔸 Добавляем 150 опыта:")
    levels = progression.level.add_exp(150)
    print(f"Получено уровней: {levels}")
    print(progression.get_progression_string())
    
    # Проверяем достижения
    print("\n🔸 Проверка достижений:")
    player.total_kills = 10
    new_ach = progression.achievements.check_achievements()
    for ach in new_ach:
        print(f"  ✅ {ach.name} - {ach.description}")
    
    # Тест мастерства
    print("\n🔸 Система мастерства:")
    print(progression.mastery.get_tree_string())
    
    # Разблокируем узел
    progression.mastery.points = 3
    success, msg = progression.mastery.unlock_node("warrior_1")
    print(f"\n{msg}")
    
    success, msg = progression.mastery.unlock_node("warrior_2")
    print(msg)
    
    print("\n🔸 После разблокировки:")
    print(progression.mastery.get_tree_string())
    
    # Тест репутации
    print("\n🔸 Репутация:")
    progression.reputation.add_reputation("haven", 600)
    print(progression.reputation.get_reputation_string())


if __name__ == "__main__":
    test_progression_system()
