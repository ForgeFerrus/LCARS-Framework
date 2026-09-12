#!/usr/bin/env python3
# СУЧАСНИЙ LCARS - Modern OpenGL 4.x з векторною графікою
import sys
import os
import time
import math

try:
    import glfw
    from OpenGL.GL import *
    import numpy as np
    MODERN_OPENGL_AVAILABLE = True
    print("✅ Modern OpenGL доступний")
except ImportError as e:
    MODERN_OPENGL_AVAILABLE = False
    print(f"Install: pip install glfw PyOpenGL numpy - {e}")

# Додаємо шлях до LCARS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lcars.base.component import ContrastColor
from lcars.base.default import Palette, RandomButtonColor, SystemState, ResolvePaletteGroup

class ModernLCARS:
    """Сучасний LCARS з векторною графікою"""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.window = None
        self.running = True
        
        # OpenGL об'єкти
        self.shader_program = None
        self.vao = None
        self.vbo = None
        
        # LCARS палітра
        self.palette = ResolvePaletteGroup("buttons")
        
    def create_window(self):
        """Створити вікно без рамок"""
        if not glfw.init():
            return False
            
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(self.width, self.height, "Modern LCARS", None, None)
        if not self.window:
            glfw.terminate()
            return False
            
        # Центруємо
        screen = glfw.get_video_mode(glfw.get_primary_monitor())
        x = (screen.size.width - self.width) // 2
        y = (screen.size.height - self.height) // 2
        glfw.set_window_pos(self.window, x, y)
        
        glfw.make_context_current(self.window)
        return True
        
    def create_shaders(self):
        """Створити шейдери"""
        vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec2 position;
        layout(location = 1) in vec3 color;
        out vec3 fragColor;
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * vec4(position, 0.0, 1.0);
            fragColor = color;
        }
        """
        
        fragment_shader_source = """
        #version 330 core
        in vec3 fragColor;
        out vec4 outColor;
        
        void main() {
            outColor = vec4(fragColor, 1.0);
        }
        """
        
        try:
            vs = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vs, vertex_shader_source)
            glCompileShader(vs)
            
            fs = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fs, fragment_shader_source)
            glCompileShader(fs)
            
            self.shader_program = glCreateProgram()
            glAttachShader(self.shader_program, vs)
            glAttachShader(self.shader_program, fs)
            glLinkProgram(self.shader_program)
            
            glDeleteShader(vs)
            glDeleteShader(fs)
            
            return True
        except Exception as e:
            print(f"Shader error: {e}")
            return False
            
    def create_buffers(self):
        """Створити VBO/VAO"""
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # Налаштування атрибутів
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        
    def hex_to_rgb(self, hex_color):
        """Конвертувати hex в RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        return [1.0, 1.0, 1.0]
        
    def add_elbow_vertices(self, vertices, x, y, width, height, color):
        """Додати vertices для LCARS elbow"""
        thick = min(width, height) // 2
        r, g, b = self.hex_to_rgb(color)
        
        # Горизонтальна частина
        vertices.extend([
            x + thick, y, r, g, b,
            x + width, y, r, g, b,
            x + width, y + thick, r, g, b,
            x + thick, y + thick, r, g, b
        ])
        
        # Вертикальна частина
        vertices.extend([
            x, y + thick, r, g, b,
            x + thick, y + thick, r, g, b,
            x + thick, y + height, r, g, b,
            x, y + height, r, g, b
        ])
        
        # Дуга (спрощена як трикутники)
        segments = 8
        for i in range(segments):
            angle1 = math.pi/2 + (i * math.pi/2) / segments
            angle2 = math.pi/2 + ((i + 1) * math.pi/2) / segments
            
            x1 = x + thick + thick * math.cos(angle1)
            y1 = y + thick + thick * math.sin(angle1)
            x2 = x + thick + thick * math.cos(angle2)
            y2 = y + thick + thick * math.sin(angle2)
            
            vertices.extend([
                x + thick, y + thick, r, g, b,
                x1, y1, r, g, b,
                x2, y2, r, g, b
            ])
            
    def add_button_vertices(self, vertices, x, y, width, height, color):
        """Додати vertices для кнопки"""
        r, g, b = self.hex_to_rgb(color)
        
        vertices.extend([
            x, y, r, g, b,
            x + width, y, r, g, b,
            x + width, y + height, r, g, b,
            x, y + height, r, g, b
        ])
        
    def add_scanner_vertices(self, vertices, x, y, width, height):
        """Додати vertices для сканера"""
        # Фон сканера
        vertices.extend([
            x, y, 0.4, 0.4, 0.4,
            x + width, y, 0.4, 0.4, 0.4,
            x + width, y + height, 0.4, 0.4, 0.4,
            x, y + height, 0.4, 0.4, 0.4
        ])
        
        # Анімована скануюча лінія
        scan_pos = (time.time() * 100) % width
        vertices.extend([
            x, y, 0.0, 1.0, 0.0,
            x + scan_pos, y, 0.0, 1.0, 0.0,
            x + scan_pos, y + height, 0.0, 1.0, 0.0,
            x, y + height, 0.0, 1.0, 0.0
        ])
        
    def create_lcars_vertices(self):
        """Створити всі vertices для LCARS"""
        vertices = []
        
        # Верхній лівий elbow
        self.add_elbow_vertices(vertices, 50, 50, 200, 60, self.palette[0])
        
        # Кнопки
        buttons = ["BRIDGE", "SENSORS", "COMMS", "POWER"]
        for i, text in enumerate(buttons):
            color = RandomButtonColor()
            self.add_button_vertices(vertices, 50, 150 + i * 50, 180, 35, color)
            
        # Сканер
        self.add_scanner_vertices(vertices, 300, 180, 400, 3)
        
        # Правий elbow
        self.add_elbow_vertices(vertices, 750, 50, 200, 50, self.palette[1])
        
        # Індикатори
        indicators = ["CORE", "MEM", "NET", "DSP"]
        for i, label in enumerate(indicators):
            color = self.palette[i % len(self.palette)]
            self.add_button_vertices(vertices, 750, 120 + i * 35, 150, 25, color)
            
        return vertices
        
    def render(self):
        """Рендеринг"""
        if not self.window:
            return
            
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Створюємо vertices
        vertices = self.create_lcars_vertices()
        
        # Завантажуємо в VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, np.array(vertices, dtype=np.float32), GL_DYNAMIC_DRAW)
        
        # Рендеримо
        glBindVertexArray(self.vao)
        glUseProgram(self.shader_program)
        
        # Налаштування проекції
        projection = np.array([
            2.0/self.width, 0, 0, 0,
            0, -2.0/self.height, 0, 0,
            0, 0, 1, 0,
            -1, 1, 0, 1
        ], dtype=np.float32)
        
        projection_loc = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
        
        # Конвертуємо quads в triangles
        triangle_vertices = []
        for i in range(0, len(vertices), 20):  # 5 floats per vertex, 4 vertices per quad
            # Quad vertices
            v1 = vertices[i:i+5]
            v2 = vertices[i+5:i+10]
            v3 = vertices[i+10:i+15]
            v4 = vertices[i+15:i+20]
            
            # Two triangles
            triangle_vertices.extend(v1 + v2 + v3)  # Triangle 1
            triangle_vertices.extend(v1 + v3 + v4)  # Triangle 2
            
        # Завантажуємо triangles в VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(triangle_vertices) * 4, np.array(triangle_vertices, dtype=np.float32), GL_DYNAMIC_DRAW)
        
        # Малюємо
        glBindVertexArray(self.vao)
        glUseProgram(self.shader_program)
        
        # Налаштування проекції
        projection = np.array([
            2.0/self.width, 0, 0, 0,
            0, -2.0/self.height, 0, 0,
            0, 0, 1, 0,
            -1, 1, 0, 1
        ], dtype=np.float32)
        
        projection_loc = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
        
        # Малюємо triangles
        vertex_count = len(triangle_vertices) // 5
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)
        
        glfw.swap_buffers(self.window)
        
    def run(self):
        """Запустити сучасний LCARS"""
        if not MODERN_OPENGL_AVAILABLE:
            print("❌ Modern OpenGL не доступний")
            return
            
        print("🚀 Сучасний LCARS з векторною графікою")
        print("✅ Modern OpenGL 4.x")
        print("✅ Векторна графіка")
        print("✅ Апаратне прискорення")
        
        if not self.create_window():
            return
            
        if not self.create_shaders():
            return
            
        self.create_buffers()
        
        while self.running and not glfw.window_should_close(self.window):
            glfw.poll_events()
            
            if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                self.running = False
                
            self.render()
            
        glfw.terminate()
        print("📱 Сучасний LCARS завершено")

if __name__ == "__main__":
    lcars = ModernLCARS()
    lcars.run()
