# LCARS Vision v1.0.0 - Аналіз зображень для конструктора інтерфейсів
# Це утиліта яка аналізує фонові зображення LCARS інтерфейсів
# Автоматично знаходить позиції кнопок, панелей, екранів та кольорові схеми
# Використовується для генерації JSON конфігурації UI конструктора
# Підтримує детекцію лівої/правої/нижньої панелей, кнопок, палітри
# Повертає повний аналіз геометрії та стилів інтерфейсу
# Автор: LCARS Development Team
# Ліцензія: MIT

import json
from typing import Dict, List, Tuple, Any
from lcars.base.version import getVersion

version = getVersion()
print(f"LCARS Vision v{version}")

import numpy as np
from PIL import Image
from scipy import ndimage
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QRect, pyqtSignal
from PyQt6.QtGui import QColor

import pytesseract


class ColorLab:
    # Лабораторія аналізу кольорів з зображення
    
    @staticmethod
    def extract_dominant_colors(image_array, num_colors=10):
        # Витягує домінуючі кольори з зображення
        pixels = image_array.reshape(-1, 3)
        
        # Використовуємо k-means для кластеризації кольорів
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=num_colors, random_state=42)
        kmeans.fit(pixels)
        
        colors = []
        for color in kmeans.cluster_centers_:
            r, g, b = [int(c) for c in color]
            colors.append({
                "rgb": [r, g, b],
                "hex": f"#{r:02x}{g:02x}{b:02x}",
                "brightness": (r + g + b) / 3
            })
        
        return sorted(colors, key=lambda x: x["brightness"], reverse=True)
    
    @staticmethod
    def analyze_color_distribution(image_array):
        # Аналізує розподіл кольорів по каналах
        r_hist = np.histogram(image_array[:, :, 0], bins=256, range=(0, 256))[0]
        g_hist = np.histogram(image_array[:, :, 1], bins=256, range=(0, 256))[0]
        b_hist = np.histogram(image_array[:, :, 2], bins=256, range=(0, 256))[0]
        
        return {
            "red_peaks": ColorLab.find_peaks(r_hist),
            "green_peaks": ColorLab.find_peaks(g_hist),
            "blue_peaks": ColorLab.find_peaks(b_hist),
            "dominant_channel": ["red", "green", "blue"][np.argmax([r_hist.max(), g_hist.max(), b_hist.max()])]
        }
    
    @staticmethod
    def find_peaks(hist, min_height=1000):
        # Шукає піки в гістограмі
        peaks = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > min_height:
                peaks.append(i)
        return peaks
    
    @staticmethod
    def detect_lcars_color_scheme(image_array):
        # Визначає LCARS кольорову схему
        dominant_colors = ColorLab.extract_dominant_colors(image_array, 8)
        color_dist = ColorLab.analyze_color_distribution(image_array)
        
        # Аналізуємо кольори за LCARS стандартами
        lcars_colors = {
            "primary_buttons": [],
            "secondary_buttons": [],
            "alerts": [],
            "panels": [],
            "background": None
        }
        
        for color in dominant_colors:
            r, g, b = color["rgb"]
            
            # Червоні кнопки (LCARS primary)
            if r > 180 and g < 100 and b < 100:
                lcars_colors["primary_buttons"].append(color)
            
            # Сині/бірюзові кнопки (LCARS secondary)
            elif r < 100 and g > 100 and b > 150:
                lcars_colors["secondary_buttons"].append(color)
            
            # Жовті/помаранчеві алерти
            elif r > 200 and g > 150 and b < 100:
                lcars_colors["alerts"].append(color)
            
            # Темні панелі
            elif r < 50 and g < 50 and b < 50:
                lcars_colors["panels"].append(color)
            
            # Фон
            elif r < 30 and g < 30 and b < 30:
                lcars_colors["background"] = color
        
        return lcars_colors
    
    @staticmethod
    def generate_color_palette(lcars_colors):
        # Генерує повну палітру на основі аналізу
        palette = {
            "background": "#000000",
            "primary": "#FF6B6B",
            "secondary": "#00FFCC",
            "accent": "#FF9900",
            "alert": "#FFD700",
            "text": "#FFFFFF",
            "border": "#FF9999"
        }
        
        # Оновлюємо на основі знайдених кольорів
        if lcars_colors["background"]:
            palette["background"] = lcars_colors["background"]["hex"]
        
        if lcars_colors["primary_buttons"]:
            palette["primary"] = lcars_colors["primary_buttons"][0]["hex"]
        
        if lcars_colors["secondary_buttons"]:
            palette["secondary"] = lcars_colors["secondary_buttons"][0]["hex"]
        
        if lcars_colors["alerts"]:
            palette["alert"] = lcars_colors["alerts"][0]["hex"]
        
        return palette


class UIAnalyzer:
    # Аналізує зображення для пошуку оптимальних позицій UI елементів
    
    @staticmethod
    def extract_text_from_region(image_array, region):
        # Витягує текст з області зображення через OCR
        
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        region_array = image_array[y:y+h, x:x+w]
        
        # Конвертуємо в PIL для OCR
        region_image = Image.fromarray(region_array)
        
        text = pytesseract.image_to_string(region_image, config='--psm 7')
        return text.strip()
    
    @staticmethod
    def detect_element_type(image_array, region):
        # Визначає тип елемента за кольором та формою
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        region_array = image_array[y:y+h, x:x+w]
        
        # Аналізуємо середній колір
        mean_color = region_array.mean(axis=(0, 1))
        r, g, b = mean_color
        
        # Визначаємо тип за кольором
        if r > 150 and g < 100 and b < 100:
            return "button_red"
        elif r < 100 and g > 150 and b < 100:
            return "button_green"
        elif r < 100 and g < 100 and b > 150:
            return "button_blue"
        elif r > 200 and g > 200 and b < 100:
            return "button_yellow"
        elif r < 50 and g < 50 and b < 50:
            return "panel_dark"
        else:
            return "label"
    
    @staticmethod
    def detect_gradients(image_array):
        # Детектує градієнти та тіні
        gray = np.mean(image_array, axis=2)
        grad_x = np.gradient(gray, axis=1)
        grad_y = np.gradient(gray, axis=0)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Шукаємо області з сильними градієнтами
        gradient_regions = gradient_magnitude > np.percentile(gradient_magnitude, 90)
        
        return {
            "has_gradients": gradient_regions.any(),
            "gradient_intensity": float(gradient_magnitude.mean()),
            "shadow_regions": gradient_regions.sum()
        }
    
        
    @staticmethod
    def analyze_background(image_path: str) -> Dict[str, Any]:
        # Аналізує зображення і повертає словник знайдених UI областей
        
        
        im = Image.open(image_path).convert('RGB')
        w, h = im.size

        # Використовуємо NumPy для швидкості
        arr = np.array(im)
        brightness = arr.max(axis=2)

        # Простий поріг для LCARS елементів
        mask = brightness > 30

        # 1. Шукаємо ліву панель навігації
        left_region = arr[:, :w//4, :]
        left_mask = left_region.max(axis=2) > 30
        left_y_hist = left_mask.sum(axis=1)
        
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
                if end - start > 20:
                    faction_positions.append({"x": 10, "y": start, "w": 90, "h": end - start})
        
        # 2. Детекція кнопок по всьому екрану з розширеним аналізом
        button_positions = []
        button_masks = [
            (arr[:, :, 0] > 100) & (arr[:, :, 1] < 50) & (arr[:, :, 2] < 50),  # Червоні
            (arr[:, :, 0] < 50) & (arr[:, :, 1] > 100) & (arr[:, :, 2] < 50),  # Зелені
            (arr[:, :, 0] < 50) & (arr[:, :, 1] < 50) & (arr[:, :, 2] > 100),  # Сині
        ]
        
        for color_idx, button_mask in enumerate(button_masks):
            labeled, num_features = ndimage.label(button_mask)
            
            for i in range(1, min(num_features + 1, 20)):
                coords = np.where(labeled == i)
                if len(coords[0]) > 50:
                    y_min, y_max = coords[0].min(), coords[0].max()
                    x_min, x_max = coords[1].min(), coords[1].max()
                    
                    button_data = {
                        "x": x_min, "y": y_min, 
                        "w": x_max - x_min, "h": y_max - y_min,
                        "type": ["button_red", "button_green", "button_blue"][color_idx],
                        "text": UIAnalyzer.extract_text_from_region(arr, {
                            "x": x_min, "y": y_min, "w": x_max - x_min, "h": y_max - y_min
                        })
                    }
                    button_positions.append(button_data)
        
        # 3. Аналіз кольорової палітри через ColorLab
        lcars_scheme = ColorLab.detect_lcars_color_scheme(arr)
        color_palette = ColorLab.generate_color_palette(lcars_scheme)
        dominant_colors = ColorLab.extract_dominant_colors(arr, 10)
        color_distribution = ColorLab.analyze_color_distribution(arr)
        
        # 4. Детекція правої панелі
        right_region = arr[:, 3*w//4:, :]
        right_mask = right_region.max(axis=2) > 30
        right_y_hist = right_mask.sum(axis=1)
        
        right_positions = []
        in_band = False
        start = 0
        for y, v in enumerate(right_y_hist):
            if not in_band and v >= th:
                in_band = True
                start = y
            elif in_band and v < th:
                in_band = False
                end = y
                if end - start > 20:
                    right_positions.append({"x": 3*w//4 + 10, "y": start, "w": 90, "h": end - start})
        
        # 5. Детекція нижньої панелі
        bottom_region = arr[4*h//5:, :, :]
        bottom_mask = bottom_region.max(axis=2) > 30
        bottom_x_hist = bottom_mask.sum(axis=0)
        
        bottom_positions = []
        in_band = False
        start = 0
        for x, v in enumerate(bottom_x_hist):
            if not in_band and v >= th:
                in_band = True
                start = x
            elif in_band and v < th:
                in_band = False
                end = x
                if end - start > 30:
                    bottom_positions.append({"x": start, "y": 4*h//5 + 10, "w": end - start, "h": 40})
        
        # 6. Аналіз градієнтів та тіней
        gradient_analysis = UIAnalyzer.detect_gradients(arr)
        
        # Повертаємо повний аналіз з ColorLab результатами
        return {
            "image_size": [w, h],
            "faction_buttons": faction_positions[:4],
            "info_screen": {"x": w//4, "y": h//6, "w": w//2, "h": h//2},
            "buttons": button_positions[:15],
            "color_scheme": lcars_scheme,
            "color_palette": color_palette,
            "dominant_colors": dominant_colors,
            "color_distribution": color_distribution,
            "right_panel": right_positions[:3],
            "bottom_panel": bottom_positions[:5],
            "brightness": float(arr.mean()),
            "contrast": float(arr.std()),
            "gradients": gradient_analysis,
                    }

    @staticmethod
    def generate_ui_from_image(image_path: str) -> QWidget:
        # Створює повноцінний PyQt6 інтерфейс з аналізу зображення
        return LCARSAutoWidget(image_path)

    @staticmethod
    def generate_layout_json(analysis_results: Dict[str, Any], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=4)


class LCARSAutoWidget(QWidget):
    # Автоматично згенерований LCARS віджет з сигналами
    
    button_clicked = pyqtSignal(str)
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.analysis = UIAnalyzer.analyze_background(image_path)
        self.setup_ui()
    
    def setup_ui(self):
        # Налаштовуємо UI на основі аналізу
        w, h = self.analysis["image_size"]
        
        # Адаптивний розмір під екран
        screen_size = QApplication.primaryScreen().size()
        scale_x = screen_size.width() * 0.8 / w
        scale_y = screen_size.height() * 0.8 / h
        scale = min(scale_x, scale_y, 1.0)  # Не збільшувати
        
        self.setFixedSize(int(w * scale), int(h * scale))
        
        # Використовуємо палітру з ColorLab
        palette = self.analysis["color_palette"]
        self.setStyleSheet(f"background-color: {palette['background']};")
        
        # Створюємо кнопки фракцій з текстом з OCR
        for i, btn_data in enumerate(self.analysis["faction_buttons"]):
            btn = QPushButton(self)
            btn.setGeometry(
                int(btn_data["x"] * scale), 
                int(btn_data["y"] * scale), 
                int(btn_data["w"] * scale), 
                int(btn_data["h"] * scale)
            )
            
            text = btn_data.get("text", f"F{i+1}") if "text" in btn_data else f"F{i+1}"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {palette['primary']};
                    border: 2px solid {palette['border']};
                    color: {palette['text']};
                    font-weight: bold;
                    font-family: 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {palette['secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {palette['border']};
                }}
            """)
            btn.setText(text)
            btn.clicked.connect(lambda checked, t=text: self.button_clicked.emit(f"faction_{t}"))
        
        # Створюємо інформаційний екран
        screen_data = self.analysis["info_screen"]
        screen = QLabel(self)
        screen.setGeometry(
            int(screen_data["x"] * scale), 
            int(screen_data["y"] * scale), 
            int(screen_data["w"] * scale), 
            int(screen_data["h"] * scale)
        )
        screen.setStyleSheet(f"""
            QLabel {{
                background-color: {palette['secondary']};
                border: 2px solid {palette['border']};
                color: {palette['text']};
                font-family: 'Courier New', monospace;
            }}
        """)
        screen.setText("INFO SCREEN")
        screen.setAlignment(32)  # Center alignment
        
        # Створюємо кнопки з розпізнаним текстом
        for i, btn_data in enumerate(self.analysis["buttons"]):
            btn = QPushButton(self)
            btn.setGeometry(
                int(btn_data["x"] * scale), 
                int(btn_data["y"] * scale), 
                int(btn_data["w"] * scale), 
                int(btn_data["h"] * scale)
            )
            
            # Використовуємо розпізнаний текст або тип кнопки
            text = btn_data.get("text", btn_data.get("type", f"B{i+1}"))
            
            # Використовуємо кольори з ColorLab
            btn_color = palette.get('accent', palette['primary'])
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    border: 1px solid {palette['border']};
                    color: {palette['text']};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {palette['secondary']};
                }}
            """)
            btn.setText(text)
            btn.clicked.connect(lambda checked, t=text: self.button_clicked.emit(f"button_{t}"))
        
        # Створюємо праву панель
        for i, panel_data in enumerate(self.analysis["right_panel"]):
            panel = QLabel(self)
            panel.setGeometry(
                int(panel_data["x"] * scale), 
                int(panel_data["y"] * scale), 
                int(panel_data["w"] * scale), 
                int(panel_data["h"] * scale)
            )
            panel.setStyleSheet(f"""
                QLabel {{
                    background-color: {palette['secondary']};
                    border: 2px solid {palette['border']};
                    color: {palette['text']};
                }}
            """)
            panel.setText(f"R{i+1}")
        
        # Створюємо нижню панель
        for i, panel_data in enumerate(self.analysis["bottom_panel"]):
            panel = QLabel(self)
            panel.setGeometry(
                int(panel_data["x"] * scale), 
                int(panel_data["y"] * scale), 
                int(panel_data["w"] * scale), 
                int(panel_data["h"] * scale)
            )
            panel.setStyleSheet(f"""
                QLabel {{
                    background-color: {palette['primary']};
                    border: 2px solid {palette['border']};
                    color: {palette['text']};
                }}
            """)
            panel.setText(f"BOT{i+1}")

    
