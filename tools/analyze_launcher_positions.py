#!/usr/bin/env python3
"""Аналізатор позицій кнопок для LCARS лаунчера

Цей скрипт аналізує фонові зображення і знаходить оптимальні позиції для кнопок
на основі кольорових областей та геометрії LCARS інтерфейсу.
"""

import sys
import os
sys.path.insert(0, '')
from PIL import Image
import numpy as np
import json
from tools.extract_palettes import extract_bands, extract_colors_from_band

def analyze_image_for_positions(image_path):
    """Аналізує зображення і знаходить позиції для кнопок"""
    print(f"Аналіз зображення: {image_path}")
    
    im = Image.open(image_path).convert('RGB')
    w, h = im.size
    print(f"Розмір: {w}x{h}")
    
    arr = np.array(im)
    brightness = arr.max(axis=2)
    mask = brightness > 30
    
    # Аналізуємо горизонтальні смуги для кнопок фракцій (ліворуч)
    left_region = arr[:, :w//4, :]  # Ліві 25% екрану
    left_brightness = left_region.max(axis=2)
    left_mask = left_brightness > 30
    left_y_hist = left_mask.sum(axis=1)
    
    # Знаходимо горизонтальні смуги для кнопок фракцій
    faction_positions = []
    th = max(3, int((w//4) * 0.01))
    in_band = False
    start = 0
    for y, v in enumerate(left_y_hist):
        if not in_band and v >= th:
            in_band = True
            start = y
        elif in_band and v < th:
            in_band = False
            end = y
            if end - start > 20:  # Мінімальна висота кнопки
                faction_positions.append((10, start, 90, end - start))
    if in_band:
        faction_positions.append((10, start, 90, h - start))
    
    # Аналізуємо верхню область для DATE/MOD/BACK кнопок
    top_region = arr[:h//6, :, :]  # Верхні 17% екрану
    top_brightness = top_region.max(axis=2)
    top_mask = top_brightness > 30
    top_x_hist = top_mask.sum(axis=0)
    
    # Знаходимо вертикальні смуги для верхніх кнопок
    side_positions = []
    thx = max(3, int((h//6) * 0.05))
    in_block = False
    bx = 0
    for x, v in enumerate(top_x_hist):
        if not in_block and v >= thx:
            in_block = True
            bx = x
        elif in_block and v < thx:
            in_block = False
            ex = x
            if ex - bx > 30:  # Мінімальна ширина кнопки
                side_positions.append((bx, 10, ex - bx, 60))
    if in_block:
        side_positions.append((bx, 10, w - bx, 60))
    
    # Аналізуємо центральну область для головного екрану
    center_x = w // 2
    center_y = h // 2
    info_screen_pos = (center_x - 300, center_y - 175, 600, 350)
    
    # Аналізуємо нижню область для ACTIVATE кнопки
    bottom_y = h - 100
    activate_pos = (center_x - 110, bottom_y, 220, 60)
    
    # Аналізуємо бічні області для кнопок епох
    left_era_positions = []
    right_era_positions = []
    
    # Ліві кнопки епох
    for i in range(3):
        y_pos = h//6 + i * 100
        left_era_positions.append((10, y_pos, 120, 80))
    
    # Праві кнопки епох
    for i in range(3):
        y_pos = h//6 + i * 100
        right_era_positions.append((w - 130, y_pos, 120, 80))
    
    # Позиції для текстових елементів
    title_pos = (w//4, h//10, 400, 40)
    mode_pos = (50, h - 50, 200, 30)
    
    return {
        'image_size': (w, h),
        'faction_buttons': faction_positions[:4],  # Беремо перші 4 позиції
        'side_buttons': side_positions[:3],  # Беремо перші 3 позиції
        'era_buttons_left': left_era_positions,
        'era_buttons_right': right_era_positions,
        'activate_button': activate_pos,
        'title': title_pos,
        'mode_label': mode_pos,
        'info_screen': info_screen_pos
    }

def generate_launcher_code(positions_data):
    """Генерує код для лаунчера на основі позицій"""
    code = f'''# Автоматично згенеровані позиції для лаунчера
# Розмір зображення: {positions_data['image_size'][0]}x{positions_data['image_size'][1]}

# Кнопки фракцій
faction_positions = {positions_data['faction_buttons']}

# Кнопки DATE, MOD, BACK
side_positions = {positions_data['side_buttons']}

# Кнопки епох ліворуч
era_left_positions = {positions_data['era_buttons_left']}

# Кнопки епох праворуч
era_right_positions = {positions_data['era_buttons_right']}

# Кнопка ACTIVATE
activate_position = {positions_data['activate_button']}

# Заголовок
title_position = {positions_data['title']}

# MODE label
mode_position = {positions_data['mode_label']}

# Центральний екран
info_screen_position = {positions_data['info_screen']}
'''
    return code

def main():
    # Аналізуємо обидва фонові зображення
    images = [
        "resources/PCARS_22.png",
        "resources/COMS2.png"
    ]
    
    all_positions = {}
    
    for image_path in images:
        if os.path.exists(image_path):
            positions = analyze_image_for_positions(image_path)
            all_positions[image_path] = positions
            print(f"\nПозиції для {image_path}:")
            print(json.dumps(positions, indent=2))
        else:
            print(f"Зображення не знайдено: {image_path}")
    
    # Генеруємо код для лаунчера
    if all_positions:
        first_image = list(all_positions.keys())[0]
        launcher_code = generate_launcher_code(all_positions[first_image])
        
        # Зберігаємо код у файл
        with open('launcher_positions_generated.py', 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        
        print(f"\nЗгенеровано код у файл: launcher_positions_generated.py")
        print("\nСкопіюйте ці позиції у ваш launcher.py:")
        print(launcher_code)
    else:
        print("Не вдалося проаналізувати жодне зображення")

if __name__ == '__main__':
    main()
