from __future__ import annotations

# LCARS SOURCE BRIDGE (TITANIUM STANDARD)
# Система синхронізації коду (Round-trip Engineering).
# Дозволяє знайти визначення об'єкта в коді та оновити його параметри в реальному часі.

from lcars.base.type import SystemComponent, Directive
from lcars.system.synapse import SystemSynapse
from lcars.engineering.telemetry import emit_telemetry

class SourceBridge(SystemComponent):
    # Нейронний міст між UI та вихідним кодом.
    # Забезпечує живе середовище розробки без перевантаження системи.
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_bridge()
        return cls._instance

    def _init_bridge(self):
        self.introspection = Directive.Introspection
        self.logic = Directive.Logic
        self.drive = Directive.PathDrive
        self.synapse = SystemSynapse()
        
        emit_telemetry("System", "PROCESS: SOURCE_BRIDGE_ACTIVE. Neural sync established.")

    def get_object_source_info(self, obj: Any) -> Tuple[Optional[str], Optional[int]]:
        # Знаходить файл та рядок, де визначено об'єкт (чероез інтроспекцію)."""

            # Використовуємо канонічну інтроспекцію
            file_path = self.introspection.getsourcefile(obj.__class__)
            lines, start_line = self.introspection.getsourcelines(obj.__class__)
            return file_path, start_line

            emit_telemetry("System", "TASK_WARN: Source mapping failed for object.", "warn")
            return None, None

    def find_variable_name(self, parent: Any, child: Any) -> Optional[str]:
        # Шукає ім'я змінної дитини в атрибутах батька (наприклад, self.btn).
        if not parent or not child: return None
        for attr_name in dir(parent):

                if getattr(parent, attr_name) is child:
                    return attr_name
        return None

    def rewrite_geometry(self, file_path: str, var_name: str, new_geom: list):
        # Хірургічно оновлює setGeometry або fixedSize в .py файлі.
        path = self.drive(file_path)
        if not path.exists(): return False
        
        content = path.read_text(encoding='utf-8')
        
        # Регулярний вираз для пошуку setGeometry (через Directive.Logic)
        pattern = rf"self\.{var_name}\.setGeometry\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)"
        replacement = f"self.{var_name}.setGeometry({new_geom[0]}, {new_geom[1]}, {new_geom[2]}, {new_geom[3]})"
        
        if self.logic.search(pattern, content):
            new_content = self.logic.sub(pattern, replacement, content)
            path.write_text(new_content, encoding='utf-8')
            
            # Сповіщення Нексуса про зміну коду
            self.synapse.emit_pulse("SourceBridge", {
                "event": "SOURCE_UPDATED", 
                "file": path.name, 
                "variable": var_name,
                "type": "GEOMETRY"
            })
            emit_telemetry("System", f"EVENT: Code surgery on {path.name} ({var_name}) complete.")
            return True
        
        emit_telemetry("System", f"TASK_WARN: No setGeometry found for {var_name} in {path.name}", "warn")
        return False

    def update_property(self, file_path: str, var_name: str, prop_name: str, value: Any):
        # Оновлює властивість (колір, текст тощо) у вихідному коді.
        path = self.drive(file_path)
        if not path.exists(): return False
        
        content = path.read_text(encoding='utf-8')
        updated = False

        # 1. Текстові властивості (setText)
        if prop_name == "text":
            pattern = rf"self\.{var_name}\.setText\s*\(\s*['\"].*?['\"]\s*\)"
            replacement = f"self.{var_name}.setText(\"{value}\")"
            if self.logic.search(pattern, content):
                content = self.logic.sub(pattern, replacement, content)
                updated = True

        # 2. Аргументи конструктора (color="#...", etc.)
        if not updated:
            val_str = f"\"{value}\"" if isinstance(value, str) else str(value)
            pattern = rf"(self\.{var_name}\s*=\s*\w+\s*\(.*{prop_name}\s*=\s*)(['\"].*?['\"]|\w+)(.*\))"
            if self.logic.search(pattern, content, self.logic.DOTALL):
                content = self.logic.sub(pattern, rf"\1{val_str}\3", content, flags=self.logic.DOTALL)
                updated = True

        if updated:
            path.write_text(content, encoding='utf-8')
            self.synapse.emit_pulse("SourceBridge", {
                "event": "SOURCE_UPDATED", 
                "file": path.name, 
                "variable": var_name,
                "property": prop_name
            })
            emit_telemetry("System", f"EVENT: Property '{prop_name}' updated in {path.name}.")
            return True

        return False

# Глобальний екземплярSourceBridge
source_bridge = SourceBridge()
get_bridge = lambda: source_bridge
