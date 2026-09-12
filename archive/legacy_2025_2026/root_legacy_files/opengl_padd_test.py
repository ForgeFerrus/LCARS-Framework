#!/usr/bin/env python3
# Простий тест LCARS OpenGL PADD
import sys
import os

# Додаємо шлях до LCARS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lcars_opengl_renderer import LCARSPadd, LCARSOpenGLRenderer
from lcars.base.component import Surface, Symbol, Structure

class SimpleLCARSPadd:
    def __init__(self):
        # Створюємо рендерер для PADD (800x600 - адаптивний)
        self.renderer = LCARSOpenGLRenderer(800, 600)
        self.padd = LCARSPadd(self.renderer)
        
        # Створюємо базові елементи
        self.setup_interface()
        
    def setup_interface(self):
        """Створюємо інтерфейс PADD"""
        
        # --- Верхня панель ---
        # Elbow ліворуч
        self.header_elbow = Structure(
            3001,  # Top-left elbow
            Parent=None,
            Text="◤ PADD INTERFACE",
            Color="#FFFF00",
            X=10, Y=10,
            Width=200, Height=50
        )
        
        # Status
        self.status = Surface(
            1001,  # Button
            Parent=None,
            Text="SYSTEM ONLINE",
            Color="#00FF00",
            X=220, Y=15,
            Width=200, Height=30
        )
        
        # Час
        self.time_label = Symbol(
            2001,  # Text
            Parent=None,
            Text="15:47:23",
            Color="#FF9900",
            X=600, Y=15,
            Width=150, Height=30
        )
        
        # --- Основна область ---
        # Ліва панель кнопок
        self.left_buttons = []
        buttons_data = [
            ("◤ SENSORS", "#FFFF00"),
            ("◤ COMM", "#FF9900"),
            ("◤ TACTICAL", "#FF0000"),
            ("◤ SCIENCE", "#00FF00"),
            ("◤ ENGINEERING", "#FFFF00")
        ]
        
        for i, (text, color) in enumerate(buttons_data):
            btn = Surface(
                1001,  # Button
                Parent=None,
                Text=text,
                Color=color,
                X=10, Y=80 + i * 45,
                Width=180, Height=40
            )
            self.left_buttons.append(btn)
        
        # Центральна область (простір)
        self.center_area = Structure(
            3010,  # Horizontal bar
            Parent=None,
            Color="#333333",
            X=200, Y=80,
            Width=400, Height=2
        )
        
        # Права панель даних
        self.right_indicators = []
        for i in range(5):
            indicator = Surface(
                1007,  # Indicator
                Parent=None,
                Text=f"DATA-{i+1}",
                Color="#00FF00",
                X=620, Y=80 + i * 35,
                Width=150, Height=30
            )
            self.right_indicators.append(indicator)
        
        # --- Нижня панель ---
        self.footer_elbow = Structure(
            3003,  # Bottom-left elbow
            Parent=None,
            Text="◤ SECURE",
            Color="#FF9900",
            X=10, Y=520,
            Width=200, Height=40
        )
        
        # Додаємо всі компоненти до PADD
        all_components = [
            self.header_elbow, self.status, self.time_label,
            self.center_area, self.footer_elbow
        ]
        all_components.extend(self.left_buttons)
        all_components.extend(self.right_indicators)
        
        for comp in all_components:
            self.padd.add_component(comp)
    
    def print_components(self):
        """Друкуємо інформацію про компоненти"""
        print("LCARS PADD Components:")
        print("-" * 50)
        total = len(self.padd.components)
        print(f"Всього компонентів: {total}")
        print(f"Розмір PADD: {self.padd.width}x{self.padd.height}")
        print("-" * 50)
        
        for i, comp in enumerate(self.padd.components[:10]):  # Перші 10
            comp_type = comp.__class__.__name__
            
            # Перевіряємо атрибути
            print(f"Компонент {i+1}: {comp_type}")
            print(f"  Атрибути: {dir(comp)}")
            
            x = getattr(comp, 'X', 'NO_X')
            y = getattr(comp, 'Y', 'NO_Y')
            w = getattr(comp, 'Width', 'NO_W')
            h = getattr(comp, 'Height', 'NO_H')
            color = getattr(comp, 'Color', 'NO_COLOR')
            text = getattr(comp, 'Text', 'NO_TEXT')
            
            print(f"  Координати: ({x},{y}) Розмір: {w}x{h}")
            print(f"  Колір: {color} Текст: {text}")
            print()
            
            if i >= 2:  # Обмежуємо для дебагу
                break
        
        if total > 3:
            print(f"... та ще {total-3} компонентів")

def main():
    """Головна функція"""
    print("◤ LCARS PADD INTERFACE TEST ◢")
    print("=" * 40)
    
    try:
        # Створюємо PADD
        padd = SimpleLCARSPadd()
        
        # Показуємо компоненти
        padd.print_components()
        
        print("\n✅ PADD створено успішно!")
        print("📱 Розмір: 800x600 (адаптивний)")
        print("🎨 Колірова схема: LCARS стандарт")
        print("📦 Компоненти: Surface, Symbol, Structure")
        
        # Перевіряємо OpenGL
        from lcars_opengl_renderer import OPENGL_AVAILABLE
        if OPENGL_AVAILABLE:
            print("\n🖥️  OpenGL доступний - можна запускати повний рендеринг")
            print("💡 Запустіть: python lcars_opengl_renderer.py")
        else:
            print("\n⚠️  OpenGL недоступний")
            print("💡 Встановіть: pip install PyOpenGL PyOpenGL_accelerate")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
