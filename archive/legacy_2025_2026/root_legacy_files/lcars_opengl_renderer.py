#!/usr/bin/env python3
# LCARS OPENGL RENDERER - Базова графіка без Qt
import sys
import math
from typing import List, Tuple, Dict, Any

try:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("PyOpenGL не встановлено: pip install PyOpenGL PyOpenGL_accelerate")

class LCARSOpenGLRenderer:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.components = []
        self.font_base = None
        
        # LCARS кольори
        self.colors = {
            'black': (0.0, 0.0, 0.0),
            'yellow': (1.0, 1.0, 0.0),
            'orange': (1.0, 0.6, 0.0),
            'red': (1.0, 0.0, 0.0),
            'green': (0.0, 1.0, 0.0),
            'blue': (0.0, 0.6, 1.0),
            'white': (1.0, 1.0, 1.0),
            'gray': (0.3, 0.3, 0.3)
        }
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def add_component(self, component):
        self.components.append(component)
        
    def init_gl(self):
        if not OPENGL_AVAILABLE:
            return False

        glClearColor(0.0, 0.0, 0.0, 1.0) 
        # Проєкція
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Налаштування
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        return True
        
    def draw_rect(self, x, y, width, height, color, filled=True):
        r, g, b = self.hex_to_rgb(color) if isinstance(color, str) else color
        
        if filled:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_LOOP)
            
        glColor3f(r, g, b)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
    def draw_elbow(self, x, y, width, height, color, corner="top-left"):
        r, g, b = self.hex_to_rgb(color) if isinstance(color, str) else color
        thickness = min(width, height) // 2
        
        glColor3f(r, g, b)
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
        
    def draw_text(self, x, y, text, color="white", size=14):
        if not OPENGL_AVAILABLE:
            return
            
        r, g, b = self.hex_to_rgb(color) if isinstance(color, str) else color
        glColor3f(r, g, b)
        
        # Масштабування тексту
        glPushMatrix()
        glTranslatef(x, y + size, 0)
        glScalef(0.1, 0.1, 1.0)
        
        # Відображення тексту
        for char in text.upper():
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
            
        glPopMatrix()
        
    def render(self):
        if not OPENGL_AVAILABLE:
            return
            
        glClear(GL_COLOR_BUFFER_BIT)
        
        for comp in self.components:
            if hasattr(comp, 'render_gl'):
                comp.render_gl(self)
            elif hasattr(comp, 'render'):
                # Стара сумісність
                comp.render()
                self.render_component_legacy(comp)
                
    def render_component_legacy(self, comp):
        if hasattr(comp, 'ElementType'):
            if comp.ElementType >= 3000:  # Structure
                self.draw_structure(comp)
            elif comp.ElementType >= 2000:  # Symbol/Text
                self.draw_symbol(comp)
            elif comp.ElementType >= 1000:  # Surface/Button
                self.draw_surface(comp)
                
    def draw_surface(self, comp):
        x = getattr(comp, 'X', 0)
        y = getattr(comp, 'Y', 0)
        w = getattr(comp, 'Width', 100)
        h = getattr(comp, 'Height', 30)
        color = getattr(comp, 'Color', '#FFFF00')
        text = getattr(comp, 'Text', '')
        
        # Фон
        self.draw_rect(x, y, w, h, color)
        
        # Текст
        if text:
            self.draw_text(x + 10, y + h//2 - 7, text, 'black', 14)
            
    def draw_symbol(self, comp):
        x = getattr(comp, 'X', 0)
        y = getattr(comp, 'Y', 0)
        w = getattr(comp, 'Width', 100)
        h = getattr(comp, 'Height', 30)
        color = getattr(comp, 'Color', '#FFFFFF')
        text = getattr(comp, 'Text', '')
        
        if text:
            self.draw_text(x, y + h//2, text, color, 14)
            
    def draw_structure(self, comp):
        x = getattr(comp, 'X', 0)
        y = getattr(comp, 'Y', 0)
        w = getattr(comp, 'Width', 100)
        h = getattr(comp, 'Height', 30)
        color = getattr(comp, 'Color', '#FF9900')
        text = getattr(comp, 'Text', '')
        
        # Типи структур
        if hasattr(comp, 'ElementType'):
            if comp.ElementType == 3001:  # Top-left elbow
                self.draw_elbow(x, y, w, h, color, "top-left")
            elif comp.ElementType == 3002:  # Top-right elbow
                self.draw_elbow(x, y, w, h, color, "top-right")
            elif comp.ElementType == 3010:  # Horizontal bar
                self.draw_rect(x, y, w, 4, color)  # Тонка лінія
            elif comp.ElementType == 3011:  # Vertical bar
                self.draw_rect(x, y, 4, h, color)  # Тонка лінія
            else:  # Звичайний прямокутник
                self.draw_rect(x, y, w, h, color)
                
        # Текст
        if text:
            self.draw_text(x + 10, y + h//2 - 7, text, 'black', 14)

class LCARSPadd:
    def __init__(self, renderer):
        self.renderer = renderer
        self.width = 800  # Адаптивний розмір
        self.height = 600
        self.components = []
        
    def add_component(self, component):
        self.components.append(component)
        self.renderer.add_component(component)
        
    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.renderer.width = width
        self.renderer.height = height
        
    def render(self):
        # Чорний фон
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Рамка PADD (опціонально)
        self.renderer.draw_rect(0, 0, self.width, self.height, '#111111', False)
        
        # Рендеримо компоненти
        self.renderer.render()

# Тестуємо OpenGL LCARS рендерер
def test_opengl_lcars():
    if not OPENGL_AVAILABLE:
        print("OpenGL недоступний!")
        return
        
    # Ініціалізація GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1920, 1080)
    glutCreateWindow(b"LCARS OpenGL Interface")
    
    # Створюємо рендерер
    renderer = LCARSOpenGLRenderer(1920, 1080)
    renderer.init_gl()
    
    # Створюємо PADD
    padd = LCARSPadd(renderer)
    
    # Додаємо тестові компоненти
    from lcars.base.component import Surface, Symbol, Structure
    
    # Elbow
    elbow = Structure(3001, Text="◤ TITANIUM CORE", Color="#FFFF00", 
                     X=10, Y=10, Width=240, Height=60)
    
    # Кнопка
    button = Surface(1001, Text="CORE INTEGRITY: OPTIMAL", Color="#FF9900",
                    X=260, Y=20, Width=300, Height=30)
    
    # Текст
    time_label = Symbol(2001, Text="00:00:00", Color="#FF9900",
                       X=1600, Y=20, Width=150, Height=30)
    
    # Додаємо до PADD
    padd.add_component(elbow)
    padd.add_component(button)
    padd.add_component(time_label)
    
    # Callback функції
    def display():
        padd.render()
        glutSwapBuffers()
        
    def reshape(width, height):
        padd.set_size(width, height)
        glViewport(0, 0, width, height)
        glutPostRedisplay()
    
    # Реєструємо callback
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    
    print("LCARS OpenGL Interface запущено!")
    print("ESC - вихід")
    
    # Головний цикл
    glutMainLoop()

if __name__ == "__main__":
    test_opengl_lcars()
