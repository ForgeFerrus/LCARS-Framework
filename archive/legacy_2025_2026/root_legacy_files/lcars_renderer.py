#!/usr/bin/env python3
# LCARS PURE RENDERER - Без Qt залежностей
import json
from typing import List, Dict, Any

class LCARenderer:
    def __init__(self):
        self.components = []
        self.screen_width = 1920
        self.screen_height = 1080
        
    def add_component(self, component):
        """Додати LCARS компонент для рендерингу"""
        self.components.append(component)
        
    def render_to_html(self):
        """Рендерити в HTML/CSS для web"""
        html_parts = []
        css_parts = []
        
        # Базовий HTML
        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LCARS Interface</title>
    <style>
        body {
            background: #000;
            margin: 0;
            padding: 20px;
            font-family: 'Courier New', monospace;
            overflow: hidden;
        }
        .lcars-container {
            position: relative;
            width: 100vw;
            height: 100vh;
        }
    """)
        
        # Рендеримо кожен компонент
        for component in self.components:
            if hasattr(component, 'paintEvent'):
                # Симулюємо paintEvent
                component.paintEvent(None)
                
            # Отримуємо команди рендерингу
            if hasattr(component, '_qt_widget') and hasattr(component._qt_widget, 'painter'):
                painter = component._qt_widget.painter
                if hasattr(painter, 'getCommands'):
                    commands = painter.getCommands()
                    
                    # Створюємо CSS для компонента
                    comp_id = f"comp_{id(component)}"
                    css = self._commands_to_css(commands, component)
                    css_parts.append(css)
                    
                    # Створюємо HTML елемент
                    html = f'<div id="{comp_id}" class="lcars-component"></div>'
                    html_parts.append(html)
        
        html_parts.append("    </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        html_parts.append('<div class="lcars-container">')
        
        # Додаємо всі компоненти
        for component in self.components:
            comp_id = f"comp_{id(component)}"
            html_parts.append(f'<div id="{comp_id}"></div>')
            
            # Додаємо текст якщо є
            if hasattr(component, 'Text') and component.Text:
                html_parts.append(f'<div class="lcars-text">{component.Text.upper()}</div>')
        
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _commands_to_css(self, commands: List[Dict], component) -> str:
        """Конвертувати команди рендерингу в CSS"""
        css = f"#comp_{id(component)} {{\n"
        
        for cmd in commands:
            if cmd['type'] == 'rect':
                css += f"  position: absolute;\n"
                css += f"  left: {cmd['x']}px;\n"
                css += f"  top: {cmd['y']}px;\n"
                css += f"  width: {cmd['w']}px;\n"
                css += f"  height: {cmd['h']}px;\n"
                
                if cmd['brush'] and hasattr(cmd['brush'], 'Color'):
                    css += f"  background-color: {cmd['brush'].Color};\n"
                
                if cmd['opacity'] != 1.0:
                    css += f"  opacity: {cmd['opacity']};\n"
                    
            elif cmd['type'] == 'text':
                css += f"  color: {cmd['pen'].Color if cmd['pen'] else '#FFF'};\n"
                css += f"  font-size: {cmd['font'].Size if cmd['font'] else 14}px;\n"
                css += f"  text-align: center;\n"
                css += f"  display: flex;\n"
                css += f"  align-items: center;\n"
                css += f"  justify-content: center;\n"
        
        css += "}\n"
        return css

def test_lcars_renderer():
    """Тестуємо LCARS рендерер"""
    from lcars.base.component import Surface, Symbol, Structure
    
    renderer = LCARenderer()
    
    # Створюємо тестові компоненти
    elbow = Structure(3001, Text="◤ TITANIUM CORE", Color="#FFFF00", Width=240, Height=60)
    button = Surface(1001, Text="CORE INTEGRITY: OPTIMAL", Color="#FF9900", Width=200, Height=30)
    time_label = Symbol(2001, Text="00:00:00", Color="#FF9900", Width=150, Height=30)
    
    # Додаємо компоненти
    renderer.add_component(elbow)
    renderer.add_component(button)
    renderer.add_component(time_label)
    
    # Рендеримо в HTML
    html = renderer.render_to_html()
    
    # Зберігаємо
    with open("lcars_desktop.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("LCARS Desktop збережено як lcars_desktop.html")
    print("Відкрийте в браузері для перегляду")

if __name__ == "__main__":
    test_lcars_renderer()
