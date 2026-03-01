from enum import Enum
import random
from data.act1 import Act1

# ============= ТИПЫ КВЕСТОВ =============

class QuestType(Enum):
    MAIN = "main"           # Основной квест
    SIDE = "side"           # Побочный квест
    DAILY = "daily"         # Ежедневный квест
    REPEATABLE = "repeat"   # Повторяемый квест

class QuestStatus(Enum):
    LOCKED = "locked"       # Заблокирован
    AVAILABLE = "available" # Доступен для взятия
    ACTIVE = "active"       # Взят и выполняется
    COMPLETED = "completed" # Выполнен
    FAILED = "failed"       # Провален

class ObjectiveType(Enum):
    KILL_MONSTERS = "kill_monsters"     # Убить монстров
    KILL_BOSS = "kill_boss"             # Убить босса
    FIND_ITEM = "find_item"             # Найти предмет
    TALK_TO_NPC = "talk_to_npc"         # Поговорить с NPC
    REACH_LOCATION = "reach_location"   # Достичь локации
    RESCUE = "rescue"                   # Спасти кого-то
    ESCORT = "escort"                   # Сопроводить
    COLLECT = "collect"                  # Собрать ресурсы
    USE_ITEM = "use_item"                # Использовать предмет
    CRAFT = "craft"                      # Создать предмет
    EXPLORE = "explore"                   # Исследовать


# ============= КЛАСС ЦЕЛИ КВЕСТА =============

class QuestObjective:
    """Цель квеста"""
    
    def __init__(self, objective_data):
        self.type = ObjectiveType(objective_data["type"])
        self.required = objective_data.get("required", 1)
        self.progress = objective_data.get("progress", 0)
        self.description = objective_data.get("description", "")
        self.location_id = objective_data.get("location")
        self.target = self._get_target(objective_data)
        self.completed = False
        
        # Дополнительные параметры
        self.monster_name = objective_data.get("monster")
        self.boss_name = objective_data.get("boss")
        self.item_name = objective_data.get("item")
        self.npc_name = objective_data.get("npc")
        self.target_name = objective_data.get("target")
    
    def _get_target(self, data):
        """Определяет цель квеста"""
        if "monster" in data:
            return data["monster"]
        elif "boss" in data:
            return data["boss"]
        elif "item" in data:
            return data["item"]
        elif "npc" in data:
            return data["npc"]
        elif "target" in data:
            return data["target"]
        return None
    
    def update_progress(self, amount=1):
        """Обновляет прогресс цели"""
        self.progress = min(self.progress + amount, self.required)
        if self.progress >= self.required:
            self.completed = True
        return self.completed
    
    def is_completed(self):
        """Проверяет, выполнена ли цель"""
        return self.progress >= self.required
    
    def get_progress_string(self):
        """Возвращает строку с прогрессом"""
        if self.required > 1:
            return f"{self.progress}/{self.required}"
        else:
            return "✅" if self.completed else "❌"
    
    def get_description_string(self):
        """Возвращает описание цели"""
        if self.description:
            return self.description
        
        # Автоматическое описание на основе типа
        if self.type == ObjectiveType.KILL_MONSTERS:
            return f"Убить {self.monster_name} ({self.progress}/{self.required})"
        elif self.type == ObjectiveType.KILL_BOSS:
            return f"Убить {self.boss_name}"
        elif self.type == ObjectiveType.FIND_ITEM:
            return f"Найти {self.item_name}"
        elif self.type == ObjectiveType.TALK_TO_NPC:
            return f"Поговорить с {self.npc_name}"
        elif self.type == ObjectiveType.REACH_LOCATION:
            return f"Достичь {self.location_id}"
        elif self.type == ObjectiveType.RESCUE:
            return f"Спасти {self.target_name} ({self.progress}/{self.required})"
        elif self.type == ObjectiveType.COLLECT:
            return f"Собрать {self.target_name} ({self.progress}/{self.required})"
        
        return "Неизвестная цель"


# ============= КЛАСС НАГРАДЫ =============

class QuestReward:
    """Награда за квест"""
    
    def __init__(self, reward_data):
        self.exp = reward_data.get("exp", 0)
        self.gold = reward_data.get("gold", 0)
        self.items = reward_data.get("items", [])
        self.item = reward_data.get("item")  # Особый предмет
        self.reputation = reward_data.get("reputation", 0)
        self.unlocks = reward_data.get("unlocks", [])  # Что открывает
        
        # Дополнительные награды
        self.skill_points = reward_data.get("skill_points", 0)
        self.attribute_points = reward_data.get("attribute_points", 0)
    
    def get_reward_string(self):
        """Возвращает строку с наградами"""
        rewards = []
        
        if self.exp > 0:
            rewards.append(f"✨ {self.exp} опыта")
        if self.gold > 0:
            rewards.append(f"💰 {self.gold} золота")
        if self.items:
            for item in self.items:
                rewards.append(f"📦 {item}")
        if self.item:
            rewards.append(f"🎁 Особый предмет")
        if self.reputation > 0:
            rewards.append(f"⭐ +{self.reputation} репутации")
        if self.skill_points > 0:
            rewards.append(f"⚡ +{self.skill_points} очков навыков")
        if self.attribute_points > 0:
            rewards.append(f"📈 +{self.attribute_points} очков атрибутов")
        
        return ", ".join(rewards) if rewards else "Нет наград"


# ============= КЛАСС КВЕСТА =============

class Quest:
    """Класс квеста"""
    
    def __init__(self, quest_id, quest_data):
        self.id = quest_id
        self.name = quest_data["name"]
        self.giver = quest_data.get("giver", "Неизвестно")
        self.giver_id = quest_data.get("giver_id")
        self.description = quest_data.get("description", "")
        
        # Тип квеста
        quest_type = quest_data.get("type", "main")
        self.type = QuestType(quest_type) if isinstance(quest_type, str) else quest_type
        
        # Статус
        self.status = QuestStatus.AVAILABLE
        
        # Цели
        self.objectives = []
        for obj_data in quest_data.get("objectives", []):
            self.objectives.append(QuestObjective(obj_data))
        
        # Награды
        self.rewards = QuestReward(quest_data.get("rewards", {}))
        
        # Связи с другими квестами
        self.next_quest = quest_data.get("next_quest")
        self.prerequisites = quest_data.get("prerequisites", [])
        
        # Ограничения по уровню
        self.min_level = quest_data.get("min_level", 1)
        self.max_level = quest_data.get("max_level", 99)
        
        # Временные ограничения
        self.time_limit = quest_data.get("time_limit")  # В минутах
        self.start_time = None
        
        # Повторяемость
        self.is_repeatable = quest_data.get("is_repeatable", False)
        self.repeat_cooldown = quest_data.get("repeat_cooldown", 0)  # В минутах
        self.last_completed = None
        
        # Диалоги
        self.dialogue_start = quest_data.get("dialogue_start", "")
        self.dialogue_progress = quest_data.get("dialogue_progress", "")
        self.dialogue_complete = quest_data.get("dialogue_complete", "")
        
        # Флаг финального квеста
        self.is_final = quest_data.get("is_final", False)
    
    def is_available(self, player_level=1, completed_quests=None):
        """Проверяет, доступен ли квест"""
        # Проверка уровня
        if player_level < self.min_level or player_level > self.max_level:
            return False
        
        # Проверка предусловий
        if completed_quests and self.prerequisites:
            for prereq in self.prerequisites:
                if prereq not in completed_quests:
                    return False
        
        # Проверка повторяемости
        if self.is_repeatable and self.last_completed:
            # Здесь должна быть проверка времени
            pass
        
        return True
    
    def start(self):
        """Начинает квест"""
        if self.status != QuestStatus.AVAILABLE:
            return False
        
        self.status = QuestStatus.ACTIVE
        if self.time_limit:
            import time
            self.start_time = time.time()
        
        return True
    
    def update_progress(self, objective_type, target, amount=1):
        """Обновляет прогресс квеста"""
        if self.status != QuestStatus.ACTIVE:
            return False
        
        updated = False
        for objective in self.objectives:
            if objective.type.value == objective_type:
                # Проверяем соответствие цели
                if objective.target == target or objective.target is None:
                    objective.update_progress(amount)
                    updated = True
        
        return updated
    
    def check_completion(self):
        """Проверяет, выполнен ли квест"""
        if self.status != QuestStatus.ACTIVE:
            return False
        
        for objective in self.objectives:
            if not objective.is_completed():
                return False
        
        return True
    
    def complete(self):
        """Завершает квест"""
        if not self.check_completion():
            return False, "Квест еще не выполнен"
        
        self.status = QuestStatus.COMPLETED
        import time
        self.last_completed = time.time()
        
        return True, self.rewards
    
    def fail(self):
        """Проваливает квест"""
        self.status = QuestStatus.FAILED
        return True
    
    def reset(self):
        """Сбрасывает квест (для повторяемых)"""
        if not self.is_repeatable:
            return False
        
        self.status = QuestStatus.AVAILABLE
        for objective in self.objectives:
            objective.progress = 0
            objective.completed = False
        
        return True
    
    def get_progress_string(self):
        """Возвращает строку с прогрессом квеста"""
        if self.status == QuestStatus.LOCKED:
            return "🔒 Заблокирован"
        elif self.status == QuestStatus.AVAILABLE:
            return "📜 Доступен"
        elif self.status == QuestStatus.ACTIVE:
            return "⚔️ В процессе"
        elif self.status == QuestStatus.COMPLETED:
            return "✅ Завершен"
        elif self.status == QuestStatus.FAILED:
            return "❌ Провален"
        return "❓ Неизвестно"
    
    def get_detailed_info(self):
        """Возвращает подробную информацию о квесте"""
        lines = []
        
        # Заголовок
        type_emoji = "⚔️" if self.type == QuestType.MAIN else "📜"
        lines.append(f"{type_emoji} **{self.name}**")
        lines.append(f"└ {self.get_progress_string()}")
        lines.append("")
        
        # Описание
        if self.description:
            lines.append(f"_{self.description}_")
            lines.append("")
        
        # Дающий квест
        if self.giver:
            lines.append(f"**Дает:** {self.giver}")
            lines.append("")
        
        # Цели
        if self.objectives:
            lines.append("**Цели:**")
            for i, obj in enumerate(self.objectives, 1):
                status = "✅" if obj.is_completed() else "⬜"
                lines.append(f"  {status} {obj.get_description_string()}")
            lines.append("")
        
        # Награды
        reward_str = self.rewards.get_reward_string()
        if reward_str:
            lines.append(f"**Награды:** {reward_str}")
        
        return "\n".join(lines)
    
    def get_brief_info(self):
        """Возвращает краткую информацию о квесте"""
        status_emoji = {
            QuestStatus.LOCKED: "🔒",
            QuestStatus.AVAILABLE: "📜",
            QuestStatus.ACTIVE: "⚔️",
            QuestStatus.COMPLETED: "✅",
            QuestStatus.FAILED: "❌"
        }.get(self.status, "❓")
        
        progress = ""
        if self.status == QuestStatus.ACTIVE:
            completed = sum(1 for obj in self.objectives if obj.is_completed())
            total = len(self.objectives)
            progress = f" ({completed}/{total})"
        
        return f"{status_emoji} **{self.name}**{progress}"


# ============= КЛАСС УПРАВЛЕНИЯ КВЕСТАМИ =============

class QuestManager:
    """Менеджер квестов для игрока"""
    
    def __init__(self, player):
        self.player = player
        self.quests = {}  # {quest_id: Quest}
        self.completed_quests = set()
        self.failed_quests = set()
        self.quest_log = []  # История квестов
        
        # Инициализация квестов из Act1
        self._init_quests_from_act1()
    
    def _init_quests_from_act1(self):
        """Инициализирует квесты из данных акта 1"""
        for quest_id, quest_data in Act1.QUESTS.items():
            quest = Quest(quest_id, quest_data)
            self.quests[quest_id] = quest
    
    def get_available_quests(self):
        """Возвращает список доступных квестов"""
        available = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.AVAILABLE:
                if quest.is_available(self.player.level, self.completed_quests):
                    available.append(quest)
        return available
    
    def get_active_quests(self):
        """Возвращает список активных квестов"""
        active = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.ACTIVE:
                active.append(quest)
        return active
    
    def get_completed_quests(self):
        """Возвращает список выполненных квестов"""
        completed = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.COMPLETED:
                completed.append(quest)
        return completed
    
    def accept_quest(self, quest_id):
        """Принять квест"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        quest = self.quests[quest_id]
        
        # Проверка доступности
        if quest.status != QuestStatus.AVAILABLE:
            return False, "Квест недоступен"
        
        if not quest.is_available(self.player.level, self.completed_quests):
            return False, "Не выполнены условия"
        
        # Начинаем квест
        quest.start()
        
        # Добавляем в лог
        self.quest_log.append(f"Принят квест: {quest.name}")
        
        return True, f"Квест '{quest.name}' принят"
    
    def update_quest_progress(self, objective_type, target, amount=1, location_id=None):
        """Обновляет прогресс всех активных квестов"""
        updated_quests = []
        
        for quest in self.get_active_quests():
            was_updated = quest.update_progress(objective_type, target, amount)
            
            if was_updated:
                # Проверяем выполнение
                if quest.check_completion():
                    updated_quests.append(quest)
        
        return updated_quests
    
    def complete_quest(self, quest_id):
        """Завершить квест"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        quest = self.quests[quest_id]
        
        # Завершаем квест
        success, result = quest.complete()
        
        if success:
            # Добавляем в выполненные
            self.completed_quests.add(quest_id)
            
            # Добавляем в лог
            self.quest_log.append(f"Завершен квест: {quest.name}")
            
            # Начисляем награды
            rewards = result
            self._apply_rewards(rewards)
            
            # Разблокируем следующий квест
            if quest.next_quest and quest.next_quest in self.quests:
                next_quest = self.quests[quest.next_quest]
                if next_quest.status == QuestStatus.LOCKED:
                    next_quest.status = QuestStatus.AVAILABLE
            
            return True, quest, rewards
        
        return False, result
    
    def _apply_rewards(self, rewards):
        """Применяет награды к игроку"""
        if rewards.exp > 0:
            self.player.add_exp(rewards.exp)
        
        if rewards.gold > 0:
            self.player.add_gold(rewards.gold)
        
        if rewards.skill_points > 0:
            # Добавить очки навыков
            pass
        
        if rewards.attribute_points > 0:
            # Добавить очки атрибутов
            pass
    
    def fail_quest(self, quest_id):
        """Провалить квест"""
        if quest_id not in self.quests:
            return False
        
        quest = self.quests[quest_id]
        quest.fail()
        self.failed_quests.add(quest_id)
        self.quest_log.append(f"Провален квест: {quest.name}")
        
        return True
    
    def reset_repeatable_quest(self, quest_id):
        """Сбрасывает повторяемый квест"""
        if quest_id not in self.quests:
            return False
        
        quest = self.quests[quest_id]
        return quest.reset()
    
    def get_quest_by_id(self, quest_id):
        """Получает квест по ID"""
        return self.quests.get(quest_id)
    
    def get_quests_by_giver(self, giver_id):
        """Получает квесты от конкретного NPC"""
        quests = []
        for quest in self.quests.values():
            if quest.giver_id == giver_id:
                quests.append(quest)
        return quests
    
    def get_quest_log_string(self, limit=10):
        """Возвращает строку с логом квестов"""
        if not self.quest_log:
            return "История квестов пуста"
        
        recent = self.quest_log[-limit:]
        return "\n".join(recent)
    
    def get_quests_string(self):
        """Возвращает строку со всеми квестами"""
        lines = ["📋 **ЖУРНАЛ КВЕСТОВ**\n"]
        
        # Активные квесты
        active = self.get_active_quests()
        if active:
            lines.append("**⚔️ АКТИВНЫЕ:**")
            for quest in active:
                lines.append(f"  {quest.get_brief_info()}")
            lines.append("")
        
        # Доступные квесты
        available = self.get_available_quests()
        if available:
            lines.append("**📜 ДОСТУПНЫЕ:**")
            for quest in available:
                lines.append(f"  {quest.get_brief_info()}")
            lines.append("")
        
        # Выполненные квесты
        completed = self.get_completed_quests()
        if completed:
            lines.append("**✅ ВЫПОЛНЕННЫЕ:**")
            for quest in completed[-5:]:  # Последние 5
                lines.append(f"  {quest.get_brief_info()}")
        
        if not active and not available and not completed:
            lines.append("Нет квестов")
        
        return "\n".join(lines)
    
    def get_quest_details_string(self, quest_id):
        """Возвращает детальную информацию о квесте"""
        quest = self.get_quest_by_id(quest_id)
        if not quest:
            return "Квест не найден"
        
        return quest.get_detailed_info()


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_quest_system():
    """Тест системы квестов"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМЫ КВЕСТОВ")
    print("=" * 50)
    
    # Создаем тестового игрока (упрощенно)
    class TestPlayer:
        def __init__(self):
            self.level = 1
            self.exp = 0
            self.gold = 0
        
        def add_exp(self, amount):
            self.exp += amount
            print(f"  Получено {amount} опыта")
        
        def add_gold(self, amount):
            self.gold += amount
            print(f"  Получено {amount} золота")
    
    player = TestPlayer()
    quest_manager = QuestManager(player)
    
    # Проверяем доступные квесты
    print("\n🔹 Доступные квесты:")
    for quest in quest_manager.get_available_quests():
        print(f"  - {quest.name} (от {quest.giver})")
    
    # Принимаем квест
    print("\n🔸 Принимаем квест 'Потерянный амулет':")
    success, message = quest_manager.accept_quest("quest1")
    print(f"  {message}")
    
    # Проверяем активные квесты
    print("\n🔹 Активные квесты:")
    for quest in quest_manager.get_active_quests():
        print(f"  {quest.get_detailed_info()}")
        print()
    
    # Обновляем прогресс
    print("🔸 Обновляем прогресс (найден амулет):")
    updated = quest_manager.update_quest_progress("find_item", "amulet", location_id=3)
    if updated:
        for quest in updated:
            print(f"  Квест '{quest.name}' выполнен!")
    
    # Завершаем квест
    print("\n🔸 Завершаем квест:")
    success, quest, rewards = quest_manager.complete_quest("quest1")
    if success:
        print(f"  Квест '{quest.name}' завершен!")
        print(f"  Награды: {rewards.get_reward_string()}")
    
    # Проверяем следующий квест
    print("\n🔹 Доступные квесты после завершения:")
    for quest in quest_manager.get_available_quests():
        print(f"  - {quest.name}")
    
    # Выводим журнал
    print("\n🔸 Журнал квестов:")
    print(quest_manager.get_quests_string())


if __name__ == "__main__":
    test_quest_system()
