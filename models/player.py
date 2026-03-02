import random
from models.item import Item, ItemType, MeleeWeapon, Flask
from data.items import FLASKS
from systems.area_level import AreaRegistry

# ============= МОДЕЛЬ ИГРОКА =============

class Player:
    """Класс игрока"""
    
    def __init__(self, name="Игрок"):
        # Основная информация
        self.name = name
        self.act = 1
        self.current_location = 1
        self.position_in_location = 0
        self.visited_locations = {1}
        self.talked_to_npcs = set()
        
        # Флаги получения базовых предметов
        self.has_portal = False  # Свиток портала (получаем в убежище)
        
        # Базовые статы
        self.hp = 150
        self.max_hp = 150
        self.mana = 100
        self.max_mana = 100
        self.defense = 5
        self.base_damage = 15
        self.accuracy = 85
        self.crit_chance = 5
        self.crit_multiplier = 125
        self.attack_speed = 100
        self.life_on_hit = 0
        self.stun_multiplier = 1.0
        
        # Атрибуты
        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        
        # Прогрессия
        self.exp = 0
        self.level = 1
        self.gold = 50
        
        # Инвентарь
        self.inventory = []
        self.equipped = {
            ItemType.WEAPON: None,
            ItemType.HELMET: None,
            ItemType.ARMOR: None,
            ItemType.GLOVES: None,
            ItemType.BOOTS: None,
            ItemType.BELT: None,
            ItemType.RING: None,
            ItemType.AMULET: None
        }
        
        # Фласки - в начале игры пусто
        self.flasks = []
        self.max_flasks = 3
        self.active_flask = 0
        
        # Квесты
        self.quests = {}
        
        # Статистика
        self.kill_stats = {}
        self.total_kills = 0
        self.deaths = 0
        self.steps_taken = 0
        self.chests_opened = 0
        self.traps_triggered = 0
        
        # Временные эффекты
        self.buffs = []
        self.debuffs = []
    
    # ============= МЕТОДЫ ДЛЯ НАЧАЛЬНЫХ ПРЕДМЕТОВ =============
    
    def give_starter_items(self):
        """Выдает стартовые предметы после первого посещения убежища"""
        from models.item import Flask
        
        items_given = []
        
        # Даем фласку здоровья, если еще нет
        if len([f for f in self.flasks if "💊" in f.emoji]) == 0:
            health_flask = Flask("small_life")
            health_flask.emoji = "🟢💊🧪"
            self.flasks.append(health_flask)
            items_given.append("🟢💊🧪 Фласка здоровья")
        
        # Даем фласку маны, если еще нет
        if len([f for f in self.flasks if "Ⓜ️" in f.emoji]) == 0:
            mana_flask = Flask("small_mana")
            mana_flask.emoji = "🟢Ⓜ️🧪"
            self.flasks.append(mana_flask)
            items_given.append("🟢Ⓜ️🧪 Фласка маны")
        
        # Даем свиток портала
        if not self.has_portal:
            self.has_portal = True
            items_given.append("🌀 Свиток портала")
        
        return items_given
    
    # ============= МЕТОДЫ ИНВЕНТАРЯ =============
    
    def add_item(self, item):
        """Добавляет предмет в инвентарь"""
        if item:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item_or_index):
        """Удаляет предмет из инвентаря"""
        if isinstance(item_or_index, int):
            if 0 <= item_or_index < len(self.inventory):
                return self.inventory.pop(item_or_index)
        else:
            if item_or_index in self.inventory:
                self.inventory.remove(item_or_index)
                return item_or_index
        return None
    
    def get_inventory_item(self, index):
        """Получает предмет по индексу"""
        if 0 <= index < len(self.inventory):
            return self.inventory[index]
        return None
    
    # ============= БОЕВЫЕ МЕТОДЫ =============
    
    def get_total_damage(self):
        """Рассчитывает общий урон с учетом оружия"""
        if self.equipped[ItemType.WEAPON]:
            weapon = self.equipped[ItemType.WEAPON]
            min_dmg, max_dmg = weapon.get_damage_range()
            damage = random.randint(min_dmg, max_dmg)
            
            # Бонус от атрибутов
            if hasattr(weapon, 'weapon_type'):
                if weapon.weapon_type in ["one_hand_mace", "two_hand_mace", "one_hand_axe", "two_hand_axe"]:
                    damage = int(damage * (1 + self.strength / 200))
                elif weapon.weapon_type in ["dagger", "claw", "thrusting_sword"]:
                    damage = int(damage * (1 + self.dexterity / 200))
                    self.crit_chance += self.dexterity // 20
            
            return damage
        else:
            return random.randint(5, 10) + self.strength // 5
    
    def take_damage(self, damage):
        """Получение урона с учетом защиты"""
        reduced_damage = max(1, damage - self.defense // 2)
        self.hp = max(0, self.hp - reduced_damage)
        return reduced_damage
    
    def heal(self, amount):
        """Лечение"""
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp
    
    def use_mana(self, amount):
        """Использовать ману"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def restore_mana(self, amount):
        """Восстановить ману"""
        self.mana = min(self.max_mana, self.mana + amount)
        return self.mana
    
    def add_flask_charge(self):
        """Восстанавливает заряды фласок"""
        charges_added = 0
        for flask in self.flasks:
            if flask.current_uses < flask.flask_data["uses"]:
                flask.current_uses += 1
                charges_added += 1
        return charges_added
    
    def use_flask(self, flask_index=None):
        """Использовать фласку"""
        if flask_index is None:
            flask_index = self.active_flask
            
        if not self.flasks or flask_index >= len(self.flasks):
            return 0, "Нет фласок"
        
        flask = self.flasks[flask_index]
        value = flask.use()
        
        if value > 0:
            if "💊" in flask.emoji:  # Фласка здоровья
                self.heal(value)
                return value, f"🧪 Использована фласка здоровья: +{value} HP"
            elif "Ⓜ️" in flask.emoji:  # Фласка маны
                self.restore_mana(value)
                return value, f"💙 Использована фласка маны: +{value} MP"
            else:
                return value, f"✨ Использована {flask.name}"
        else:
            if self._switch_to_next_flask():
                return 0, "Фласка пуста, переключено на другую"
            return 0, "Все фласки пусты"
    
    def _switch_to_next_flask(self):
        """Переключает на следующую фласку с зарядами"""
        if len(self.flasks) <= 1:
            return False
        
        for i in range(1, len(self.flasks) + 1):
            next_index = (self.active_flask + i) % len(self.flasks)
            if self.flasks[next_index].current_uses > 0:
                self.active_flask = next_index
                return True
        return False
    
    def switch_flask(self):
        """Переключить активную фласку вручную"""
        if len(self.flasks) > 1:
            self.active_flask = (self.active_flask + 1) % len(self.flasks)
            flask_type = "🟢💊" if "💊" in self.flasks[self.active_flask].emoji else "🟢Ⓜ️" if "Ⓜ️" in self.flasks[self.active_flask].emoji else "⚪️✨"
            return True, f"Активная фласка: {flask_type}"
        return False, "Только одна фласка"
    
    # ============= МЕТОДЫ ЭКИПИРОВКИ =============
    
    def apply_item_stats(self, item):
        """Применяет статы предмета"""
        for stat, value in item.stats.items():
            if hasattr(self, stat):
                current = getattr(self, stat)
                setattr(self, stat, current + value)
    
    def remove_item_stats(self, item):
        """Убирает статы предмета"""
        for stat, value in item.stats.items():
            if hasattr(self, stat):
                current = getattr(self, stat)
                setattr(self, stat, current - value)
    
    def can_equip(self, item):
        """Проверяет возможность экипировки"""
        if isinstance(item, MeleeWeapon) and hasattr(item, 'requirements') and item.requirements:
            req = item.requirements
            if req.get("str", 0) > self.strength:
                return False, f"Требуется сила: {req['str']}"
            if req.get("dex", 0) > self.dexterity:
                return False, f"Требуется ловкость: {req['dex']}"
            if req.get("int", 0) > self.intelligence:
                return False, f"Требуется интеллект: {req['int']}"
        return True, ""
    
    def equip(self, item, slot):
        """Экипировать предмет"""
        can_equip, reason = self.can_equip(item)
        if not can_equip:
            return False, reason
        
        if self.equipped[slot]:
            self.unequip(slot)
        
        self.equipped[slot] = item
        self.apply_item_stats(item)
        
        if item in self.inventory:
            self.inventory.remove(item)
        
        return True, f"Экипировано: {item.name}"
    
    def unequip(self, slot):
        """Снять предмет"""
        item = self.equipped[slot]
        if not item:
            return False, "Слот пуст"
        
        self.remove_item_stats(item)
        self.inventory.append(item)
        self.equipped[slot] = None
        
        return True, f"Снято: {item.name}"
    
    # ============= МЕТОДЫ ПРОГРЕССИИ =============
    
    def add_exp(self, amount):
        """Добавить опыт"""
        self.exp += amount
        levels_gained = 0
        
        while self.exp >= self.get_exp_for_next_level():
            self.level_up()
            levels_gained += 1
        
        return levels_gained
    
    def get_exp_for_next_level(self):
        """Опыт для следующего уровня"""
        return self.level * 100
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.max_mana += 10
        self.mana = self.max_mana
        self.strength += 2
        self.dexterity += 2
        self.intelligence += 2
        self.accuracy += 1
        self.crit_chance += 0.5
    
    def add_gold(self, amount):
        """Добавить золото"""
        self.gold += amount
        return self.gold
    
    def spend_gold(self, amount):
        """Потратить золото"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    # ============= МЕТОДЫ ПЕРЕМЕЩЕНИЯ =============
    
    def move_to_location(self, location_id):
        """Переместиться в новую локацию"""
        location = AreaRegistry.get_location(location_id)
        if not location:
            return False, "Локация не найдена"
        
        self.current_location = location_id
        self.position_in_location = 0
        self.visited_locations.add(location_id)
        self.steps_taken += 1
        
        return True, f"Вы вошли в {location['name']}"
    
    def get_location_progress(self, total_events):
        """Прогресс в текущей локации"""
        return f"{self.position_in_location + 1}/{total_events}"
    
    # ============= МЕТОДЫ КВЕСТОВ =============
    
    def get_active_quests(self):
        """Получить активные квесты"""
        active = []
        for quest_id, quest_data in self.quests.items():
            if quest_data.get("status") == "active":
                active.append(quest_id)
        return active
    
    def update_quest_progress(self, quest_id, objective_key, amount=1):
        """Обновить прогресс конкретного квеста"""
        if quest_id not in self.quests:
            return False
        
        quest_data = self.quests[quest_id]
        if quest_data.get("status") != "active":
            return False
        
        if objective_key in quest_data.get("progress", {}):
            quest_data["progress"][objective_key] += amount
            return True
        return False
    
    # ============= МЕТОДЫ СТАТИСТИКИ =============
    
    def add_kill(self, monster_name):
        """Добавить убийство"""
        self.kill_stats[monster_name] = self.kill_stats.get(monster_name, 0) + 1
        self.total_kills += 1
    
    def add_death(self):
        """Добавить смерть"""
        self.deaths += 1
    
    def add_chest_opened(self):
        """Добавить открытый сундук"""
        self.chests_opened += 1
    
    def add_trap_triggered(self):
        """Добавить сработавшую ловушку"""
        self.traps_triggered += 1
    
    # ============= МЕТОДЫ СОСТОЯНИЯ =============
    
    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.hp > 0
    
    def die(self):
        """Смерть игрока"""
        self.add_death()
        
        haven_id = 2
        self.current_location = haven_id
        self.position_in_location = 0
        self.hp = self.max_hp // 2
        self.mana = self.max_mana // 2
        
        for flask in self.flasks:
            flask.current_uses = max(1, flask.flask_data["uses"] // 2)
    
    # ============= МЕТОДЫ ОТОБРАЖЕНИЯ =============
    
    def get_stats_string(self):
        """Получить строку со статами"""
        weapon_info = "Нет оружия"
        if self.equipped[ItemType.WEAPON]:
            weapon = self.equipped[ItemType.WEAPON]
            min_dmg, max_dmg = weapon.get_damage_range()
            weapon_info = f"{weapon.get_name_colored()} [{min_dmg}-{max_dmg}]"
        
        flask_info = []
        for i, flask in enumerate(self.flasks):
            marker = "👉" if i == self.active_flask else "  "
            flask_type = "🟢💊" if "💊" in flask.emoji else "🟢Ⓜ️" if "Ⓜ️" in flask.emoji else "⚪️✨" if "✨" in flask.emoji else "🔵🛡️"
            flask_info.append(f"{marker} {flask_type} [{flask.current_uses}/{flask.flask_data['uses']}]")
        flask_text = "\n".join(flask_info) if flask_info else "Нет фласок"
        
        current_location = AreaRegistry.get_location_name(self.current_location)
        
        portal_status = "Есть" if self.has_portal else "Нет"
        
        return (
            f"👤 **{self.name}** | Ур. {self.level}\n"
            f"📍 {current_location}\n"
            f"❤️ {self.hp}/{self.max_hp} HP\n"
            f"💙 {self.mana}/{self.max_mana} MP\n"
            f"⚔️ {weapon_info}\n"
            f"🛡️ Защита: {self.defense} | 🎯 Точность: {self.accuracy}%\n"
            f"🔥 Крит: {self.crit_chance}% x{self.crit_multiplier}%\n"
            f"💪 {self.strength} | 🏹 {self.dexterity} | 📚 {self.intelligence}\n"
            f"💰 {self.gold} золота | ✨ {self.exp}/{self.level * 100}\n"
            f"🌀 Порталы: {portal_status}\n\n"
            f"🧪 **Фласки:**\n{flask_text}"
        )
