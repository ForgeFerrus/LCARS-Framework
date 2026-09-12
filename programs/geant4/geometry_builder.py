"""
LCARS Native Geometry Builder
===========================
Вбудований рушій генерації геометрії для Geant4 (Без використання сторонніх інструментів).
Формує GDML/C++ макроси напряму з інтерфейсу LCARS (Architect).
"""

import math
from typing import Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum

class GeometryType(Enum):
    CYLINDER = "cylinder"
    BOX = "box"
    SPHERE = "sphere"
    TUBE = "tube"
    CONE = "cone"

class MaterialEnum(Enum):
    COBALT_59 = "Cobalt-59"
    LEAD = "Lead"
    TUNGSTEN = "Tungsten"
    COPPER = "Copper"
    ALUMINUM = "Aluminum"
    VACUUM = "Vacuum"

@dataclass
class DetectorNode:
    name: str
    geom_type: GeometryType
    dimensions: Tuple[float, ...]
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    material: MaterialEnum = MaterialEnum.VACUUM

class LCARSGeometryEngine:
    """Генерує фізичну геометрію напряму з матриці LCARS для Geant4."""
    
    def __init__(self):
        self.nodes: List[DetectorNode] = []
        
    def add_node(self, node: DetectorNode):
        self.nodes.append(node)
        
    def export_to_gdml(self) -> str:
        """Власний генератор GDML-структури"""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">']
        
        # 1. Materials
        xml.append('  <materials>')
        for mat in MaterialEnum:
            xml.append(f'    <material name="{mat.value}"/>')
        xml.append('  </materials>')
        
        # 2. Solids
        xml.append('  <solids>')
        for n in self.nodes:
            if n.geom_type == GeometryType.BOX:
                xml.append(f'    <box name="{n.name}_solid" x="{n.dimensions[0]}" y="{n.dimensions[1]}" z="{n.dimensions[2]}"/>')
            elif n.geom_type == GeometryType.CYLINDER:
                xml.append(f'    <tube name="{n.name}_solid" rmin="0" rmax="{n.dimensions[0]}" z="{n.dimensions[1]}" deltaphi="360"/>')
        xml.append('  </solids>')
        
        # 3. Structure
        xml.append('  <structure>')
        for n in self.nodes:
            xml.append(f'    <volume name="{n.name}_log">')
            xml.append(f'      <materialref ref="{n.material.value}"/>')
            xml.append(f'      <solidref ref="{n.name}_solid"/>')
            xml.append(f'    </volume>')
        xml.append('  </structure>')
        
        # 4. Setup
        xml.append('  <setup name="Default" version="1.0">')
        if self.nodes:
            xml.append(f'    <world ref="{self.nodes[0].name}_log"/>')
        xml.append('  </setup>')
        xml.append('</gdml>')
        
        return "\n".join(xml)

    def generate_cpp_macro(self) -> str:
        """Альтернативна генерація як макрос Geant4"""
        macro = []
        for n in self.nodes:
            macro.append(f"/lcars/geom/add {n.geom_type.value} {n.name}")
            macro.append(f"/lcars/geom/material {n.name} {n.material.value}")
            macro.append(f"/lcars/geom/pos {n.name} {n.position[0]} {n.position[1]} {n.position[2]}")
        return "\n".join(macro)

        try:
            # Send command as JSON
            cmd_json = json.dumps(command)
            self.socket.sendall((cmd_json + "\n").encode())

            # Receive response
            response = self.socket.recv(4096).decode()
            return json.loads(response) if response else {"status": "ok"}

        except Exception as e:

            logger.exception("Unhandled exception in %s", __file__)

            raise

            logger.error(f"Command execution failed: {e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    def find_blender_executable() -> Optional[Path]:
        """Find Blender executable in system"""
        # First, respect environment override
        env_path = os.getenv("BLENDER_PATH")
        if env_path:
            p = Path(env_path)
            if p.exists():
                logger.info(f"Found Blender via BLENDER_PATH={env_path}")
                return p

        # Use shutil.which for PATH lookup
        which = shutil.which("blender")
        if which:
            p = Path(which)
            logger.info(f"Found Blender via PATH at {p}")
            return p

        # Fallback to a small list of known locations (non-exhaustive)
        system = platform.system()
        candidates = []
        if system == "Windows":
            candidates = [
                Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
            ]
        elif system == "Darwin":
            candidates = [Path("/Applications/Blender.app/Contents/MacOS/Blender")]
        else:
            candidates = [Path("/usr/bin/blender"), Path("/usr/local/bin/blender")]

        for c in candidates:
            if c.exists():
                logger.info(f"Found Blender at {c}")
                return c

        return None

    @staticmethod
    def _create_blender_startup_script() -> Path:
        """Create Python script for Blender startup"""

        script_content = '''
import bpy
import socket
import json
import threading

PORT = 12345
HOST = "localhost"

class BlenderServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(1)
        print(f"Blender server listening on {HOST}:{PORT}")
    
    def handle_command(self, command):
        """Process command from LCARS"""
        action = command.get("action")
        
        if action == "create_object":
            obj_type = command.get("type", "CUBE")
            name = command.get("name", "Object")
            bpy.ops.mesh.primitive_cube_add(name=name) if obj_type == "CUBE" else None
            return {"status": "ok", "object": name}
        
        elif action == "list_objects":
            objects = [obj.name for obj in bpy.data.objects]
            return {"status": "ok", "objects": objects}
        
        elif action == "delete_object":
            obj_name = command.get("name")
            if obj_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[obj_name])
            return {"status": "ok"}
        
        elif action == "get_scene_info":
            return {
                "status": "ok",
                "version": bpy.app.version_string,
                "objects": len(bpy.data.objects),
                "meshes": len(bpy.data.meshes)
            }
        
        else:
            return {"status": "error", "message": "Unknown action"}
    
    def run(self):
        while True:
            try:
                conn, addr = self.server.accept()
                print(f"Client connected: {addr}")
                
                data = conn.recv(4096).decode()
                if data:
                    command = json.loads(data)
                    response = self.handle_command(command)
                    conn.sendall(json.dumps(response).encode())
                
                conn.close()
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                print(f"Server error: {e}")

server = BlenderServer()
server.run()
'''

        script_path = Path.home() / ".lcars" / "blender_server.py"
        script_path.parent.mkdir(exist_ok=True)

        with open(script_path, "w") as f:
            f.write(script_content)

        return script_path


class BlenderObject:
    """Represents a Blender object"""

    def __init__(
        self,
        name: str,
        obj_type: str = "CUBE",
        connector: Optional[BlenderConnector] = None,
    ):
        self.name = name
        self.obj_type = obj_type
        self.connector = connector
        self.properties = {}

    def create(self) -> bool:
        """Create object in Blender"""
        if not self.connector or not self.connector.is_connected:
            logger.error("Connector not available")
            return False

        response = self.connector.execute_command(
            {"action": "create_object", "type": self.obj_type, "name": self.name}
        )

        return response.get("status") == "ok"

    def delete(self) -> bool:
        """Delete object from Blender"""
        if not self.connector or not self.connector.is_connected:
            return False

        response = self.connector.execute_command(
            {"action": "delete_object", "name": self.name}
        )

        return response.get("status") == "ok"

    def set_property(self, prop_name: str, value: Any):
        """Set object property"""
        self.properties[prop_name] = value


class BlenderSession:
    """Manages Blender session"""

    def __init__(self):
        self.connector = BlenderConnector()
        self.objects: Dict[str, BlenderObject] = {}
        self.is_active = False

    def start(self, headless: bool = False) -> bool:
        """Start Blender session"""
        self.is_active = self.connector.start_blender(headless=headless)
        return self.is_active

    def stop(self):
        """Stop Blender session"""
        self.connector.disconnect()
        self.is_active = False

    def get_scene_info(self) -> Dict[str, Any]:
        """Get current scene information"""
        if not self.is_active:
            return {"status": "error", "message": "Blender not active"}

        return self.connector.execute_command({"action": "get_scene_info"})

    def add_object(
        self, obj_type: str = "CUBE", name: Optional[str] = None
    ) -> Optional[BlenderObject]:
        """Add object to scene"""
        if not self.is_active:
            logger.error("Blender session not active")
            return None

        if name is None:
            name = f"{obj_type}_{len(self.objects) + 1}"

        obj = BlenderObject(name, obj_type, self.connector)
        if obj.create():
            self.objects[name] = obj
            logger.info(f"Created object: {name}")
            return obj

        return None

    def remove_object(self, name: str) -> bool:
        """Remove object from scene"""
        if not self.is_active or name not in self.objects:
            return False

        obj = self.objects[name]
        if obj.delete():
            del self.objects[name]
            logger.info(f"Deleted object: {name}")
            return True

        return False

    def list_objects(self) -> List[str]:
        """List all objects in scene"""
        if not self.is_active:
            return []

        response = self.connector.execute_command({"action": "list_objects"})
        return response.get("objects", [])


class DetectorBuilder:
    """
    Об'єктно-орієнтована побудова детекторів в Blender
    ===================================================

    Приклад:
        builder = DetectorBuilder(connector)
        builder.add_crystal("Co59", MaterialEnum.COBALT_59, radius=2.0, height=2.0)
        builder.add_shield("PbShield", MaterialEnum.LEAD, (5, 5, 5))
        builder.build_ncc02()
        builder.export_to_gdml("output.gdml")
    """

    def __init__(self, connector: Optional[BlenderConnector] = None):
        """
        Args:
            connector: BlenderConnector instance. Створити новий якщо None.
        """
        self.connector = connector
        self.components: List[DetectorObjectDefinition] = []
        self.detector_name = "LCARS_Detector"

    def add_crystal(
        self,
        name: str,
        material: MaterialEnum = MaterialEnum.COBALT_59,
        radius: float = 2.0,
        height: float = 2.0,
        position: Tuple[float, float, float] = (0, 0, 0),
        color: Tuple[float, float, float] = (1.0, 0.6, 0.2),
    ) -> DetectorObjectDefinition:
        """Додати кристалічний детектор (циліндр)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.CYLINDER,
            dimensions=(radius * 2, radius * 2, height),
            position=position,
            material=material,
            color=color,
        )
        self.components.append(obj)
        logger.info(f"Додано crystal: {name}")
        return obj

    def add_shield(
        self,
        name: str,
        material: MaterialEnum = MaterialEnum.LEAD,
        dimensions: Tuple[float, float, float] = (5, 5, 5),
        position: Tuple[float, float, float] = (0, 0, 0),
        color: Tuple[float, float, float] = (0.4, 0.4, 0.4),
    ) -> DetectorObjectDefinition:
        """Додати екран (куб)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.BOX,
            dimensions=dimensions,
            position=position,
            material=material,
            color=color,
        )
        self.components.append(obj)
        logger.info(f"Додано shield: {name}")
        return obj

    def add_collimator(
        self,
        name: str,
        material: MaterialEnum = MaterialEnum.TUNGSTEN,
        inner_radius: float = 0.5,
        outer_radius: float = 2.0,
        height: float = 1.0,
        position: Tuple[float, float, float] = (0, 0, 0),
        color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> DetectorObjectDefinition:
        """Додати колімотор (труба)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.TUBE,
            dimensions=(inner_radius, outer_radius, height),
            position=position,
            material=material,
            color=color,
        )
        self.components.append(obj)
        logger.info(f"Додано collimator: {name}")
        return obj

    def build_ncc02(self) -> List[DetectorObjectDefinition]:
        """
        Побудувати повну геометрію NCC-02 детектора

        Компоненти:
        - Co-59 crystal (центр)
        - Lead shield (зовні)
        - Tungsten collimator (напрямок)
        """
        self.detector_name = "NCC-02_Detector"

        # Crystal
        self.add_crystal(
            "Co59_Crystal",
            MaterialEnum.COBALT_59,
            radius=2.0,
            height=2.0,
            position=(0, 0, 0),
            color=(1.0, 0.8, 0.0),  # Золотистий
        )

        # Shield
        self.add_shield(
            "Lead_Shield",
            MaterialEnum.LEAD,
            dimensions=(5.0, 5.0, 5.0),
            position=(0, 0, 0),
            color=(0.3, 0.3, 0.3),  # Темно-сірий
        )

        # Collimator
        self.add_collimator(
            "Tungsten_Collimator",
            MaterialEnum.TUNGSTEN,
            inner_radius=0.5,
            outer_radius=2.0,
            height=1.0,
            position=(0, 0, 3.0),
            color=(0.9, 0.9, 0.9),  # Світло-сірий
        )

        logger.info(f"NCC-02 детектор побудований ({len(self.components)} компонентів)")
        return self.components

    def export_scene_config(self) -> Dict[str, Any]:
        """Експортувати конфігурацію сцени як dict"""
        return {
            "detector_name": self.detector_name,
            "num_components": len(self.components),
            "components": [
                {
                    "name": obj.name,
                    "geometry_type": obj.geometry_type.value,
                    "dimensions": obj.dimensions,
                    "position": obj.position,
                    "material": obj.material.value,
                    "color": obj.color,
                }
                for obj in self.components
            ],
        }

    def to_json(self, filepath: Path):
        """Зберегти конфігурацію до JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.export_scene_config(), f, indent=2, ensure_ascii=False)
        logger.info(f"Конфігурація збережена: {filepath}")

    def export_to_gdml(self, filepath: Path) -> bool:
        """Експортувати до GDML (Geant4)"""
        # TODO: реалізувати GDML export
        logger.warning("GDML export не реалізований")
        return False

    def export_to_cpp(
        self, filepath: Path, class_name: str = "DetectorConstruction"
    ) -> bool:
        """Експортувати до C++ для Geant4"""
        # TODO: реалізувати C++ export
        logger.warning("C++ export не реалізований")
        return False


# Приклад використання
if __name__ == "__main__":
    # Тест DetectorBuilder
    builder = DetectorBuilder()
    builder.build_ncc02()

    # Вивести конфігурацію
    import pprint

    pprint.pprint(builder.export_scene_config())
