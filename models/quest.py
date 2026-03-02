from enum import Enum
import time

# ============= ТИПЫ КВЕСТОВ =============

class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    REPEATABLE = "repeat"

class QuestStatus(Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class ObjectiveType(Enum):
    KILL_MONSTERS = "kill_monsters"
    KILL_BOSS = "kill_boss"
    FIND_ITEM = "find_item"
    TALK_TO_NPC = "talk_to_npc"
    REACH_LOCATION = "reach_location"
    RESCUE = "rescue"
    COLLECT = "collect"


# ============= ЦЕЛЬ КВЕСТА =============

class QuestObjective:
    """Цель квеста"""
    
    def __init__(self, objective_data):
        self.type = ObjectiveType(objective_data["type"])
        self.required = objective_data.get("required", 1)
        self.progress = objective_data.get("progress", 0)
        self.target = self._get_target(objective_data)
        self.location_id = objective_data.get("location")
        self.completed = False
        
        # Дополнительные параметры
        self.monster_name = objective_data.get("monster")
        self.boss_name = objective_data.get("boss")
        self.item_name = objective_data.get("item")
        self.npc_name = objective_data.get("npc")
        self.target_name = objective_data.get("target")
    
    def _get_target(self, data):
        """Определяет цель квеста"""
        return (data.get("monster") or data.get("boss") or 
                data.get("item") or data.get("npc") or data.get("target"))
    
    def update_progress(self, amount=1):
        """Обновляет прогресс"""
        self.progress = min(self.progress + amount, self.required)
        if self.progress >= self.required:
            self.completed = True
        return self.completed
    
    def is_completed(self):
        """Проверяет выполнение"""
        return self.progress >= self.required
    
    def get_description(self):
        """Возвращает описание"""
        if self.type == ObjectiveType.KILL_MONSTERS:
            return f"Убить {self.monster_name} ({self.progress}/{self.required})"
        elif self.type == ObjectiveType.KILL_BOSS:
            return f"Убить {self.boss_name}"
        elif self.type == ObjectiveType.FIND_ITEM:
            return f"Найти {self.item_name}"
        elif self.type == ObjectiveType.TALK_TO_NPC:
            return f"Поговорить с {self.npc_name}"
        elif self.type == ObjectiveType.RESCUE:
            return f"Спасти {self.target_name} ({self.progress}/{self.required})"
        return "Неизвестная цель"


# ============= НАГРАДА =============

class QuestReward:
    """Награда за квест"""
    
    def __init__(self, reward_data):
        self.exp = reward_data.get("exp", 0)
        self.gold = reward_data.get("gold", 0)
        self.item = reward_data.get("item")
        self.skill_points = reward_data.get("skill_points", 0)
    
    def get_string(self):
        """Строка с наградами"""
        rewards = []
        if self.exp > 0:
            rewards.append(f"✨ {self.exp} опыта")
        if self.gold > 0:
            rewards.append(f"💰 {self.gold} золота")
        if self.item:
            rewards.append(f"🎁 Особый предмет")
        return ", ".join(rewards) if rewards else "Нет наград"


# ============= КВЕСТ =============

class Quest:
    """Класс квеста"""
    
    def __init__(self, quest_id, quest_data):
        self.id = quest_id
        self.name = quest_data["name"]
        self.giver = quest_data.get("giver", "Неизвестно")
        self.giver_id = quest_data.get("giver_id")
        self.description = quest_data.get("description", "")
        
        self.type = QuestType(quest_data.get("type", "main"))
        self.status = QuestStatus.AVAILABLE
        
        self.objectives = [QuestObjective(obj) for obj in quest_data.get("objectives", [])]
        self.rewards = QuestReward(quest_data.get("rewards", {}))
        
        self.next_quest = quest_data.get("next_quest")
        self.prerequisites = quest_data.get("prerequisites", [])
        self.min_level = quest_data.get("min_level", 1)
        self.is_final = quest_data.get("is_final", False)
        
        self.start_time = None
        self.completed_time = None
    
    def is_available(self, player_level=1, completed_quests=None):
        """Проверяет доступность"""
        if player_level < self.min_level:
            return False
        
        if completed_quests and self.prerequisites:
            for prereq in self.prerequisites:
                if prereq not in completed_quests:
                    return False
        
        return True
    
    def start(self):
        """Начинает квест"""
        if self.status != QuestStatus.AVAILABLE:
            return False
        
        self.status = QuestStatus.ACTIVE
        self.start_time = time.time()
        return True
    
    def update_progress(self, objective_type, target, amount=1, location_id=None):
        """Обновляет прогресс"""
        if self.status != QuestStatus.ACTIVE:
            return False
        
        updated = False
        for obj in self.objectives:
            if obj.type.value == objective_type:
                # Проверяем соответствие цели и локации
                target_match = (obj.target == target or obj.target is None)
                location_match = (obj.location_id is None or obj.location_id == location_id)
                
                if target_match and location_match:
                    obj.update_progress(amount)
                    updated = True
        
        return updated
    
    def is_completed(self):
        """Проверяет выполнение"""
        return all(obj.is_completed() for obj in self.objectives)
    
    def complete(self):
        """Завершает квест"""
        if not self.is_completed():
            return False, "Квест еще не выполнен"
        
        self.status = QuestStatus.COMPLETED
        self.completed_time = time.time()
        return True, self.rewards
    
    def get_progress_string(self):
        """Строка прогресса"""
        completed = sum(1 for obj in self.objectives if obj.is_completed())
        total = len(self.objectives)
        
        status_emoji = {
            QuestStatus.LOCKED: "🔒",
            QuestStatus.AVAILABLE: "📜",
            QuestStatus.ACTIVE: "⚔️",
            QuestStatus.COMPLETED: "✅",
        }.get(self.status, "❓")
        
        if self.status == QuestStatus.ACTIVE:
            return f"{status_emoji} {self.name} ({completed}/{total})"
        return f"{status_emoji} {self.name}"
    
    def get_detailed_info(self):
        """Детальная информация"""
        lines = [f"**{self.name}**"]
        lines.append(f"└ {self.get_progress_string()}")
        lines.append("")
        
        if self.description:
            lines.append(f"_{self.description}_")
            lines.append("")
        
        lines.append("**Цели:**")
        for obj in self.objectives:
            status = "✅" if obj.is_completed() else "⬜"
            lines.append(f"  {status} {obj.get_description()}")
        
        reward_str = self.rewards.get_string()
        if reward_str:
            lines.append("")
            lines.append(f"**Награды:** {reward_str}")
        
        return "\n".join(lines)


# ============= ДАННЫЕ КВЕСТОВ =============

class QuestData:
    """Статические данные квестов (замена Act1.QUESTS)"""
    
    QUESTS = {
        "quest1": {
            "id": "quest1",
            "name": "Потерянный амулет",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Элли потеряла свой амулет где-то в Костях катакомб.",
            "objectives": [
                {"type": "find_item", "item": "amulet", "location": 3, "required": 1}
            ],
            "rewards": {"exp": 100, "gold": 50},
            "next_quest": "quest2",
            "min_level": 1
        },
        "quest2": {
            "id": "quest2",
            "name": "Проклятие надзирателя",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Надзиратель тюрьмы мучает души заключенных.",
            "objectives": [
                {"type": "kill_boss", "boss": "Смотритель темниц", "location": 6, "required": 1}
            ],
            "rewards": {"exp": 200, "gold": 150, "item": "unique_ring"},
            "next_quest": "quest3",
            "min_level": 3
        },
        "quest3": {
            "id": "quest3",
            "name": "Выход наружу",
            "giver": "Безумная Элли",
            "giver_id": "ellie",
            "description": "Убей древнего спрута и выйди на свободу.",
            "objectives": [
                {"type": "kill_boss", "boss": "Древний спрут", "location": 7, "required": 1}
            ],
            "rewards": {"exp": 500, "gold": 300, "item": "unique_weapon"},
            "is_final": True,
            "min_level": 5
        },
        "side_quest1": {
            "id": "side_quest1",
            "name": "Помоги выжившим",
            "giver": "Старик Морли",
            "giver_id": "morley",
            "description": "В тюрьме остались выжившие. Найди их и приведи в убежище.",
            "objectives": [
                {"type": "rescue", "target": "prisoners", "location": 6, "required": 3}
            ],
            "rewards": {"exp": 150, "gold": 100},
            "min_level": 2
        },
        "side_quest2": {
            "id": "side_quest2",
            "name": "Червивая проблема",
            "giver": "Торговец Грег",
            "giver_id": "greg",
            "description": "Убей 10 огромных червей в туннелях.",
            "objectives": [
                {"type": "kill_monsters", "monster": "Огромный червь", "location": 4, "required": 10}
            ],
            "rewards": {"exp": 120, "gold": 80},
            "min_level": 2
        }
    }
    
    @classmethod
    def get_quest(cls, quest_id):
        """Безопасно получает данные квеста"""
        return cls.QUESTS.get(quest_id)
    
    @classmethod
    def get_quests_by_giver(cls, giver_id):
        """Получает квесты от NPC"""
        return [q for q in cls.QUESTS.values() if q.get("giver_id") == giver_id]


# ============= МЕНЕДЖЕР КВЕСТОВ =============

class QuestManager:
    """Менеджер квестов для игрока"""
    
    def __init__(self, player):
        self.player = player
        self.quests = {}
        self.completed_quests = set()
        self._init_quests()
    
    def _init_quests(self):
        """Инициализирует квесты"""
        for quest_id, quest_data in QuestData.QUESTS.items():
            quest = Quest(quest_id, quest_data)
            self.quests[quest_id] = quest
            
            # Синхронизируем с player.quests
            if quest_id not in self.player.quests:
                self.player.quests[quest_id] = {
                    "status": "available",
                    "progress": {}
                }
    
    def get_available_quests(self):
        """Доступные квесты"""
        available = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.AVAILABLE:
                if quest.is_available(self.player.level, self.completed_quests):
                    available.append(quest)
        return available
    
    def get_active_quests(self):
        """Активные квесты"""
        return [q for q in self.quests.values() if q.status == QuestStatus.ACTIVE]
    
    def get_completed_quests(self):
        """Выполненные квесты"""
        return [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]
    
    def accept_quest(self, quest_id):
        """Принять квест"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        quest = self.quests[quest_id]
        
        if quest.status != QuestStatus.AVAILABLE:
            return False, "Квест недоступен"
        
        if not quest.is_available(self.player.level, self.completed_quests):
            return False, "Не выполнены условия"
        
        quest.start()
        
        # Обновляем статус в player.quests
        self.player.quests[quest_id]["status"] = "active"
        
        return True, f"Квест '{quest.name}' принят"
    
    def update_progress(self, objective_type, target, amount=1, location_id=None):
        """Обновляет прогресс всех активных квестов"""
        completed_quests = []
        
        for quest in self.get_active_quests():
            was_updated = quest.update_progress(objective_type, target, amount, location_id)
            
            if was_updated and quest.is_completed():
                completed_quests.append(quest)
        
        return completed_quests
    
    def complete_quest(self, quest_id):
        """Завершить квест"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        quest = self.quests[quest_id]
        
        if not quest.is_completed():
            return False, "Квест еще не выполнен"
        
        success, rewards = quest.complete()
        
        if success:
            self.completed_quests.add(quest_id)
            self.player.quests[quest_id]["status"] = "completed"
            
            # Начисляем награды
            if rewards.exp > 0:
                self.player.add_exp(rewards.exp)
            if rewards.gold > 0:
                self.player.add_gold(rewards.gold)
            
            # Разблокируем следующий квест
            if quest.next_quest and quest.next_quest in self.quests:
                next_quest = self.quests[quest.next_quest]
                if next_quest.status == QuestStatus.LOCKED:
                    next_quest.status = QuestStatus.AVAILABLE
                    self.player.quests[quest.next_quest]["status"] = "available"
            
            return True, quest, rewards
        
        return False, "Ошибка при завершении"
    
    def get_quest_by_id(self, quest_id):
        """Получает квест по ID"""
        return self.quests.get(quest_id)
    
    def get_quests_string(self):
        """Строка со всеми квестами"""
        lines = ["📋 **ЖУРНАЛ КВЕСТОВ**\n"]
        
        active = self.get_active_quests()
        if active:
            lines.append("**⚔️ АКТИВНЫЕ:**")
            for quest in active:
                lines.append(f"  {quest.get_progress_string()}")
            lines.append("")
        
        available = self.get_available_quests()
        if available:
            lines.append("**📜 ДОСТУПНЫЕ:**")
            for quest in available:
                lines.append(f"  {quest.get_progress_string()}")
        
        if not active and not available:
            lines.append("Нет активных квестов")
        
        return "\n".join(lines)
