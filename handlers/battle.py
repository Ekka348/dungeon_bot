async def handle_victory(self, message: types.Message, state: FSMContext):
    """Обрабатывает победу"""
    data = await state.get_data()
    player = data['player']
    enemy = data['battle_enemy']
    combat = data.get('combat_system')
    events = data.get('dungeon_events', [])
    current_index = player.position_in_location
    
    # Добавляем опыт
    exp_gained = enemy.get_exp_reward()
    levels_gained = player.add_exp(exp_gained)
    
    # Добавляем золото
    gold_gained = enemy.get_gold_reward()
    player.add_gold(gold_gained)
    
    # Восстанавливаем заряды фласок
    charges_restored = player.add_flask_charge()
    
    # Добавляем убийство в статистику
    player.add_kill(enemy.name)
    
    # Генерируем лут
    area_level = AreaLevelSystem.get_area_level(player.current_location)
    loot = self.loot_system.generate_loot(
        enemy.rarity, 
        area_level, 
        enemy.area_level,  # Используем area_level вместо monster_level
        player.current_location
    )
    
    # Добавляем лут в инвентарь
    loot_text = []
    for loot_item in loot:
        if loot_item.type == "gold":
            loot_text.append(f"💰 {loot_item.amount} золота")
        elif loot_item.item:
            player.add_item(loot_item.item)
            loot_text.append(loot_item.get_name())
    
    # Отмечаем событие как пройденное
    if current_index < len(events):
        events[current_index]["completed"] = True
        await state.update_data(dungeon_events=events)
    
    # Формируем текст победы
    text = f"🎉 **ПОБЕДА!**\n\n"
    text += f"Ты победил {enemy.emoji} {enemy.name}!\n\n"
    text += f"✨ Опыт: +{exp_gained}\n"
    text += f"💰 Золото: +{gold_gained}\n"
    
    if charges_restored > 0:
        text += f"🧪 Восстановлено зарядов фласок: +{charges_restored}\n"
    
    if levels_gained > 0:
        text += f"⬆️ Новый уровень: {player.level}!\n"
    
    if loot_text:
        text += f"\n**Добыча:**\n"
        for item in loot_text:
            text += f"  {item}\n"
    
    # Краткая статистика боя
    if combat:
        text += f"\n{combat.get_summary()}\n"
    
    text += f"\n**Что дальше?**"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Идти дальше", callback_data="next_step")],
        [InlineKeyboardButton(text="🏚️ В убежище", callback_data="return_to_haven")],
        [InlineKeyboardButton(text="📊 Статы", callback_data="show_progression")]
    ])
    
    # Сохраняем обновленного игрока
    await state.update_data(player=player)
    
    # Удаляем сообщение с боем
    try:
        await message.delete()
    except:
        pass
    
    # Отправляем сообщение о победе
    await message.answer(text, reply_markup=keyboard)
