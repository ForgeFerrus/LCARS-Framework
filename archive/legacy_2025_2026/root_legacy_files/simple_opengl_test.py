#!/usr/bin/env python3
# Простий тест LCARS OpenGL без GLUT
import sys
import os

# Додаємо шлях до LCARS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lcars.base.component import Surface, Symbol, Structure

# Перевіряємо OpenGL на рівні модуля
try:
    import OpenGL.GL as GL
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

class SimpleLCARSTest:
    def __init__(self):
        print("◤ LCARS OpenGL COMPONENT TEST ◢")
        print("=" * 50)
        
        # Створюємо тестові компоненти
        self.create_test_components()
        
    def create_test_components(self):
        """Створюємо базові елементи LCARS"""
        
        print("\n📦 Створюємо LCARS компоненти...")
        
        # --- Surface (кнопки) ---
        self.button1 = Surface(
            1001,  # Rect button
            Parent=None,
            Text="◤ BRIDGE",
            Color="#FFFF00",
            X=10, Y=10,
            Width=150, Height=40
        )
        
        self.button2 = Surface(
            1002,  # Rect button
            Parent=None,
            Text="◤ TACTICAL",
            Color="#FF9900",
            X=10, Y=60,
            Width=150, Height=40
        )
        
        # --- Symbol (текст) ---
        self.text1 = Symbol(
            2001,  # Text
            Parent=None,
            Text="STATUS: ONLINE",
            Color="#00FF00",
            X=200, Y=20,
            Width=200, Height=30
        )
        
        # --- Structure (рамки, лінії) ---
        self.elbow1 = Structure(
            3001,  # Top-left elbow
            Parent=None,
            Text="◤ MAIN DISPLAY",
            Color="#FF9900",
            X=10, Y=120,
            Width=250, Height=50
        )
        
        self.bar1 = Structure(
            3010,  # Horizontal bar
            Parent=None,
            Color="#333333",
            X=10, Y=200,
            Width=400, Height=4
        )
        
        # Зберігаємо всі компоненти
        self.components = [
            self.button1, self.button2,
            self.text1,
            self.elbow1, self.bar1
        ]
        
        print(f"✅ Створено {len(self.components)} компонентів")
        
    def test_render_commands(self):
        """Тестуємо генерацію рендер команд"""
        print("\n🎨 Тестуємо рендер команди...")
        
        for i, comp in enumerate(self.components):
            print(f"\n{i+1}. {comp.__class__.__name__}:")
            print(f"   Позиція: ({comp.X}, {comp.Y})")
            print(f"   Розмір: {comp.Width}x{comp.Height}")
            print(f"   Колір: {comp.Color}")
            print(f"   Текст: {comp.Text}")
            
            # Симулюємо рендеринг
            comp.render()
            
            # Отримуємо команди
            commands = comp.get_render_commands()
            print(f"   Команд: {len(commands)}")
            
            for cmd in commands:
                cmd_type = cmd['type']
                if cmd_type == 'rect':
                    print(f"     - Прямокутник: ({cmd['x']},{cmd['y']}) {cmd['w']}x{cmd['h']}")
                elif cmd_type == 'text':
                    print(f"     - Текст: '{cmd['text']}'")
                    
    def create_opengl_commands(self):
        """Створюємо OpenGL команди з компонентів"""
        print("\n🖥️  Генеруємо OpenGL команди...")
        
        opengl_commands = []
        
        for comp in self.components:
            comp.render()
            commands = comp.get_render_commands()
            
            for cmd in commands:
                if cmd['type'] == 'rect':
                    # OpenGL прямокутник
                    gl_cmd = {
                        'type': 'gl_rect',
                        'x': comp.X + cmd['x'],
                        'y': comp.Y + cmd['y'],
                        'w': cmd['w'],
                        'h': cmd['h'],
                        'color': cmd['color']
                    }
                    opengl_commands.append(gl_cmd)
                    
                elif cmd['type'] == 'text':
                    # OpenGL текст
                    gl_cmd = {
                        'type': 'gl_text',
                        'x': comp.X + cmd['x'],
                        'y': comp.Y + cmd['y'],
                        'text': cmd['text'],
                        'color': cmd['color'],
                        'size': cmd['font_size']
                    }
                    opengl_commands.append(gl_cmd)
        
        print(f"✅ Згенеровано {len(opengl_commands)} OpenGL команд")
        
        # Показуємо перші команди
        print("\n📋 Приклад команд:")
        for i, cmd in enumerate(opengl_commands[:5]):
            if cmd['type'] == 'gl_rect':
                print(f"   {i+1}. Прямокутник: ({cmd['x']},{cmd['y']}) {cmd['w']}x{cmd['h']} колір:{cmd['color']}")
            elif cmd['type'] == 'gl_text':
                print(f"   {i+1}. Текст: '{cmd['text']}' на ({cmd['x']},{cmd['y']}) колір:{cmd['color']}")
        
        return opengl_commands
        
    def export_to_file(self, commands, filename="lcars_opengl_data.txt"):
        """Експортуємо команди в файл"""
        print(f"\n💾 Експортуємо в {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("LCARS OpenGL Render Data\n")
            f.write("=" * 40 + "\n\n")
            
            for cmd in commands:
                if cmd['type'] == 'gl_rect':
                    f.write(f"RECT {cmd['x']} {cmd['y']} {cmd['w']} {cmd['h']} {cmd['color']}\n")
                elif cmd['type'] == 'gl_text':
                    f.write(f"TEXT {cmd['x']} {cmd['y']} {cmd['text']} {cmd['color']} {cmd['size']}\n")
        
        print(f"✅ Дані збережено в {filename}")

def main():
    """Головна функція"""
    try:
        # Створюємо тест
        test = SimpleLCARSTest()
        
        # Тестуємо рендер команди
        test.test_render_commands()
        
        # Створюємо OpenGL команди
        commands = test.create_opengl_commands()
        
        # Експортуємо в файл
        test.export_to_file(commands)
        
        print("\n🎉 Тест завершено успішно!")
        print("📁 Файл lcars_opengl_data.txt готовий для OpenGL рендерингу")
        
        # Перевіряємо OpenGL
        if OPENGL_AVAILABLE:
            print("\n🖥️  OpenGL доступний - можна робити повний рендеринг!")
        else:
            print("\n⚠️  OpenGL не встановлено")
            print(" pip install PyOpenGL PyOpenGL_accelerate")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
