import random
import asyncio
from enum import Enum
from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask

# ============= ТИПЫ ДЕЙСТВИЙ В БОЮ =============

class CombatAction(Enum):
    ATTACK = "attack"       # Атака
    HEAVY_ATTACK = "heavy"  # Тяжелая атака
    FAST_ATTACK = "fast"    # Быстрая атака
    DEFEND = "defend"       # Защита
    DODGE = "dodge"         # Уклонение
    USE_FLASK = "flask"     # Использовать фласку
    USE_SKILL = "skill"     # Использовать навык
    RUN = "run"             # Попытка сбежать


# ============= РЕЗУЛЬТАТ ДЕЙСТВИЯ =============

class ActionResult:
    """Результат действия в бою"""
    
    def __init__(self):
        self.player_damage = 0
        self.enemy_damage = 0
        self.player_heal = 0
        self.enemy_heal = 0
        self.player_buffs = []
        self.enemy_buffs = []
        self.player_debuffs = []
        self.enemy_debuffs = []
        self.messages = []
        self.crit = False
        self.dodged = False
        self.blocked = False
        self.fled = False
        self.turn_ended = False
    
    def add_message(self, message):
        """Добавляет сообщение"""
        self.messages.append(message)
    
    def get_text(self):
        """Возвращает текст результата"""
        return "\n".join(self.messages)


# ============= КОМБО-СИСТЕМА =============

class ComboSystem:
    """Система комбо-ударов"""
    
    def __init__(self):
        self.combo_counter = 0
        self.combo_timer = 0
        self.max_combo = 5
        self.combo_multiplier = 1.0
    
    def add_hit(self):
        """Добавляет удар в комбо"""
        self.combo_counter = min(self.combo_counter + 1, self.max_combo)
        self.combo_timer = 3
        self._update_multiplier()
        return self.combo_counter
    
    def reset_combo(self):
        """Сбрасывает комбо"""
        self.combo_counter = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
    
    def update_timer(self):
        """Обновляет таймер комбо"""
        if self.combo_counter > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.reset_combo()
    
    def _update_multiplier(self):
        """Обновляет множитель комбо"""
        self.combo_multiplier = 1.0 + (self.combo_counter * 0.1)
    
    def get_combo_bonus(self):
        """Возвращает бонус от комбо"""
        if self.combo_counter >= 3:
            return {
                "damage": self.combo_multiplier,
                "crit": self.combo_counter * 2,
                "text": f"🔥 Комбо x{self.combo_counter}!"
            }
        return None


# ============= ОСНОВНАЯ СИСТЕМА БОЯ =============

class CombatSystem:
    """Основная система боя"""
    
    # Стоимость действий в мане
    MANA_COSTS = {
        CombatAction.ATTACK: 5,
        CombatAction.HEAVY_ATTACK: 15,
        CombatAction.FAST_ATTACK: 8,
        CombatAction.DEFEND: 10,
        CombatAction.DODGE: 12,
        CombatAction.USE_FLASK: 0,
        CombatAction.RUN: 20
    }
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.combo = ComboSystem()
        
        # Система фаз для боссов
        self.phases = []
        if enemy.rarity == "boss" and hasattr(enemy, 'phases'):
            for phase_data in enemy.phases:
                self.phases.append(BossPhase(
                    phase_data["name"],
                    phase_data["hp_percent"],
                    phase_data.get("damage_mult", 1.0),
                    phase_data.get("speed_mult", 1.0),
                    phase_data.get("adds", [])
                ))
        
        # Статистика боя
        self.turn_count = 0
        self.player_total_damage = 0
        self.enemy_total_damage = 0
        self.battle_log = []
    
    def process_turn(self, player_action, target_enemy=None):
        """Обрабатывает ход игрока"""
        result = ActionResult()
        self.turn_count += 1
        
        # Проверяем ману
        mana_cost = self.MANA_COSTS.get(player_action, 0)
        if mana_cost > 0 and not self.player.use_mana(mana_cost):
            result.add_message(f"💙 Недостаточно маны! Нужно {mana_cost}")
            # Если нет маны, просто защищаемся
            player_action = CombatAction.DEFEND
        
        # Враг выбирает действие
        enemy_action = self._choose_enemy_action()
        
        # Обработка действий
        if player_action == CombatAction.ATTACK:
            self._process_attack(result, enemy_action)
        elif player_action == CombatAction.HEAVY_ATTACK:
            self._process_heavy_attack(result, enemy_action)
        elif player_action == CombatAction.FAST_ATTACK:
            self._process_fast_attack(result, enemy_action)
        elif player_action == CombatAction.DEFEND:
            self._process_defend(result, enemy_action)
        elif player_action == CombatAction.DODGE:
            self._process_dodge(result, enemy_action)
        elif player_action == CombatAction.USE_FLASK:
            self._process_flask(result, enemy_action)
        elif player_action == CombatAction.USE_SKILL:
            self._process_skill(result, enemy_action)
        elif player_action == CombatAction.RUN:
            self._process_run(result, enemy_action)
        
        # Проверка фаз босса
        if self.phases:
            for phase in self.phases:
                if phase.check_activation(self.enemy.hp, self.enemy.max_hp):
                    phase_messages = phase.activate(self.enemy)
                    for msg in phase_messages:
                        result.add_message(msg)
        
        # Обновление комбо
        self.combo.update_timer()
        
        # Восстанавливаем ману (немного каждый ход)
        if hasattr(self.player, 'restore_mana'):
            self.player.restore_mana(3)
        
        # Добавляем в лог
        self._add_to_log(result)
        
        return result
    
    def _choose_enemy_action(self):
        """ИИ врага выбирает действие"""
        hp_percent = self.enemy.get_hp_percent()
        
        if hp_percent < 30 and random.random() < 0.4:
            return CombatAction.DEFEND
        elif random.random() < 0.3:
            return CombatAction.HEAVY_ATTACK
        else:
            return CombatAction.ATTACK
    
    def _process_attack(self, result, enemy_action):
        """Обрабатывает обычную атаку"""
        # Атака игрока
        hit_chance = self.player.accuracy
        
        if random.randint(1, 100) <= hit_chance:
            damage = self.player.get_total_damage()
            
            # Проверка на крит
            if random.randint(1, 100) <= self.player.crit_chance:
                damage = int(damage * (self.player.crit_multiplier / 100))
                result.crit = True
                result.add_message(f"🔥 КРИТ! {damage} урона")
            else:
                result.add_message(f"⚔️ Атака: {damage} урона")
            
            # Применяем урон
            actual_damage = self.enemy.take_damage(damage)
            result.player_damage = actual_damage
            self.player_total_damage += actual_damage
            
            # Вампиризм
            if self.player.life_on_hit > 0:
                heal = min(self.player.max_hp - self.player.hp, self.player.life_on_hit)
                if heal > 0:
                    self.player.heal(heal)
                    result.add_message(f"🩸 Вампиризм: +{heal} HP")
            
            # Комбо
            if actual_damage > 0:
                combo = self.combo.add_hit()
                if combo >= 3:
                    result.add_message(f"🔥 Комбо x{combo}!")
        else:
            result.add_message("😫 Промах!")
            self.combo.reset_combo()
        
        # Ответная атака врага (если жив)
        if self.enemy.is_alive():
            self._process_enemy_attack(result, enemy_action)
    
    def _process_heavy_attack(self, result, enemy_action):
        """Обрабатывает тяжелую атаку"""
        hit_chance = self.player.accuracy - 10  # Тяжелая атака менее точная
        
        if random.randint(1, 100) <= hit_chance:
            damage = int(self.player.get_total_damage() * 1.5)
            
            if random.randint(1, 100) <= self.player.crit_chance:
                damage = int(damage * (self.player.crit_multiplier / 100))
                result.crit = True
                result.add_message(f"🔥 КРИТИЧЕСКАЯ ТЯЖЕЛАЯ АТАКА! {damage} урона")
            else:
                result.add_message(f"💪 Тяжелая атака: {damage} урона")
            
            actual_damage = self.enemy.take_damage(damage)
            result.player_damage = actual_damage
            self.player_total_damage += actual_damage
            
            # Дополнительный эффект - оглушение
            stun_chance = 20 + self.player.stun_multiplier * 10
            if random.randint(1, 100) <= stun_chance:
                result.add_message("😵 Враг оглушен и пропустит ход!")
                result.turn_ended = True
            
            # Комбо
            combo = self.combo.add_hit()
            if combo >= 3:
                result.add_message(f"🔥 Комбо x{combo}!")
        else:
            result.add_message("😫 Тяжелая атака промахнулась!")
            self.combo.reset_combo()
        
        # Ответная атака врага, если не оглушен
        if self.enemy.is_alive() and not result.turn_ended:
            self._process_enemy_attack(result, enemy_action)
    
    def _process_fast_attack(self, result, enemy_action):
        """Обрабатывает быструю атаку"""
        hit_chance = self.player.accuracy + 15  # Быстрая атака точнее
        
        if random.randint(1, 100) <= hit_chance:
            damage = int(self.player.get_total_damage() * 0.7)
            
            # Повышенный шанс крита
            crit_chance = self.player.crit_chance + 10
            if random.randint(1, 100) <= crit_chance:
                damage = int(damage * (self.player.crit_multiplier / 100))
                result.crit = True
                result.add_message(f"🔥 КРИТИЧЕСКАЯ БЫСТРАЯ АТАКА! {damage} урона")
            else:
                result.add_message(f"⚡ Быстрая атака: {damage} урона")
            
            actual_damage = self.enemy.take_damage(damage)
            result.player_damage = actual_damage
            self.player_total_damage += actual_damage
            
            # Комбо
            combo = self.combo.add_hit()
            if combo >= 3:
                result.add_message(f"🔥 Комбо x{combo}!")
        else:
            result.add_message("😫 Промах!")
            self.combo.reset_combo()
        
        # Ответная атака врага
        if self.enemy.is_alive():
            self._process_enemy_attack(result, enemy_action)
    
    def _process_defend(self, result, enemy_action):
        """Обрабатывает защиту"""
        result.add_message("🛡️ Ты встаешь в защитную стойку!")
        
        # Бонус к защите на этот ход
        defense_bonus = self.player.defense * 2
        
        # Ответная атака врага с учетом защиты
        if self.enemy.is_alive():
            if enemy_action == CombatAction.ATTACK:
                enemy_damage = self.enemy.attack()
                reduced_damage = max(1, enemy_damage - defense_bonus // 2)
                self.player.take_damage(reduced_damage)
                result.enemy_damage = reduced_damage
                result.add_message(f"🛡️ Заблокировано! Получено {reduced_damage} урона")
            elif enemy_action == CombatAction.HEAVY_ATTACK:
                enemy_damage = int(self.enemy.attack() * 1.5)
                reduced_damage = max(1, enemy_damage - defense_bonus // 2)
                self.player.take_damage(reduced_damage)
                result.enemy_damage = reduced_damage
                result.add_message(f"🛡️ Тяжелый удар заблокирован! Получено {reduced_damage} урона")
            else:
                result.add_message("🤔 Враг не атакует")
        
        # Сброс комбо при защите
        self.combo.reset_combo()
    
    def _process_dodge(self, result, enemy_action):
        """Обрабатывает уклонение"""
        result.add_message("💨 Ты готовишься уклониться!")
        
        # Шанс уклонения
        dodge_chance = 50 + self.player.dexterity // 5
        
        if self.enemy.is_alive():
            if enemy_action in [CombatAction.ATTACK, CombatAction.HEAVY_ATTACK]:
                if random.randint(1, 100) <= dodge_chance:
                    result.add_message("💨 Ты грациозно уклоняешься от атаки!")
                    result.dodged = True
                else:
                    enemy_damage = self.enemy.attack()
                    if enemy_action == CombatAction.HEAVY_ATTACK:
                        enemy_damage = int(enemy_damage * 1.5)
                    self.player.take_damage(enemy_damage)
                    result.enemy_damage = enemy_damage
                    result.add_message(f"💥 Неудачный уклон! Получено {enemy_damage} урона")
            else:
                result.add_message("🤔 Враг не атакует")
        
        # Сброс комбо при уклонении
        self.combo.reset_combo()
    
    def _process_flask(self, result, enemy_action):
        """Обрабатывает использование фласки"""
        if not self.player.flasks:
            result.add_message("❌ Нет фласок!")
            return
        
        flask = self.player.flasks[self.player.active_flask]
        heal = flask.use()
        
        if heal > 0:
            self.player.heal(heal)
            result.player_heal = heal
            result.add_message(f"🧪 Использована {flask.name}: +{heal} HP")
            
            # Если фласка опустела, переключаемся
            if flask.current_uses == 0:
                for i, f in enumerate(self.player.flasks):
                    if f.current_uses > 0:
                        self.player.active_flask = i
                        result.add_message(f"🔄 Переключено на {f.name}")
                        break
        else:
            result.add_message("❌ Фласка пуста!")
            if hasattr(self.player, '_switch_to_next_flask') and self.player._switch_to_next_flask():
                result.add_message(f"🔄 Переключено на {self.player.flasks[self.player.active_flask].name}")
        
        # Враг может атаковать во время использования фласки
        if self.enemy.is_alive() and random.random() < 0.7:
            enemy_damage = self.enemy.attack()
            self.player.take_damage(enemy_damage)
            result.enemy_damage = enemy_damage
            result.add_message(f"💥 {self.enemy.name} атакует во время лечения: {enemy_damage} урона")
    
    def _process_skill(self, result, enemy_action):
        """Обрабатывает использование навыка (заглушка)"""
        result.add_message("✨ Навык не реализован")
        self._process_attack(result, enemy_action)
    
    def _process_run(self, result, enemy_action):
        """Обрабатывает попытку сбежать"""
        if random.random() < 0.5:
            result.fled = True
            result.add_message("🏃 Ты сбежал!")
        else:
            result.add_message("❌ Не удалось сбежать!")
            
            # Враг атакует
            enemy_damage = self.enemy.attack()
            self.player.take_damage(enemy_damage)
            result.enemy_damage = enemy_damage
            result.add_message(f"💥 {self.enemy.name} атакует: {enemy_damage} урона")
    
    def _process_enemy_attack(self, result, enemy_action):
        """Обрабатывает атаку врага"""
        if enemy_action == CombatAction.ATTACK:
            if random.randint(1, 100) <= self.enemy.accuracy:
                damage = self.enemy.attack()
                actual_damage = self.player.take_damage(damage)
                result.enemy_damage = actual_damage
                self.enemy_total_damage += actual_damage
                result.add_message(f"💥 {self.enemy.name} атакует: {actual_damage} урона")
            else:
                result.add_message(f"🙏 {self.enemy.name} промахнулся")
        
        elif enemy_action == CombatAction.HEAVY_ATTACK:
            if random.randint(1, 100) <= self.enemy.accuracy - 10:
                damage = int(self.enemy.attack() * 1.5)
                actual_damage = self.player.take_damage(damage)
                result.enemy_damage = actual_damage
                self.enemy_total_damage += actual_damage
                result.add_message(f"💥 {self.enemy.name} использует тяжелую атаку: {actual_damage} урона")
            else:
                result.add_message(f"🙏 {self.enemy.name} промахнулся тяжелой атакой")
        
        elif enemy_action == CombatAction.DEFEND:
            result.add_message(f"🛡️ {self.enemy.name} защищается")
    
    def is_player_dead(self):
        """Проверяет, мертв ли игрок"""
        return self.player.hp <= 0
    
    def is_enemy_dead(self):
        """Проверяет, мертв ли враг"""
        return self.enemy.hp <= 0
    
    def get_battle_status(self):
        """Возвращает статус боя"""
        player_hp_bar = self._get_hp_bar(self.player.hp, self.player.max_hp)
        enemy_hp_bar = self.enemy.get_hp_bar()
        
        # Информация о комбо
        combo_info = ""
        if self.combo.combo_counter >= 3:
            combo_info = f"🔥 Комбо x{self.combo.combo_counter}!"
        
        # Информация о мане
        mana_bar = self._get_hp_bar(self.player.mana, self.player.max_mana, "💙")
        
        # Информация о враге
        enemy_info = self.enemy.get_battle_string()
        
        # Информация о фласках
        flask_status = []
        for i, flask in enumerate(self.player.flasks):
            marker = "👉" if i == self.player.active_flask else "  "
            flask_status.append(f"{marker} {flask.get_status()}")
        flask_text = "\n".join(flask_status)
        
        return {
            "player_hp": f"👤 {player_hp_bar}",
            "player_mana": f"💙 {mana_bar}",
            "enemy_info": enemy_info,
            "combo": combo_info,
            "flasks": flask_text,
            "turn": self.turn_count
        }
    
    def _get_hp_bar(self, current, max_hp, emoji="❤️", length=10):
        """Возвращает полоску здоровья"""
        filled = int((current / max_hp) * length)
        bar = "█" * filled + "░" * (length - filled)
        
        hp_percent = (current / max_hp) * 100
        if hp_percent > 66:
            color = "🟢"
        elif hp_percent > 33:
            color = "🟡"
        else:
            color = "🔴"
        
        return f"{color} {bar} {current}/{max_hp}"
    
    def _add_to_log(self, result):
        """Добавляет результат в лог боя"""
        self.battle_log.append({
            "turn": self.turn_count,
            "player_damage": result.player_damage,
            "enemy_damage": result.enemy_damage,
            "player_heal": result.player_heal,
            "crit": result.crit,
            "dodged": result.dodged,
            "messages": result.messages.copy()
        })
        
        # Ограничим лог последними 10 записями
        if len(self.battle_log) > 10:
            self.battle_log = self.battle_log[-10:]
    
    def get_battle_log(self):
        """Возвращает лог боя"""
        if not self.battle_log:
            return "История боя пуста"
        
        lines = ["📋 **ИСТОРИЯ БОЯ**\n"]
        for entry in self.battle_log[-5:]:
            lines.append(f"**Ход {entry['turn']}:**")
            for msg in entry['messages'][:2]:
                lines.append(f"  {msg}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_summary(self):
        """Возвращает сводку по бою"""
        return (
            f"📊 **ИТОГИ БОЯ**\n\n"
            f"⏱️ Ходов: {self.turn_count}\n"
            f"⚔️ Твой урон: {self.player_total_damage}\n"
            f"💥 Урон врага: {self.enemy_total_damage}\n"
            f"🔥 Макс. комбо: {self.combo.combo_counter}"
        )


# ============= ФАЗЫ БОССА =============

class BossPhase:
    """Фаза босса"""
    
    def __init__(self, name, hp_percent, damage_mult=1.0, speed_mult=1.0, adds=None):
        self.name = name
        self.hp_percent = hp_percent
        self.damage_mult = damage_mult
        self.speed_mult = speed_mult
        self.adds = adds or []
        self.activated = False
    
    def check_activation(self, current_hp, max_hp):
        """Проверяет, нужно ли активировать фазу"""
        hp_percent = (current_hp / max_hp) * 100
        return not self.activated and hp_percent <= self.hp_percent
    
    def activate(self, enemy):
        """Активирует фазу"""
        self.activated = True
        enemy.damage_min = int(enemy.damage_min * self.damage_mult)
        enemy.damage_max = int(enemy.damage_max * self.damage_mult)
        
        messages = [f"⚠️ **{self.name}**"]
        
        if self.adds:
            messages.append(f"👥 {self.name}: призыв миньонов!")
        
        return messages
