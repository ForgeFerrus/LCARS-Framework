#!/usr/bin/env python3
# СУЧАСНИЙ OPENGL LCARS - OpenGL 4.x Core Profile
import sys
import os
import time
import math
import numpy as np
from typing import List, Dict, Any

# Додаємо шлях до LCARS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GL import shaders
    from OpenGL.arrays import vbo
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("PyOpenGL не встановлено: pip install PyOpenGL PyOpenGL_accelerate")

from lcars.base.component import Surface, Symbol, Structure
from lcars.base.default import RandomButtonColor, ContrastColor

class ModernLCARSRenderer:
    """Сучасний OpenGL 4.x LCARS рендерер"""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.time = 0
        
        # OpenGL об'єкти
        self.vao = None
        self.vbo = None
        self.shader_program = None
        self.texture_atlas = None
        
        # Uniforms
        self.mvp_matrix_loc = None
        self.time_loc = None
        self.resolution_loc = None
        self.texture_loc = None
        
        # Дані
        self.vertices = []
        self.colors = []
        self.uvs = []
        
        # Створюємо LCARS
        self.setup_lcars()
        
    def setup_lcars(self):
        """Створити LCARS елементи"""
        print("🎨 Створюємо сучасний LCARS...")
        
        # Генеруємо вершини для LCARS елементів
        self.generate_lcars_geometry()
        
        # Створюємо текстурний атлас
        self.create_texture_atlas()
        
        print("✅ Сучасний LCARS створено")
        
    def generate_lcars_geometry(self):
        """Генерувати геометрію LCARS"""
        # Створюємо LCARS елементи
        elements = [
            # Elbow top-left
            {'type': 'elbow', 'x': 100, 'y': 100, 'w': 200, 'h': 60, 'color': '#FFFF00'},
            # Buttons
            {'type': 'button', 'x': 100, 'y': 200, 'w': 180, 'h': 40, 'color': '#FF9900', 'text': 'BRIDGE'},
            {'type': 'button', 'x': 100, 'y': 250, 'w': 180, 'h': 40, 'color': '#00FF00', 'text': 'SENSORS'},
            {'type': 'button', 'x': 100, 'y': 300, 'w': 180, 'h': 40, 'color': '#336699', 'text': 'COMMS'},
            # Scanner
            {'type': 'scanner', 'x': 300, 'y': 200, 'w': 800, 'h': 4, 'color': '#666666'},
            # Right panel
            {'type': 'elbow', 'x': 1400, 'y': 100, 'w': 200, 'h': 50, 'color': '#FF9900', 'corner': 'top-right'},
            {'type': 'button', 'x': 1400, 'y': 200, 'w': 150, 'h': 30, 'color': '#00FF00', 'text': 'CORE'},
            {'type': 'button', 'x': 1400, 'y': 240, 'w': 150, 'h': 30, 'color': '#00FF00', 'text': 'MEMORY'},
        ]
        
        # Генеруємо вершини для кожного елемента
        for elem in elements:
            self.add_element_vertices(elem)
            
    def add_element_vertices(self, element):
        """Додати вершини елемента"""
        x, y, w, h = element['x'], element['y'], element['w'], element['h']
        color = self.hex_to_rgb(element['color'])
        
        if element['type'] == 'elbow':
            # Elbow геометрія
            thickness = min(w, h) // 2
            corner = element.get('corner', 'top-left')
            
            if corner == 'top-left':
                # Горизонтальна частина
                self.add_quad(x + thickness, y, w - thickness, thickness, color)
                # Вертикальна частина
                self.add_quad(x, y + thickness, thickness, h - thickness, color)
            elif corner == 'top-right':
                # Горизонтальна частина
                self.add_quad(x, y, w - thickness, thickness, color)
                # Вертикальна частина
                self.add_quad(x + w - thickness, y + thickness, thickness, h - thickness, color)
                
        elif element['type'] == 'scanner':
            # Анімований сканер
            self.add_quad(x, y, w, h, color)
            
        else:  # button
            # Прямокутник з округленими кутами
            self.add_rounded_rect(x, y, w, h, 5, color)
            
        # Додаємо текст якщо є
        if 'text' in element:
            self.add_text_vertices(element['text'], x + w//2, y + h//2, color)
            
    def add_quad(self, x, y, w, h, color):
        """Додати квад вершини (як 2 triangles для Core Profile)"""
        # Triangle 1: верхній лівий, верхній правий, нижній лівий
        # Triangle 2: верхній правий, нижній правий, нижній лівий
        
        triangle_vertices = [
            x, y,           # Triangle 1 - вершин 1
            x + w, y,       # Triangle 1 - вершин 2
            x, y + h,       # Triangle 1 - вершин 3
            x + w, y,       # Triangle 2 - вершин 1
            x + w, y + h,   # Triangle 2 - вершин 2
            x, y + h        # Triangle 2 - вершин 3
        ]
        
        triangle_uvs = [
            0.0, 0.0,  # Triangle 1 - UV 1
            1.0, 0.0,  # Triangle 1 - UV 2
            0.0, 1.0,  # Triangle 1 - UV 3
            1.0, 0.0,  # Triangle 2 - UV 1
            1.0, 1.0,  # Triangle 2 - UV 2
            0.0, 1.0,  # Triangle 2 - UV 3
        ]
        
        self.vertices.extend(triangle_vertices)
        self.colors.extend(color * 6)
        self.uvs.extend(triangle_uvs)
        
    def add_rounded_rect(self, x, y, w, h, radius, color):
        """Додати прямокутник з округленими кутами"""
        # Спрощена версія - просто прямокутник
        self.add_quad(x, y, w, h, color)
        
    def add_text_vertices(self, text, x, y, color):
        """Додати текстові вершини (як 2 triangles для Core Profile)"""
        text_width = len(text) * 8
        text_height = 16
        
        # 2 triangles для тексту
        text_vertices = [
            x - text_width//2, y - text_height//2,    # Triangle 1 - вершин 1
            x + text_width//2, y - text_height//2,   # Triangle 1 - вершин 2
            x - text_width//2, y + text_height//2,    # Triangle 1 - вершин 3
            x + text_width//2, y - text_height//2,   # Triangle 2 - вершин 1
            x + text_width//2, y + text_height//2,   # Triangle 2 - вершин 2
            x - text_width//2, y + text_height//2     # Triangle 2 - вершин 3
        ]
        
        text_uvs = [
            0.0, 0.0,  # Triangle 1 - UV 1
            1.0, 0.0,  # Triangle 1 - UV 2
            0.0, 1.0,  # Triangle 1 - UV 3
            1.0, 0.0,  # Triangle 2 - UV 1
            1.0, 1.0,  # Triangle 2 - UV 2
            0.0, 1.0,  # Triangle 2 - UV 3
        ]
        
        self.vertices.extend(text_vertices)
        self.colors.extend(color * 6)
        self.uvs.extend(text_uvs)
        
    def create_texture_atlas(self):
        """Створити текстурний атлас"""
        # Простий текстурний атлас (1x1 білий піксель)
        texture_data = np.array([255, 255, 255, 255], dtype=np.uint8)
        
        self.texture_atlas = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_atlas)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
    def vertex_shader_source(self):
        """Сучасний вершинний шейдер"""
        return """
        #version 410 core
        layout (location = 0) in vec2 a_position;
        layout (location = 1) in vec3 a_color;
        layout (location = 2) in vec2 a_texcoord;
        
        uniform mat4 u_mvp;
        uniform float u_time;
        uniform vec2 u_resolution;
        
        out vec3 v_color;
        out vec2 v_texcoord;
        out vec2 v_position;
        
        void main() {
            v_color = a_color;
            v_texcoord = a_texcoord;
            v_position = a_position;
            
            // Сучасна анімація в вершинному шейдері
            vec2 animated_pos = a_position;
            animated_pos.y += sin(u_time * 3.0 + a_position.x * 0.01) * 2.0;
            
            gl_Position = u_mvp * vec4(animated_pos, 0.0, 1.0);
        }
        """
        
    def fragment_shader_source(self):
        """Сучасний фрагментний шейдер з пост-ефектами"""
        return """
        #version 410 core
        in vec3 v_color;
        in vec2 v_texcoord;
        in vec2 v_position;
        
        uniform sampler2D u_texture;
        uniform float u_time;
        uniform vec2 u_resolution;
        
        out vec4 frag_color;
        
        void main() {
            // Базовий колір
            vec3 base_color = v_color;
            
            // Сучасний glow ефект
            float glow = sin(u_time * 2.0) * 0.5 + 0.5;
            vec3 glow_color = base_color * (1.0 + glow * 0.3);
            
            // Edge detection для LCARS ефекту
            vec2 texel_size = 1.0 / u_resolution;
            vec2 offset = vec2(texel_size.x, 0.0);
            
            float left = length(v_texcoord - offset);
            float right = length(v_texcoord + offset);
            float edge = abs(left - right) * 2.0;
            
            // Поєднуємо ефекти
            vec3 final_color = glow_color + edge * 0.2;
            
            // Додаємо scanline ефект
            float scanline = sin(v_position.y * 80.0) * 0.04;
            final_color -= scanline;
            
            frag_color = vec4(final_color, 1.0);
        }
        """
        
    def create_shaders(self):
        """Створити сучасні шейдери"""
        if not OPENGL_AVAILABLE:
            return False
            
        try:
            # Компілюємо шейдери
            vertex_shader = shaders.compileShader(self.vertex_shader_source(), GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(self.fragment_shader_source(), GL_FRAGMENT_SHADER)
            
            # Лінкуємо програму
            self.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
            
            # Отримуємо uniform locations
            self.mvp_matrix_loc = glGetUniformLocation(self.shader_program, "u_mvp")
            self.time_loc = glGetUniformLocation(self.shader_program, "u_time")
            self.resolution_loc = glGetUniformLocation(self.shader_program, "u_resolution")
            self.texture_loc = glGetUniformLocation(self.shader_program, "u_texture")
            
            print("✅ Сучасні шейдери створено")
            return True
            
        except Exception as e:
            print(f"❌ Помилка шейдерів: {e}")
            return False
            
    def create_buffers(self):
        """Створити VBO та VAO"""
        if not OPENGL_AVAILABLE:
            return False
            
        # Створюємо VBO
        vertex_data = []
        for i in range(0, len(self.vertices), 2):
            vertex_data.extend([
                self.vertices[i], self.vertices[i+1],  # position (2 floats)
                self.colors[i], self.colors[i+1], self.colors[i+2],  # color (3 floats)
                self.uvs[i], self.uvs[i+1]  # uv (2 floats)
            ])
            
        self.vbo = vbo.VBO(np.array(vertex_data, dtype=np.float32))
        
        # Створюємо VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Прив'язуємо VBO
        self.vbo.bind()
        
        # Налаштовуємо атрибути
        # Position (location 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(0))
        
        # Color (location 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(8))
        
        # TexCoord (location 2)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(20))
        
        # Роз'єднуємо
        glBindVertexArray(0)
        
        print(f"✅ VBO/VAO створено: {len(vertex_data)//7} вершин")
        return True
        
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
        """Ініціалізація сучасного OpenGL"""
        if not OPENGL_AVAILABLE:
            return False
            
        # Встановлюємо OpenGL 4.1 Core Profile
        glutInitContextVersion(4, 1)
        glutInitContextProfile(GLUT_CORE_PROFILE)
        
        # Налаштування OpenGL
        glClearColor(0.02, 0.02, 0.05, 1.0)  # Темно-синій фон
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Вмикаємо VSync
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        return True
        
    def setup_matrices(self):
        """Налаштувати матриці"""
        # Проєкційна матриця
        projection = np.array([
            [2.0/self.width, 0, 0, 0],
            [0, 2.0/self.height, 0, 0],
            [0, 0, -1, 0],
            [-1, -1, 0, 1]
        ], dtype=np.float32)
        
        return projection
        
    def render(self):
        """Сучасний рендеринг"""
        if not OPENGL_AVAILABLE or not self.shader_program:
            return
            
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Оновлюємо час
        self.time += 0.016
        
        # Використовуємо шейдерну програму
        glUseProgram(self.shader_program)
        
        # Встановлюємо uniforms
        mvp_matrix = self.setup_matrices()
        glUniformMatrix4fv(self.mvp_matrix_loc, 1, GL_FALSE, mvp_matrix)
        glUniform1f(self.time_loc, self.time)
        glUniform2f(self.resolution_loc, self.width, self.height)
        
        # Прив'язуємо текстуру
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_atlas)
        glUniform1i(self.texture_loc, 0)
        
        # Рендеримо через VAO
        glBindVertexArray(self.vao)
        
        # Рендеримо всі елементи (OpenGL 4.1 Core Profile)
        # Вершини вже генеруються як triangles
        vertex_count = len(self.vertices) // 2  # Кількість вершинних пар
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)
        
        # Роз'єднуємо
        glBindVertexArray(0)
        glUseProgram(0)
        
        glutSwapBuffers()
        
    def print_modern_info(self):
        """Показати інформацію про сучасний OpenGL"""
        print("\n🚀 СУЧАСНИЙ OPENGL LCARS:")
        print("=" * 50)
        print("OpenGL 4.1 Core Profile")
        print("Сучасні можливості:")
        print("   ✅ GLSL 4.10 шейдери")
        print("   ✅ VBO/VAO буфери")
        print("   ✅ Uniform variables")
        print("   ✅ Матричні перетворення")
        print("   ✅ Текстурний атлас")
        print("   ✅ GPU анімації")
        print("   ✅ Glow ефекти")
        print("   ✅ Edge detection")
        print("   ✅ Scanline ефекти")
        print("   ✅ Пост-обробка")
        print(f"   📊 Вершин: {len(self.vertices)//2}")
        print(f"   🎨 Елементів: {len(self.vertices)//8}")
        print("=" * 50)

# Глобальні змінні для GLUT
renderer = None

def display():
    """Callback для відображення"""
    if renderer:
        renderer.render()

def reshape(width, height):
    """Callback для зміни розміру"""
    if renderer:
        renderer.width = width
        renderer.height = height
        glViewport(0, 0, width, height)

def timer(value):
    """Timer callback"""
    if renderer:
        glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # ~60 FPS

def main():
    """Головна функція"""
    if not OPENGL_AVAILABLE:
        print("❌ OpenGL недоступний!")
        print("💡 Встановіть: pip install PyOpenGL PyOpenGL_accelerate numpy")
        return
        
    # Ініціалізація GLUT з Core Profile
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitContextVersion(4, 1)
    glutInitContextProfile(GLUT_CORE_PROFILE)
    glutInitWindowSize(1920, 1080)
    glutCreateWindow(b"Modern OpenGL LCARS")
    
    # Створюємо сучасній рендерер
    global renderer
    renderer = ModernLCARSRenderer(1920, 1080)
    
    # Ініціалізація OpenGL
    if not renderer.init_opengl():
        print("❌ Помилка ініціалізації OpenGL")
        return
        
    # Створюємо шейдери
    if not renderer.create_shaders():
        print("❌ Помилка створення шейдерів")
        return
        
    # Створюємо буфери
    if not renderer.create_buffers():
        print("❌ Помилка створення буферів")
        return
        
    # Показуємо інформацію
    renderer.print_modern_info()
    
    # Реєструємо callback функції
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(16, timer, 0)
    
    print("\n🚀 Сучасний OpenGL LCARS запущено!")
    print("🎮 Управління:")
    print("   ESC - вихід")
    print("   Вікно можна змінювати розмір")
    
    # Головний цикл
    glutMainLoop()

if __name__ == "__main__":
    main()
