from models.item import Item, ItemType, MeleeWeapon, Flask
from data.items import FLASKS
from data.act1 import Act1
import random

# ============= МОДЕЛЬ ИГРОКА =============

class Player:
    """Класс игрока"""
    
    def __init__(self, name="Игрок"):
        # Основная информация
        self.name = name
        self.act = 1
        self.current_location = 1  # Начинаем с локации 1 (Вход в бездну)
        self.position_in_location = 0  # Позиция внутри текущей локации
        self.visited_locations = {1}  # Посещенные локации
        
        # Базовые статы
        self.hp = 150
        self.max_hp = 150
        self.defense = 5
        self.base_damage = 15  # Базовый урон без оружия
        self.accuracy = 85
        self.crit_chance = 5
        self.crit_multiplier = 125
        self.attack_speed = 100
        self.life_on_hit = 0
        self.stun_multiplier = 1.0
        
        # Атрибуты (для требований к оружию)
        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        
        # Прогрессия
        self.exp = 0
        self.level = 1
        self.gold = 50  # Немного стартового золота
        
        # Инвентарь
        self.inventory = []  # Список предметов
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
        
        # Фласки
        self.flasks = []
        self.max_flasks = 3
        self.active_flask = 0
        
        # Даем стартовую фласку
        starter_flask = self._create_starter_flask()
        self.flasks.append(starter_flask)
        
        # Квесты
        self.quests = {}  # {quest_id: {"status": "active/ completed/ locked", "progress": {...}}}
        self._init_quests()
        
        # Статистика
        self.kill_stats = {}  # {monster_name: count}
        self.total_kills = 0
        self.deaths = 0
        self.steps_taken = 0
        self.chests_opened = 0
        self.traps_triggered = 0
        
        # Временные эффекты
        self.buffs = []  # [(name, duration, effect)]
        self.debuffs = []  # [(name, duration, effect)]
    
    def _create_starter_flask(self):
        """Создает стартовую фласку"""
        from models.item import Flask
        return Flask("small_life")
    
    def _init_quests(self):
        """Инициализирует квесты"""
        # Основные квесты
        self.quests["quest1"] = {
            "status": "active",  # active, completed, locked
            "progress": {
                "find_item_amulet": 0
            }
        }
        self.quests["quest2"] = {
            "status": "locked",
            "progress": {
                "kill_boss_Смотритель темниц": 0
            }
        }
        self.quests["quest3"] = {
            "status": "locked",
            "progress": {
                "kill_boss_Древний спрут": 0
            }
        }
        
        # Побочные квесты
        self.quests["side_quest1"] = {
            "status": "available",
            "progress": {
                "rescue_prisoners": 0
            }
        }
        self.quests["side_quest2"] = {
            "status": "available",
            "progress": {
                "kill_monsters_Огромный червь": 0
            }
        }
    
    # ============= БОЕВЫЕ МЕТОДЫ =============
    
    def get_total_damage(self):
        """Рассчитывает общий урон с учетом оружия и атрибутов"""
        if self.equipped[ItemType.WEAPON]:
            weapon = self.equipped[ItemType.WEAPON]
            min_dmg, max_dmg = weapon.get_damage_range()
            damage = random.randint(min_dmg, max_dmg)
            
            # Бонус от силы для тяжелого оружия
            if hasattr(weapon, 'weapon_type') and weapon.weapon_type in ["one_hand_mace", "two_hand_mace", "one_hand_axe", "two_hand_axe"]:
                damage = int(damage * (1 + self.strength / 200))
            
            # Бонус от ловкости для легкого оружия
            if hasattr(weapon, 'weapon_type') and weapon.weapon_type in ["dagger", "claw", "thrusting_sword"]:
                damage = int(damage * (1 + self.dexterity / 200))
                self.crit_chance += self.dexterity // 20
            
            return damage
        else:
            # Без оружия
            return random.randint(5, 10) + self.strength // 5
    
    def take_damage(self, damage):
        """Получение урона с учетом защиты"""
        reduced_damage = max(1, damage - self.defense // 2)
        self.hp -= reduced_damage
        if self.hp < 0:
            self.hp = 0
        return reduced_damage
    
    def heal(self, amount):
        """Лечение"""
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp
    
    def add_flask_charge(self):
        """Восстанавливает 1 заряд всем фласкам после убийства"""
        charges_added = 0
        for flask in self.flasks:
            if flask.current_uses < flask.flask_data["uses"]:
                flask.current_uses = min(flask.flask_data["uses"], flask.current_uses + 1)
                charges_added += 1
        return charges_added
    
    def use_flask(self):
        """Использовать активную фласку"""
        if not self.flasks or self.active_flask >= len(self.flasks):
            return 0, "Нет фласок"
        
        flask = self.flasks[self.active_flask]
        heal = flask.use()
        
        if heal > 0:
            self.heal(heal)
            
            # Если фласка опустела, переключаем на следующую с зарядами
            if flask.current_uses == 0:
                self._switch_to_next_flask()
            
            return heal, f"Использована {flask.name}"
        else:
            # Фласка пуста, пробуем переключиться
            if self._switch_to_next_flask():
                return 0, "Фласка пуста, переключено на другую"
            return 0, "Все фласки пусты"
    
    def _switch_to_next_flask(self):
        """Переключает на следующую фласку с зарядами"""
        if len(self.flasks) <= 1:
            return False
        
        start_index = self.active_flask
        for i in range(len(self.flasks)):
            next_index = (start_index + i + 1) % len(self.flasks)
            if self.flasks[next_index].current_uses > 0:
                self.active_flask = next_index
                return True
        
        return False
    
    def switch_flask(self):
        """Переключить активную фласку вручную"""
        if len(self.flasks) > 1:
            self.active_flask = (self.active_flask + 1) % len(self.flasks)
            return True, f"Активная фласка: {self.flasks[self.active_flask].name}"
        return False, "Только одна фласка"
    
    # ============= МЕТОДЫ ЭКИПИРОВКИ =============
    
    def apply_item_stats(self, item):
        """Применяет статы предмета к игроку"""
        for stat, value in item.stats.items():
            if hasattr(self, stat):
                current = getattr(self, stat)
                setattr(self, stat, current + value)
    
    def remove_item_stats(self, item):
        """Убирает статы предмета у игрока"""
        for stat, value in item.stats.items():
            if hasattr(self, stat):
                current = getattr(self, stat)
                setattr(self, stat, current - value)
    
    def can_equip(self, item):
        """Проверяет, может ли игрок экипировать предмет"""
        if isinstance(item, MeleeWeapon):
            req = item.requirements
            
            # Проверка требований по атрибутам
            if req.get("str", 0) > self.strength:
                return False, f"Требуется сила: {req['str']}"
            if req.get("dex", 0) > self.dexterity:
                return False, f"Требуется ловкость: {req['dex']}"
            if req.get("int", 0) > self.intelligence:
                return False, f"Требуется интеллект: {req['int']}"
        
        return True, ""
    
    def equip(self, item, slot):
        """Экипировать предмет"""
        # Проверяем возможность экипировки
        can_equip, reason = self.can_equip(item)
        if not can_equip:
            return False, reason
        
        # Если в слоте уже есть предмет, снимаем его
        if self.equipped[slot]:
            self.unequip(slot)
        
        # Экипируем новый предмет
        self.equipped[slot] = item
        self.apply_item_stats(item)
        
        # Убираем из инвентаря
        if item in self.inventory:
            self.inventory.remove(item)
        
        return True, f"Экипировано: {item.name}"
    
    def unequip(self, slot):
        """Снять предмет"""
        item = self.equipped[slot]
        if not item:
            return False, "Слот пуст"
        
        # Убираем статы
        self.remove_item_stats(item)
        
        # Добавляем в инвентарь
        self.inventory.append(item)
        
        # Очищаем слот
        self.equipped[slot] = None
        
        return True, f"Снято: {item.name}"
    
    # ============= МЕТОДЫ ИНВЕНТАРЯ =============
    
    def add_item(self, item):
        """Добавить предмет в инвентарь"""
        self.inventory.append(item)
        return True
    
    def remove_item(self, item_or_index):
        """Удалить предмет из инвентаря"""
        if isinstance(item_or_index, int):
            if 0 <= item_or_index < len(self.inventory):
                return self.inventory.pop(item_or_index)
        else:
            if item_or_index in self.inventory:
                self.inventory.remove(item_or_index)
                return item_or_index
        return None
    
    def get_inventory_item(self, index):
        """Получить предмет из инвентаря по индексу"""
        if 0 <= index < len(self.inventory):
            return self.inventory[index]
        return None
    
    def add_flask(self, flask):
        """Добавить фласку"""
        if len(self.flasks) < self.max_flasks:
            self.flasks.append(flask)
            return True, "Фласка добавлена"
        else:
            # Если уже максимум, кладем в инвентарь
            self.inventory.append(flask)
            return True, "Фласка добавлена в инвентарь (максимум фласок)"
    
    # ============= МЕТОДЫ ПРОГРЕССИИ =============
    
    def add_exp(self, amount):
        """Добавить опыт и проверить повышение уровня"""
        self.exp += amount
        
        # Проверка на повышение уровня
        levels_gained = 0
        while self.exp >= self.get_exp_for_next_level():
            self.level_up()
            levels_gained += 1
        
        return levels_gained
    
    def get_exp_for_next_level(self):
        """Получить опыт, необходимый для следующего уровня"""
        return self.level * 100
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        
        # Повышение атрибутов
        self.strength += 2
        self.dexterity += 2
        self.intelligence += 2
        
        # Небольшое повышение характеристик
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
        location = Act1.get_location_by_id(location_id)
        if not location:
            return False, "Локация не найдена"
        
        self.current_location = location_id
        self.position_in_location = 0
        self.visited_locations.add(location_id)
        self.steps_taken += 1
        
        return True, f"Вы вошли в {location['name']}"
    
    def move_forward(self):
        """Продвинуться вперед в текущей локации"""
        self.position_in_location += 1
        self.steps_taken += 1
        return self.position_in_location
    
    def can_proceed(self, total_events):
        """Может ли игрок идти дальше в текущей локации"""
        return self.position_in_location < total_events - 1
    
    def is_at_end_of_location(self, total_events):
        """Проверяет, дошел ли игрок до конца локации"""
        return self.position_in_location >= total_events - 1
    
    def get_location_progress(self, total_events):
        """Получить прогресс в текущей локации"""
        return f"{self.position_in_location + 1}/{total_events}"
    
    # ============= МЕТОДЫ КВЕСТОВ =============
    
    def get_active_quests(self):
        """Получить список активных квестов"""
        active = []
        for quest_id, quest_data in self.quests.items():
            if quest_data["status"] == "active":
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    active.append({
                        "id": quest_id,
                        "info": quest_info,
                        "progress": quest_data["progress"]
                    })
        return active
    
    def get_available_quests(self):
        """Получить список доступных квестов"""
        available = []
        for quest_id, quest_data in self.quests.items():
            if quest_data["status"] == "available":
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    available.append({
                        "id": quest_id,
                        "info": quest_info
                    })
        return available
    
    def get_completed_quests(self):
        """Получить список выполненных квестов"""
        completed = []
        for quest_id, quest_data in self.quests.items():
            if quest_data["status"] == "completed":
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    completed.append({
                        "id": quest_id,
                        "info": quest_info
                    })
        return completed
    
    def accept_quest(self, quest_id):
        """Принять квест"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        if self.quests[quest_id]["status"] != "available":
            return False, "Квест недоступен"
        
        self.quests[quest_id]["status"] = "active"
        return True, f"Квест '{Act1.get_quest_by_id(quest_id)['name']}' принят"
    
    def update_quest_progress(self, quest_id, objective_type, target, amount=1):
        """Обновить прогресс квеста"""
        if quest_id not in self.quests:
            return False
        
        quest_data = self.quests[quest_id]
        if quest_data["status"] != "active":
            return False
        
        quest_info = Act1.get_quest_by_id(quest_id)
        if not quest_info:
            return False
        
        # Обновляем прогресс
        updated = Act1.update_quest_progress(quest_info, objective_type, target, amount)
        
        # Синхронизируем с данными игрока - ИСПРАВЛЕННАЯ СТРОКА
        for obj in quest_info["objectives"]:
            key = f"{obj['type']}_{obj.get('item', obj.get('boss', obj.get('monster', obj.get('target', ''))))}"
            quest_data["progress"][key] = obj["progress"]
        
        # Проверяем выполнение квеста
        if Act1.is_quest_completed(quest_info):
            return self.complete_quest(quest_id)
        
        return True
    
    def complete_quest(self, quest_id):
        """Завершить квест и получить награды"""
        if quest_id not in self.quests:
            return False, "Квест не найден"
        
        if self.quests[quest_id]["status"] != "active":
            return False, "Квест не активен"
        
        quest_info = Act1.get_quest_by_id(quest_id)
        if not quest_info:
            return False, "Информация о квесте не найдена"
        
        # Проверяем выполнение
        if not Act1.is_quest_completed(quest_info):
            return False, "Квест еще не выполнен"
        
        # Получаем награды
        rewards = Act1.get_quest_rewards(quest_id)
        
        # Начисляем награды
        reward_text = []
        
        if "exp" in rewards:
            self.add_exp(rewards["exp"])
            reward_text.append(f"✨ {rewards['exp']} опыта")
        
        if "gold" in rewards:
            self.add_gold(rewards["gold"])
            reward_text.append(f"💰 {rewards['gold']} золота")
        
        if "item" in rewards:
            # Здесь будет создание предмета-награды
            reward_text.append(f"🎁 Особый предмет")
        
        # Обновляем статус квеста
        self.quests[quest_id]["status"] = "completed"
        
        # Разблокируем следующий квест, если есть
        next_quest = Act1.get_next_quest(quest_id)
        if next_quest and next_quest["id"] in self.quests:
            self.quests[next_quest["id"]]["status"] = "available"
        
        return True, f"Квест выполнен! Награды: {', '.join(reward_text)}"
    
    # ============= МЕТОДЫ СТАТИСТИКИ =============
    
    def add_kill(self, monster_name):
        """Добавить убийство монстра в статистику"""
        if monster_name in self.kill_stats:
            self.kill_stats[monster_name] += 1
        else:
            self.kill_stats[monster_name] = 1
        self.total_kills += 1
    
    def add_death(self):
        """Добавить смерть в статистику"""
        self.deaths += 1
    
    def add_chest_opened(self):
        """Добавить открытый сундук"""
        self.chests_opened += 1
    
    def add_trap_triggered(self):
        """Добавить сработавшую ловушку"""
        self.traps_triggered += 1
    
    # ============= МЕТОДЫ БАФФОВ/ДЕБАФФОВ =============
    
    def add_buff(self, name, duration, effect):
        """Добавить временный бафф"""
        self.buffs.append([name, duration, effect])
    
    def add_debuff(self, name, duration, effect):
        """Добавить временный дебафф"""
        self.debuffs.append([name, duration, effect])
    
    def update_buffs(self):
        """Обновить длительность баффов (вызывается каждый ход)"""
        # Обновляем баффы
        new_buffs = []
        for buff in self.buffs:
            buff[1] -= 1
            if buff[1] > 0:
                new_buffs.append(buff)
            else:
                # Убираем эффект баффа
                self._remove_buff_effect(buff[2])
        self.buffs = new_buffs
        
        # Обновляем дебаффы
        new_debuffs = []
        for debuff in self.debuffs:
            debuff[1] -= 1
            if debuff[1] > 0:
                new_debuffs.append(debuff)
            else:
                # Убираем эффект дебаффа
                self._remove_debuff_effect(debuff[2])
        self.debuffs = new_debuffs
    
    def _remove_buff_effect(self, effect):
        """Убрать эффект баффа"""
        # Здесь будет логика удаления эффектов
        pass
    
    def _remove_debuff_effect(self, effect):
        """Убрать эффект дебаффа"""
        # Здесь будет логика удаления эффектов
        pass
    
    # ============= МЕТОДЫ СОСТОЯНИЯ =============
    
    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.hp > 0
    
    def reset_for_new_act(self):
        """Сброс для нового акта"""
        self.act += 1
        self.current_location = Act1.get_first_location()["id"]
        self.position_in_location = 0
        
        # Восстанавливаем здоровье
        self.hp = self.max_hp
        
        # Восстанавливаем фласки
        for flask in self.flasks:
            flask.current_uses = flask.flask_data["uses"]
    
    def die(self):
        """Смерть игрока"""
        self.add_death()
        
        # Сброс позиции в убежище
        haven = Act1.get_haven_location()
        if haven:
            self.current_location = haven["id"]
            self.position_in_location = 0
        
        # Восстанавливаем здоровье наполовину
        self.hp = self.max_hp // 2
        
        # Частично восстанавливаем фласки
        for flask in self.flasks:
            flask.current_uses = max(1, flask.flask_data["uses"] // 2)
    
    # ============= МЕТОДЫ ОТОБРАЖЕНИЯ =============
    
    def get_stats_string(self):
        """Получить строку со статами игрока"""
        # Информация об оружии
        weapon_info = "Нет оружия"
        if self.equipped[ItemType.WEAPON]:
            weapon = self.equipped[ItemType.WEAPON]
            min_dmg, max_dmg = weapon.get_damage_range()
            weapon_info = f"{weapon.get_name_colored()} [{min_dmg}-{max_dmg}]"
        
        # Информация о фласках
        flask_info = []
        for i, flask in enumerate(self.flasks):
            marker = "👉" if i == self.active_flask else "  "
            flask_info.append(f"{marker} {flask.get_status()}")
        flask_text = "\n".join(flask_info) if flask_info else "Нет фласок"
        
        # Информация о квестах
        active_quests = self.get_active_quests()
        quest_text = f"Активных квестов: {len(active_quests)}" if active_quests else "Нет активных квестов"
        
        return (
            f"👤 **{self.name}** | Ур. {self.level}\n"
            f"❤️ {self.hp}/{self.max_hp} HP\n"
            f"⚔️ {weapon_info}\n"
            f"🛡️ Защита: {self.defense} | 🎯 Точность: {self.accuracy}%\n"
            f"🔥 Крит: {self.crit_chance}% x{self.crit_multiplier}%\n"
            f"💪 {self.strength} | 🏹 {self.dexterity} | 📚 {self.intelligence}\n"
            f"💰 {self.gold} золота | ✨ {self.exp}/{self.level * 100}\n\n"
            f"🧪 **Фласки:**\n{flask_text}\n\n"
            f"📋 {quest_text}"
        )
    
    def get_inventory_string(self):
        """Получить строку с инвентарем"""
        if not self.inventory and not self.flasks:
            return "🎒 **Инвентарь пуст**"
        
        text = "🎒 **ИНВЕНТАРЬ**\n\n"
        
        # Группируем предметы
        weapons = []
        other_items = []
        inv_flasks = []
        
        for item in self.inventory:
            if item.item_type == ItemType.FLASK:
                inv_flasks.append(item)
            elif item.item_type == ItemType.WEAPON:
                weapons.append(item)
            else:
                other_items.append(item)
        
        # Оружие
        if weapons:
            text += "**⚔️ Оружие:**\n"
            for i, item in enumerate(weapons):
                text += f"{i+1}. {item.get_name_colored()}\n"
            text += "\n"
        
        # Другая экипировка
        if other_items:
            text += "**🛡️ Экипировка:**\n"
            offset = len(weapons)
            for i, item in enumerate(other_items, start=offset):
                text += f"{i+1}. {item.get_name_colored()}\n"
            text += "\n"
        
        # Фласки в инвентаре
        if inv_flasks:
            text += "**🧪 Фласки (в инвентаре):**\n"
            offset = len(weapons) + len(other_items)
            for i, item in enumerate(inv_flasks, start=offset):
                text += f"{i+1}. {item.get_name_colored()} [{item.current_uses}/{item.flask_data['uses']}]\n"
        
        # Фласки экипированные
        if self.flasks:
            text += "\n**🧪 Фласки (экипированные):**\n"
            for i, flask in enumerate(self.flasks):
                marker = "👉" if i == self.active_flask else "  "
                text += f"{marker} {flask.get_name_colored()} [{flask.current_uses}/{flask.flask_data['uses']}]\n"
        
        text += f"\n💰 Золото: {self.gold}"
        
        return text
    
    def get_equipment_string(self):
        """Получить строку с экипировкой"""
        text = "📊 **ЭКИПИРОВКА**\n\n"
        
        # Оружие
        if self.equipped[ItemType.WEAPON]:
            weapon = self.equipped[ItemType.WEAPON]
            text += f"**⚔️ Оружие:**\n"
            text += f"└ {weapon.get_name_colored()}\n"
            
            min_dmg, max_dmg = weapon.get_damage_range()
            text += f"   Урон: {min_dmg}-{max_dmg}\n"
            text += f"   Скорость: {weapon.attack_speed:.2f}\n"
            text += f"   Крит: {weapon.crit_chance + weapon.stats.get('crit_chance', 0)}%\n"
            
            if weapon.affixes:
                text += f"\n   **Модификаторы:**\n"
                for affix_type, affix_data in weapon.affixes:
                    value = weapon.stats.get(affix_data["stat"], 0)
                    stat_names = {
                        "damage": "⚔️ Урон",
                        "max_hp": "❤️ Здоровье",
                        "defense": "🛡️ Защита",
                        "attack_speed": "⚡ Скорость",
                        "accuracy": "🎯 Точность",
                        "crit_chance": "🔥 Шанс крита",
                        "crit_multiplier": "💥 Множитель",
                        "life_on_hit": "🩸 Вампиризм",
                        "stun_multiplier": "😵 Оглушение"
                    }
                    stat_name = stat_names.get(affix_data["stat"], affix_data["stat"])
                    text += f"   • {affix_data['name']}: {stat_name} +{value}\n"
        else:
            text += f"**⚔️ Оружие:** Пусто\n"
        
        text += f"\n📊 **ИТОГОВЫЕ СТАТЫ:**\n"
        text += f"❤️ HP: {self.hp}/{self.max_hp}\n"
        text += f"⚔️ Урон: {self.get_total_damage()}\n"
        text += f"🛡️ Защита: {self.defense}\n"
        text += f"🎯 Точность: {self.accuracy}%\n"
        text += f"🔥 Крит: {self.crit_chance}% x{self.crit_multiplier}%\n"
        text += f"💪 Сила: {self.strength}\n"
        text += f"🏹 Ловкость: {self.dexterity}\n"
        text += f"📚 Интеллект: {self.intelligence}"
        
        return text
    
    def get_quests_string(self):
        """Получить строку с квестами"""
        text = "📋 **КВЕСТЫ**\n\n"
        
        # Основные квесты
        text += "**⚔️ Основные:**\n"
        main_quests = ["quest1", "quest2", "quest3"]
        for quest_id in main_quests:
            if quest_id in self.quests:
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    status = self.quests[quest_id]["status"]
                    status_emoji = {
                        "active": "⚔️",
                        "completed": "✅",
                        "locked": "🔒",
                        "available": "📜"
                    }.get(status, "❓")
                    
                    text += f"{status_emoji} **{quest_info['name']}**"
                    if status == "active":
                        # Показываем прогресс
                        progress = self.quests[quest_id]["progress"]
                        progress_text = []
                        for key, value in progress.items():
                            obj = quest_info["objectives"][0]  # Упрощенно
                            progress_text.append(f"{value}/{obj['required']}")
                        text += f" ({', '.join(progress_text)})"
                    text += "\n"
        
        # Побочные квесты
        text += "\n**📜 Побочные:**\n"
        side_quests = ["side_quest1", "side_quest2"]
        for quest_id in side_quests:
            if quest_id in self.quests:
                quest_info = Act1.get_quest_by_id(quest_id)
                if quest_info:
                    status = self.quests[quest_id]["status"]
                    status_emoji = {
                        "active": "⚔️",
                        "completed": "✅",
                        "locked": "🔒",
                        "available": "📜"
                    }.get(status, "❓")
                    
                    text += f"{status_emoji} **{quest_info['name']}**"
                    if status == "active":
                        progress = self.quests[quest_id]["progress"]
                        progress_text = []
                        for key, value in progress.items():
                            obj = quest_info["objectives"][0]
                            progress_text.append(f"{value}/{obj['required']}")
                        text += f" ({', '.join(progress_text)})"
                    text += "\n"
        
        if not any(self.quests[q]["status"] in ["active", "available"] for q in main_quests + side_quests):
            text += "Нет доступных квестов\n"
        
        return text
