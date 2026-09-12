#!/usr/bin/env python3
# LCARS OPENGL CONSTRUCTOR - Робочий конструктор інтерфейсів
import sys
import os
import time
import math
from typing import List, Dict, Any, Optional, Tuple

# Додаємо шлях до LCARS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
    from OpenGL.GL import shaders
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("PyOpenGL не встановлено: pip install PyOpenGL PyOpenGL_accelerate")

from lcars.base.component import Surface, Symbol, Structure
from lcars.base.default import RandomButtonColor, ContrastColor

class LCARSOpenGLConstructor:
    """Робочий конструктор LCARS інтерфейсів з реальними OpenGL можливостями"""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.components = []
        
        # OpenGL об'єкти
        self.vao = None
        self.vbo = None
        self.shader_program = None
        self.texture_id = None
        
        # Uniforms
        self.mvp_matrix = None
        self.time_uniform = None
        self.resolution_uniform = None
        
        # Створюємо конструктор
        self.setup_constructor()
        
    def setup_constructor(self):
        """Налаштувати конструктор"""
        print("🔧 Ініціалізуємо LCARS OpenGL Constructor...")
        
        # Створюємо тестові компоненти
        self.create_test_components()
        
        # Налаштовуємо OpenGL
        self.init_opengl()
        
        # Створюємо шейдери
        self.create_shaders()
        
        # Створюємо буфери
        self.create_buffers()
        
        print("✅ LCARS Constructor готовий")
        
    def create_test_components(self):
        """Створити тестові компоненти для конструктора"""
        
        # --- Робоча область ---
        self.work_area = Structure(
            3010, Parent=None,
            Color="#333333",
            X=50, Y=50,
            Width=self.width - 100, Height=self.height - 100
        )
        
        # --- Панель інструментів ---
        self.tool_panel = Structure(
            3001, Parent=None,
            Text="◤ TOOLS",
            Color="#FF9900",
            X=60, Y=70,
            Width=200, Height=40
        )
        
        # --- Елементи для drag & drop ---
        self.elements = []
        element_types = [
            ("BUTTON", "#FFFF00"),
            ("ELBOW", "#FF9900"),
            ("SCANNER", "#00FF00"),
            ("TEXT", "#336699"),
            ("PANEL", "#6699CC")
        ]
        
        for i, (elem_type, color) in enumerate(element_types):
            element = Surface(
                1001, Parent=None,
                Text=f"◤ {elem_type}",
                Color=color,
                X=100 + i * 120, Y=150,
                Width=100, Height=40
            )
            self.elements.append(element)
            
        # --- Робоча область для drag & drop ---
        self.drop_zone = Structure(
            3010, Parent=None,
            Color="#222222",
            X=100, Y=250,
            Width=self.width - 200, Height=200
        )
        
        # --- Статусна панель ---
        self.status_panel = Structure(
            3002, Parent=None,
            Text="CONSTRUCTOR STATUS",
            Color="#FF9900",
            X=self.width - 260, Y=70,
            Width=200, Height=40
        )
        
        # --- Інформаційна панель ---
        self.info_text = Symbol(
            2001, Parent=None,
            Text="Drag elements to workspace",
            Color="#FFFFFF",
            X=100, Y=500,
            Width=400, Height=30
        )
        
        self.components = [
            self.work_area, self.tool_panel, self.drop_zone,
            self.status_panel, self.info_text
        ]
        self.components.extend(self.elements)
        
    def vertex_shader_source(self):
        """Вершинний шейдер"""
        return """
        #version 330 core
        layout (location = 0) in vec2 a_position;
        layout (location = 1) in vec3 a_color;
        layout (location = 2) in vec2 a_texcoord;
        
        uniform mat4 u_mvp;
        uniform float u_time;
        
        out vec2 v_texcoord;
        out vec3 v_color;
        out vec4 v_position;
        
        void main() {
            v_texcoord = a_texcoord;
            v_color = a_color;
            
            // Проста анімація
            vec2 animated_pos = a_position;
            animated_pos.x += sin(u_time * 2.0) * 5.0;
            
            v_position = u_mvp * vec4(animated_pos, 0.0, 1.0);
            gl_Position = v_position;
        }
        """
        
    def fragment_shader_source(self):
        """Фрагментний шейдер"""
        return """
        #version 330 core
        in vec2 v_texcoord;
        in vec3 v_color;
        in vec4 v_position;
        
        out vec4 frag_color;
        
        void main() {
            // Простий ефект edge detection
            vec2 texel_size = 1.0 / vec2(1920.0, 1080.0);
            vec2 offset = vec2(texel_size.x, 0.0);
            
            float edge = sin(v_texcoord.x * 50.0) * 0.1;
            
            vec3 final_color = v_color + edge;
            frag_color = vec4(final_color, 1.0);
        }
        """
        
    def create_shaders(self):
        """Створити шейдери"""
        if not OPENGL_AVAILABLE:
            return
            
        try:
            # Компілюємо шейдери
            vertex_shader = shaders.compileShader(self.vertex_shader_source(), GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(self.fragment_shader_source(), GL_FRAGMENT_SHADER)
            
            # Лінкуємо програму
            self.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
            
            print("✅ Шейдери створено успішно")
            
        except Exception as e:
            print(f"⚠️ Помилка шейдерів: {e}")
            self.shader_program = None
            
    def create_buffers(self):
        """Створити VBO та VAO"""
        if not OPENGL_AVAILABLE or not self.shader_program:
            return
            
        # Генеруємо вершини для всіх компонентів
        vertices = []
        colors = []
        texcoords = []
        
        for comp in self.components:
            comp_vertices = self.generate_component_vertices(comp)
            vertices.extend(comp_vertices)
            
            # Кольори для кожного компонента
            comp_color = self.hex_to_rgb(comp.Color)
            for _ in range(len(comp_vertices) // 2):
                colors.extend(comp_color)
                
            # Текстурні координати
            for _ in range(len(comp_vertices) // 2):
                texcoords.extend([0.0, 0.0])
                
        # Створюємо VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        vertex_data = []
        for i in range(0, len(vertices), 2):
            vertex_data.extend([vertices[i], vertices[i+1]])
            vertex_data.extend([colors[i], colors[i+1]])
            vertex_data.extend([texcoords[i], texcoords[i+1]])
            
        glBufferData(GL_ARRAY_BUFFER, 
                    len(vertex_data) * 4,  # 3 floats for position, 3 for color, 2 for texcoord
                    vertex_data, 
                    GL_STATIC_DRAW)
        
        # Створюємо VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Налаштовуємо атрибути
        # Position (location 0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Color (location 1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        
        # TexCoord (location 2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(2)
        
        # Роз'єднуємо VBO
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        print(f"✅ VBO/VAO створено: {len(vertex_data)//8} вершин")
        
    def generate_component_vertices(self, comp) -> List[float]:
        """Генерувати вершини для компонента"""
        x, y = comp.X, comp.Y
        w, h = comp.Width, comp.Height
        
        if hasattr(comp, 'ElementType'):
            if comp.ElementType == 3001:  # Top-left elbow
                return [
                    x + h/2, y,      # Точка 1
                    x + w, y,        # Точка 2
                    x + w, y + h/2,  # Точка 3
                    x + h/2, y + h/2, # Точка 4
                    x, y + h/2,      # Точка 5
                    x, y              # Точка 6
                ]
            elif comp.ElementType == 3010:  # Bar
                return [
                    x, y,
                    x + w, y,
                    x + w, y + h,
                    x, y + h
                ]
            else:  # Звичайний прямокутник
                return [
                    x, y,
                    x + w, y,
                    x + w, y + h,
                    x, y + h
                ]
        else:  # Surface/Symbol
            return [
                x, y,
                x + w, y,
                x + w, y + h,
                x, y + h
            ]
            
    def hex_to_rgb(self, hex_color):
        """Конвертувати HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return [r, g, b]
        return [1.0, 1.0, 1.0]
        
    def init_opengl(self):
        """Ініціалізація OpenGL"""
        if not OPENGL_AVAILABLE:
            return False
            
        # Налаштування OpenGL
        glClearColor(0.05, 0.05, 0.1, 1.0)  # Темно-синій фон
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        return True
        
    def setup_matrices(self):
        """Налаштувати матриці"""
        # Проєкційна матриця
        projection = [
            [2.0/self.width, 0, 0, 0],
            [0, 2.0/self.height, 0, 0],
            [0, 0, -1, 0],
            [-1, -1, 0, 1]
        ]
        
        # MVP матриця (проста ортографічна проєкція)
        self.mvp_matrix = projection
        
    def render(self):
        """Основний рендеринг"""
        if not OPENGL_AVAILABLE:
            return
            
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Налаштовуємо матриці
        self.setup_matrices()
        
        # Використовуємо шейдери
        if self.shader_program:
            glUseProgram(self.shader_program)
            
            # Встановлюємо uniforms
            mvp_loc = glGetUniformLocation(self.shader_program, "u_mvp")
            time_loc = glGetUniformLocation(self.shader_program, "u_time")
            res_loc = glGetUniformLocation(self.shader_program, "u_resolution")
            
            if mvp_loc != -1:
                glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, self.mvp_matrix)
            if time_loc != -1:
                glUniform1f(time_loc, time.time())
            if res_loc != -1:
                glUniform2f(res_loc, self.width, self.height)
            
            # Рендеримо через VAO
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            
            # Рендеримо всі компоненти
            vertex_count = len(self.components) * 6  # 6 вершин на компонент
            glDrawArrays(GL_TRIANGLES, 0, vertex_count)
            
            # Роз'єднуємо
            glBindVertexArray(0)
            glUseProgram(0)
        else:
            # Fallback до fixed pipeline
            self.render_fixed_pipeline()
            
    def render_fixed_pipeline(self):
        """Fallback рендеринг з fixed pipeline"""
        for comp in self.components:
            self.render_component_fixed(comp)
            
    def render_component_fixed(self, comp):
        """Рендеринг компонента з fixed pipeline"""
        x, y = comp.X, comp.Y
        w, h = comp.Width, comp.Height
        color = self.hex_to_rgb(comp.Color)
        
        glColor3f(*color)
        
        if hasattr(comp, 'ElementType'):
            if comp.ElementType == 3001:  # Elbow
                thickness = min(w, h) // 2
                glBegin(GL_QUADS)
                # Горизонтальна частина
                glVertex2f(x + thickness, y)
                glVertex2f(x + w, y)
                glVertex2f(x + w, y + thickness)
                glVertex2f(x + thickness, y + thickness)
                # Вертикальна частина
                glVertex2f(x, y + thickness)
                glVertex2f(x + thickness, y + thickness)
                glVertex2f(x + thickness, y + h)
                glVertex2f(x, y + h)
                glEnd()
            else:  # Прямокутник
                glBegin(GL_QUADS)
                glVertex2f(x, y)
                glVertex2f(x + w, y)
                glVertex2f(x + w, y + h)
                glVertex2f(x, y + h)
                glEnd()
        else:
            # Звичайний прямокутник
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()
            
        # Текст
        if hasattr(comp, 'Text') and comp.Text:
            self.render_text_fixed(comp.Text, x + w//2, y + h//2, comp.Color)
            
    def render_text_fixed(self, text, x, y, color):
        """Простий рендеринг тексту"""
        glColor3f(*self.hex_to_rgb(ContrastColor(color)))
        glRasterPos2f(x, y)
        
        for char in text.upper():
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            
    def handle_mouse(self, button, state, x, y):
        """Обробка миші"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print(f"🖱️ Клік на ({x}, {y})")
            
            # Перевіряємо чи потрапили на компонент
            for comp in self.elements:
                if (comp.X <= x <= comp.X + comp.Width and 
                    comp.Y <= y <= comp.Y + comp.Height):
                    print(f"   🎯 Вибрано: {comp.Text}")
                    break
                    
    def print_constructor_info(self):
        """Показати інформацію про конструктор"""
        print("\n🔧 LCARS OpenGL Constructor:")
        print("=" * 50)
        print(f"Розмір: {self.width}x{self.height}")
        print(f"Компонентів: {len(self.components)}")
        print(f"Елементів для drag: {len(self.elements)}")
        print("OpenGL можливості:")
        print("   ✅ VBO/VAO буфери")
        print("   ✅ GLSL шейдери")
        print("   ✅ Uniforms")
        print("   ✅ Матриці перетворень")
        print("   ✅ Анімації в шейдерах")
        print("   ✅ Mouse обробка")
        print("=" * 50)

# Глобальні змінні для GLUT
constructor = None

def display():
    """Callback для відображення"""
    if constructor:
        constructor.render()

def reshape(width, height):
    """Callback для зміни розміру"""
    if constructor:
        constructor.width = width
        constructor.height = height
        glViewport(0, 0, width, height)

def mouse(button, state, x, y):
    """Callback для миші"""
    if constructor:
        constructor.handle_mouse(button, state, x, y)

def timer(value):
    """Timer callback"""
    if constructor:
        glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # ~60 FPS

def main():
    """Головна функція"""
    if not OPENGL_AVAILABLE:
        print("❌ OpenGL недоступний!")
        print("💡 Встановіть: pip install PyOpenGL PyOpenGL_accelerate")
        return
        
    # Ініціалізація GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1920, 1080)
    glutCreateWindow(b"LCARS OpenGL Constructor")
    
    # Створюємо конструктор
    global constructor
    constructor = LCARSOpenGLConstructor(1920, 1080)
    
    # Показуємо інформацію
    constructor.print_constructor_info()
    
    # Реєструємо callback функції
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutTimerFunc(16, timer, 0)
    
    print("\n🖥️  LCARS Constructor запущено!")
    print("🎮 Управління:")
    print("   Ліва кнопка миші - вибір елементів")
    print("   ESC - вихід")
    
    # Головний цикл
    glutMainLoop()

if __name__ == "__main__":
    main()
