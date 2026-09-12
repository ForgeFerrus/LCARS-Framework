#!/usr/bin/env python3
# ПРОСТИЙ PADD - Без складних бібліотек
import sys
import os
import time

try:
    import glfw
    GLFW_AVAILABLE = True
except ImportError:
    GLFW_AVAILABLE = False
    print("GLFW не встановлено")

try:
    from OpenGL.GL import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL не встановлено")

class SimplePADD:
    """Простий але ефективний PADD"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.running = True
        self.window = None
        
    def create_borderless_window(self):
        """Створити вікно без рамок"""
        if not GLFW_AVAILABLE:
            return False
            
        try:
            # Ініціалізація GLFW
            if not glfw.init():
                return False
                
            # Налаштування вікна без рамок
            glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
            glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
            glfw.window_hint(glfw.DECORATED, glfw.FALSE)  # Без рамок!
            glfw.window_hint(glfw.FLOATING, glfw.TRUE)   # Поверх інших вікон
            glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.TRUE)
            
            # Створюємо вікно
            self.window = glfw.create_window(
                self.width, self.height,
                "PADD",
                None, None
            )
            
            if not self.window:
                glfw.terminate()
                return False
                
            # Центруємо вікно
            screen_width = glfw.get_video_mode(glfw.get_primary_monitor()).size.width
            screen_height = glfw.get_video_mode(glfw.get_primary_monitor()).size.height
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
            glfw.set_window_pos(self.window, x, y)
            
            # Робимо вікно активним
            glfw.focus_window(self.window)
            
            print("📱 PADD вікно створено без рамок")
            return True
            
        except Exception as e:
            print(f"❌ Помилка вікна: {e}")
            return False
            
    def init_opengl_context(self):
        """Ініціалізувати OpenGL контекст"""
        if not self.window or not OPENGL_AVAILABLE:
            return False
            
        try:
            # Робимо контекст поточним
            glfw.make_context_current(self.window)
            
            # Налаштування OpenGL
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, self.width, self.height, 0, -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Вимикаємо тест глибини
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            print("✅ OpenGL контекст готовий")
            return True
            
        except Exception as e:
            print(f"❌ Помилка OpenGL: {e}")
            return False
            
    def draw_padd_background(self):
        """Малювати фон PADD"""
        # Темно-синій фон
        glColor3f(0.05, 0.05, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # PADD рамка
        glColor3f(1.0, 0.6, 0.0)
        glLineWidth(4.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(10, 10)
        glVertex2f(self.width - 10, 10)
        glVertex2f(self.width - 10, self.height - 10)
        glVertex2f(10, self.height - 10)
        glEnd()
        
    def draw_lcars_interface(self):
        """Малювати LCARS інтерфейс"""
        # Верхній elbow
        self.draw_elbow(50, 50, 200, 60, "top-left", (1.0, 1.0, 0.0))
        
        # Кнопки
        buttons = [
            ("BRIDGE", (1.0, 1.0, 0.0), 50, 150),
            ("SENSORS", (0.0, 1.0, 0.0), 50, 200),
            ("COMMS", (0.2, 0.4, 0.8), 50, 250),
            ("POWER", (1.0, 0.0, 0.0), 50, 300)
        ]
        
        for text, color, x, y in buttons:
            self.draw_button(text, color, x, y)
            
        # Скануюча лінія
        self.draw_scanner(300, 180, 450, 3)
        
        # Правий elbow
        self.draw_elbow(550, 50, 200, 50, "top-right", (1.0, 0.6, 0.0))
        
        # Індикатори
        indicators = ["CORE", "MEM", "NET", "DSP"]
        for i, label in enumerate(indicators):
            self.draw_indicator(label, 550, 120 + i * 35)
            
    def draw_elbow(self, x, y, width, height, corner, color):
        """Малювати LCARS elbow"""
        glColor3f(*color)
        thickness = min(width, height) // 2
        
        glBegin(GL_QUADS)
        
        if corner == "top-left":
            # Горизонтальна частина
            glVertex2f(x + thickness, y)
            glVertex2f(x + width, y)
            glVertex2f(x + width, y + thickness)
            glVertex2f(x + thickness, y + thickness)
            
            # Вертикальна частина
            glVertex2f(x, y + thickness)
            glVertex2f(x + thickness, y + thickness)
            glVertex2f(x + thickness, y + height)
            glVertex2f(x, y + height)
            
        elif corner == "top-right":
            # Горизонтальна частина
            glVertex2f(x, y)
            glVertex2f(x + width - thickness, y)
            glVertex2f(x + width - thickness, y + thickness)
            glVertex2f(x, y + thickness)
            
            # Вертикальна частина
            glVertex2f(x + width - thickness, y + thickness)
            glVertex2f(x + width, y + thickness)
            glVertex2f(x + width, y + height)
            glVertex2f(x + width - thickness, y + height)
            
        glEnd()
        
        # Текст
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2f(x + 10, y + height // 2 + 5)
        text = "◤ PADD"
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            
    def draw_button(self, text, color, x, y):
        """Малювати кнопку"""
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + 180, y)
        glVertex2f(x + 180, y + 35)
        glVertex2f(x, y + 35)
        glEnd()
        
        # Текст
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2f(x + 10, y + 22)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
            
    def draw_scanner(self, x, y, width, height):
        """Малювати скануючу лінію"""
        # Анімована скануюча лінія
        scan_pos = (time.time() * 100) % width
        
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Анімована частина
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + scan_pos, y)
        glVertex2f(x + scan_pos, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
    def draw_indicator(self, label, x, y):
        """Малювати індикатор"""
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + 150, y)
        glVertex2f(x + 150, y + 25)
        glVertex2f(x, y + 25)
        glEnd()
        
        # Текст
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2f(x + 10, y + 17)
        for char in label:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
            
    def render(self):
        """Основний рендеринг"""
        if not self.window:
            return
            
        # Очищуємо екран
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Малюємо PADD
        self.draw_padd_background()
        self.draw_lcars_interface()
        
        # Інформація
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(10, self.height - 20)
        info = f"Simple PADD {self.width}x{self.height} | ESC: Exit"
        for char in info:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
            
        # Обмін буферів
        glfw.swap_buffers(self.window)
        
    def handle_keyboard(self):
        """Обробка клавіатури"""
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            self.running = False
            
    def run(self):
        """Запустити PADD"""
        print("📱 Запускаю Simple PADD...")
        
        if not GLFW_AVAILABLE:
            print("❌ GLFW не доступний")
            return
            
        if not OPENGL_AVAILABLE:
            print("❌ OpenGL не доступний")
            return
            
        # Створюємо вікно
        if not self.create_borderless_window():
            return
            
        # Ініціалізуємо OpenGL
        if not self.init_opengl_context():
            return
            
        print("✅ Simple PADD готовий!")
        print("🎮 ESC - вихід")
        print("📱 Вікно без рамок (справжній PADD)")
        
        # Головний цикл
        while self.running and not glfw.window_should_close(self.window):
            # Обробка подій
            glfw.poll_events()
            
            # Обробка клавіатури
            self.handle_keyboard()
            
            # Рендеринг
            self.render()
            
            # Контроль FPS
            time.sleep(0.016)  # ~60 FPS
            
        # Очищення
        if self.window:
            glfw.destroy_window(self.window)
        glfw.terminate()
        
        print("📱 Simple PADD завершено")

def main():
    """Головна функція"""
    padd = SimplePADD()
    padd.run()

if __name__ == "__main__":
    main()
