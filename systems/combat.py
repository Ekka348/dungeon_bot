import random
import asyncio
from enum import Enum
from models.player import Player
from models.enemy import Enemy
from models.item import Item, MeleeWeapon, Flask

# ============= ТИПЫ ДЕЙСТВИЙ В БОЮ =============

class CombatAction(Enum):
    ATTACK = "attack"       # Атака
    HEAVY_ATTACK = "heavy"  # Тяжелая атака (тратит больше энергии, но больше урона)
    FAST_ATTACK = "fast"    # Быстрая атака (меньше урона, но выше шанс)
    DEFEND = "defend"       # Защита (снижает получаемый урон)
    DODGE = "dodge"         # Уклонение (шанс полностью избежать урона)
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
        self.combo_timer = 3  # 3 хода на поддержание комбо
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


# ============= СИСТЕМА ЭНЕРГИИ =============

class EnergySystem:
    """Система энергии для боя"""
    
    def __init__(self, max_energy=3):
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.energy_regen = 1  # Восстановление в ход
    
    def can_use_action(self, action_cost):
        """Проверяет, хватает ли энергии"""
        return self.current_energy >= action_cost
    
    def use_energy(self, cost):
        """Тратит энергию"""
        if self.can_use_action(cost):
            self.current_energy -= cost
            return True
        return False
    
    def regen(self):
        """Восстанавливает энергию"""
        self.current_energy = min(self.max_energy, self.current_energy + self.energy_regen)
    
    def get_energy_bar(self, length=5):
        """Возвращает визуальную полоску энергии"""
        filled = int((self.current_energy / self.max_energy) * length)
        return "🔋" * filled + "⚪" * (length - filled)


# ============= СИСТЕМА ФАЗ БОССА =============

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


# ============= ОСНОВНАЯ СИСТЕМА БОЯ =============

class CombatSystem:
    """Основная система боя"""
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.combo = ComboSystem()
        self.player_energy = EnergySystem(3)
        self.enemy_energy = EnergySystem(2)  # У врагов меньше энергии
        
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
        
        # Восстановление энергии
        self.player_energy.regen()
        
        # Добавляем в лог
        self._add_to_log(result)
        
        return result
    
    def _choose_enemy_action(self):
        """ИИ врага выбирает действие"""
        # Простая логика: если у врага мало здоровья, чаще защищается
        hp_percent = self.enemy.get_hp_percent()
        
        if hp_percent < 30 and random.random() < 0.4:
            return CombatAction.DEFEND
        elif self.enemy_energy.current_energy >= 2 and random.random() < 0.3:
            return CombatAction.HEAVY_ATTACK
        else:
            return CombatAction.ATTACK
    
    def _process_attack(self, result, enemy_action):
        """Обрабатывает обычную атаку"""
        # Стоимость энергии
        if not self.player_energy.use_energy(1):
            result.add_message("⚡ Не хватает энергии!")
            return
        
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
                result.add_message(f"⚔️ {damage} урона")
            
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
        """Обрабатывает тяжелую атаку (больше урона, тратит 2 энергии)"""
        if not self.player_energy.use_energy(2):
            result.add_message("⚡ Не хватает энергии для тяжелой атаки!")
            self._process_attack(result, enemy_action)
            return
        
        hit_chance = self.player.accuracy - 10  # Тяжелая атака менее точная
        
        if random.randint(1, 100) <= hit_chance:
            damage = int(self.player.get_total_damage() * 1.5)  # 50% больше урона
            
            if random.randint(1, 100) <= self.player.crit_chance:
                damage = int(damage * (self.player.crit_multiplier / 100))
                result.crit = True
                result.add_message(f"🔥 КРИТИЧЕСКАЯ ТЯЖЕЛАЯ АТАКА! {damage} урона")
            else:
                result.add_message(f"⚔️💪 Тяжелая атака! {damage} урона")
            
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
        """Обрабатывает быструю атаку (меньше урона, но выше шанс)"""
        if not self.player_energy.use_energy(1):
            result.add_message("⚡ Не хватает энергии!")
            return
        
        hit_chance = self.player.accuracy + 15  # Быстрая атака точнее
        
        if random.randint(1, 100) <= hit_chance:
            damage = int(self.player.get_total_damage() * 0.7)  # 30% меньше урона
            
            # Повышенный шанс крита
            crit_chance = self.player.crit_chance + 10
            if random.randint(1, 100) <= crit_chance:
                damage = int(damage * (self.player.crit_multiplier / 100))
                result.crit = True
                result.add_message(f"🔥 КРИТИЧЕСКАЯ БЫСТРАЯ АТАКА! {damage} урона")
            else:
                result.add_message(f"⚡ Быстрая атака! {damage} урона")
            
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
        if not self.player_energy.use_energy(1):
            result.add_message("⚡ Не хватает энергии!")
            return
        
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
        if not self.player_energy.use_energy(1):
            result.add_message("⚡ Не хватает энергии!")
            return
        
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
            # Пробуем переключиться
            if self.player._switch_to_next_flask():
                result.add_message(f"🔄 Переключено на {self.player.flasks[self.player.active_flask].name}")
        
        # Враг может атаковать во время использования фласки
        if self.enemy.is_alive() and random.random() < 0.7:  # 70% шанс что враг атакует
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
        if random.random() < 0.5:  # 50% шанс
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
            if self.enemy_energy.use_energy(2):
                if random.randint(1, 100) <= self.enemy.accuracy - 10:
                    damage = int(self.enemy.attack() * 1.5)
                    actual_damage = self.player.take_damage(damage)
                    result.enemy_damage = actual_damage
                    self.enemy_total_damage += actual_damage
                    result.add_message(f"💥💪 {self.enemy.name} использует тяжелую атаку: {actual_damage} урона")
                else:
                    result.add_message(f"🙏 {self.enemy.name} промахнулся тяжелой атакой")
            else:
                # Если нет энергии, обычная атака
                self._process_enemy_attack(result, CombatAction.ATTACK)
        
        elif enemy_action == CombatAction.DEFEND:
            result.add_message(f"🛡️ {self.enemy.name} защищается")
        
        # Враг восстанавливает энергию
        self.enemy_energy.regen()
    
    def is_player_dead(self):
        """Проверяет, мертв ли игрок"""
        return self.player.hp <= 0
    
    def is_enemy_dead(self):
        """Проверяет, мертв ли враг"""
        return self.enemy.hp <= 0
    
    def get_battle_status(self):
        """Возвращает статус боя"""
        # Полоски здоровья
        player_hp_bar = self._get_hp_bar(self.player.hp, self.player.max_hp)
        enemy_hp_bar = self.enemy.get_hp_bar()
        
        # Информация о комбо
        combo_info = ""
        if self.combo.combo_counter >= 3:
            combo_info = f"🔥 Комбо x{self.combo.combo_counter}!"
        
        # Информация об энергии
        energy_bar = self.player_energy.get_energy_bar()
        
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
            "enemy_info": enemy_info,
            "energy": f"⚡ Энергия: {energy_bar}",
            "combo": combo_info,
            "flasks": flask_text,
            "turn": self.turn_count
        }
    
    def _get_hp_bar(self, current, max_hp, length=10):
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
        for entry in self.battle_log[-5:]:  # Последние 5 ходов
            lines.append(f"**Ход {entry['turn']}:**")
            for msg in entry['messages'][:2]:  # Первые 2 сообщения
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


# ============= ТЕСТОВЫЕ ФУНКЦИИ =============

def test_combat_system():
    """Тест боевой системы"""
    print("=" * 50)
    print("ТЕСТ БОЕВОЙ СИСТЕМЫ")
    print("=" * 50)
    
    # Создаем тестового игрока
    player = Player()
    
    # Создаем тестового врага
    from data.act1 import Act1
    monster_data = Act1.get_random_monster(1, "common")
    enemy = Enemy.from_monster_data(monster_data, area_level=1, rarity="common")
    
    print("\n🔹 Начало боя:")
    print(f"Игрок: {player.hp}/{player.max_hp} HP")
    print(f"Враг: {enemy.hp}/{enemy.max_hp} HP")
    
    # Создаем боевую систему
    combat = CombatSystem(player, enemy)
    
    # Симулируем несколько ходов
    actions = [CombatAction.ATTACK, CombatAction.HEAVY_ATTACK, 
               CombatAction.FAST_ATTACK, CombatAction.DEFEND, 
               CombatAction.DODGE, CombatAction.USE_FLASK]
    
    turn = 1
    while not combat.is_player_dead() and not combat.is_enemy_dead() and turn <= 10:
        print(f"\n🔸 ХОД {turn}")
        print("-" * 30)
        
        # Случайное действие
        action = random.choice(actions)
        print(f"Действие: {action.value}")
        
        # Обрабатываем ход
        result = combat.process_turn(action)
        
        # Выводим результат
        print(result.get_text())
        print()
        
        # Выводим статус
        status = combat.get_battle_status()
        print(status["enemy_info"])
        print(status["player_hp"])
        print(status["energy"])
        if status["combo"]:
            print(status["combo"])
        print(status["flasks"])
        
        turn += 1
    
    # Итоги
    print("\n🔹 ИТОГИ БОЯ:")
    if combat.is_enemy_dead():
        print(f"🎉 Победа! Враг повержен за {turn-1} ходов")
    elif combat.is_player_dead():
        print(f"💀 Поражение...")
    
    print(combat.get_summary())
    print("\n" + combat.get_battle_log())


if __name__ == "__main__":
    test_combat_system()
