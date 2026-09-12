#!/usr/bin/env python3
# ЧИСТИЙ LCARS DESKTOP - БЕЗ QT ЗАЛЕЖНОСТЕЙ
import json
from lcars.base.component import Surface, Symbol, Structure
from lcars.base.type import Painter, Brush, Color, Pen, Font

class PureLCARSDesktop:
    def __init__(self):
        self.components = []
        self.width = 1920
        self.height = 1080
        
        # Створюємо LCARS компоненти
        self.setup_components()
        
    def setup_components(self):
        """Створюємо всі компоненти десктопу"""
        
        # --- TOP BAR ---
        # Elbow ліворуч
        self.elbow = Structure(
            3001,  # Top-left elbow
            Parent=None,
            Text="◤ TITANIUM CORE",
            Color="#FFFF00",
            X=10, Y=10,
            Width=240, Height=60
        )
        
        # Status button
        self.status = Surface(
            1001,  # Rect button
            Parent=None,
            Text="CORE INTEGRITY: OPTIMAL",
            Color="#FF9900",
            X=260, Y=20,
            Width=300, Height=30
        )
        
        # Time label
        self.time_label = Symbol(
            2001,  # Text
            Parent=None,
            Text="00:00:00",
            Color="#FF9900",
            X=self.width - 160, Y=20,
            Width=150, Height=30
        )
        
        # --- MAIN AREA ---
        # Left sidebar buttons
        self.sidebar_buttons = []
        apps = [
            ("◤ BRIDGE", "#FFFF00"),
            ("◤ ACCESS", "#FF9900"),
            ("◤ WEATHER", "#00FF00"),
            ("◤ ENGINEERING", "#FF0000"),
            ("◤ DESIGNER", "#FFFF00")
        ]
        
        for i, (text, color) in enumerate(apps):
            btn = Surface(
                1001,  # Rect
                Parent=None,
                Text=text,
                Color=color,
                X=10, Y=100 + i * 45,
                Width=180, Height=40
            )
            self.sidebar_buttons.append(btn)
        
        # Center content area
        self.content_area = Structure(
            3010,  # Bar H
            Parent=None,
            Color="#333333",
            X=200, Y=100,
            Width=self.width - 400, Height=2
        )
        
        # Right diagnostic panel
        self.diag_elbow = Structure(
            3002,  # Top-right elbow
            Parent=None,
            Text="◤ DIAGNOSTICS",
            Color="#FF9900",
            X=self.width - 210, Y=100,
            Width=200, Height=40
        )
        
        # Diagnostic indicators
        self.diag_indicators = []
        for i in range(4):
            indicator = Surface(
                1007,  # Indicator
                Parent=None,
                Text=f"SYS-{i+1}",
                Color="#00FF00",
                X=self.width - 210, Y=150 + i * 35,
                Width=200, Height=30
            )
            self.diag_indicators.append(indicator)
        
        # --- FOOTER ---
        self.footer_elbow = Structure(
            3003,  # Bottom-left elbow
            Parent=None,
            Text="◤ SECTOR 001",
            Color="#FF9900",
            X=10, Y=self.height - 50,
            Width=240, Height=40
        )
        
        # Додаємо всі компоненти
        all_components = [
            self.elbow, self.status, self.time_label,
            self.content_area, self.diag_elbow, self.footer_elbow
        ]
        all_components.extend(self.sidebar_buttons)
        all_components.extend(self.diag_indicators)
        
        self.components = all_components
        
    def render_to_json(self):
        """Рендерити в JSON для подальшої обробки"""
        render_data = {
            "screen": {
                "width": self.width,
                "height": self.height,
                "background": "#000000"
            },
            "components": []
        }
        
        for comp in self.components:
            # Симулюємо рендеринг
            comp.render()
            
            # Отримуємо painter команди
            if hasattr(comp, '_qt_widget') and hasattr(comp._qt_widget, 'painter'):
                commands = comp._qt_widget.painter.getCommands()
                
                comp_data = {
                    "type": comp.__class__.__name__,
                    "x": comp.X,
                    "y": comp.Y,
                    "width": comp.Width,
                    "height": comp.Height,
                    "color": comp.Color,
                    "text": comp.Text if hasattr(comp, 'Text') else "",
                    "commands": commands
                }
                render_data["components"].append(comp_data)
        
        return render_data
    
    def render_to_html(self):
        """Рендерити в HTML/CSS"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LCARS Desktop</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            font-family: 'Courier New', monospace;
            overflow: hidden;
        }}
        .desktop {{
            position: relative;
            width: {self.width}px;
            height: {self.height}px;
            background: #000;
        }}
    """
        
        # Генеруємо CSS для кожного компонента
        for i, comp in enumerate(self.components):
            comp_id = f"comp_{i}"
            html += f"""
        #{comp_id} {{
            position: absolute;
            left: {comp.X}px;
            top: {comp.Y}px;
            width: {comp.Width}px;
            height: {comp.Height}px;
            background: {comp.Color};
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
            font-size: {comp.FontSize if hasattr(comp, 'FontSize') else 14}px;
            text-transform: uppercase;
        }}
            """
        
        html += """
    </style>
</head>
<body>
    <div class="desktop">
"""
        
        # Генеруємо HTML елементи
        for i, comp in enumerate(self.components):
            comp_id = f"comp_{i}"
            text = comp.Text if hasattr(comp, 'Text') and comp.Text else ""
            html += f'        <div id="{comp_id}">{text}</div>\n'
        
        html += """
    </div>
</body>
</html>"""
        
        return html
    
    def save_html(self, filename="lcars_desktop.html"):
        """Зберегти HTML файл"""
        html = self.render_to_html()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"LCARS Desktop збережено як {filename}")
        
    def print_components(self):
        """Друкує інформацію про компоненти"""
        print(f"LCARS Desktop Components ({len(self.components)} total):")
        print("-" * 60)
        for i, comp in enumerate(self.components):
            print(f"{i+1:2d}. {comp.__class__.__name__:10s} | "
                  f"Pos({comp.X:4d},{comp.Y:4d}) | "
                  f"Size({comp.Width:4d}x{comp.Height:3d}) | "
                  f"Color: {comp.Color} | "
                  f"Text: {comp.Text[:20] if hasattr(comp, 'Text') and comp.Text else 'N/A'}")

if __name__ == "__main__":
    # Створюємо чистий LCARS десктоп
    desktop = PureLCARSDesktop()
    
    # Показуємо компоненти
    desktop.print_components()
    
    # Зберігаємо HTML
    desktop.save_html()
    
    # Рендеримо в JSON
    json_data = desktop.render_to_json()
    with open("lcars_desktop.json", "w") as f:
        json.dump(json_data, f, indent=2)
    
    print("\n✅ Чистий LCARS Desktop створено без Qt залежностей!")
    print("📁 Файли збережено:")
    print("   - lcars_desktop.html (відкрийте в браузері)")
    print("   - lcars_desktop.json (дані для рендерингу)")
