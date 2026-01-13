"""
Blender Integration Module
===========================
Мост между Python та Blender для 3D моделювання детекторів.

Об'єктно-орієнтована архітектура для керування Blender як частиною LCARS Framework.

Клас:
    - BlenderConnector: Базова комунікація з Blender
    - DetectorBuilder: OOP для побудови геометрії
    - BlenderExporter: Експорт до GDML, C++, тощо
"""

import subprocess
import json
import socket
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import platform
import sys

logger = logging.getLogger(__name__)


class GeometryType(Enum):
    """Типи геометрії"""
    CYLINDER = "cylinder"
    BOX = "box"
    SPHERE = "sphere"
    TUBE = "tube"
    CONE = "cone"


class MaterialEnum(Enum):
    """Матеріали для Blender"""
    COBALT_59 = "Cobalt-59"
    LEAD = "Lead"
    TUNGSTEN = "Tungsten"
    COPPER = "Copper"
    ALUMINUM = "Aluminum"
    VACUUM = "Vacuum"


@dataclass
class DetectorObjectDefinition:
    """Визначення об'єкту для Blender"""
    name: str
    geometry_type: GeometryType
    dimensions: Tuple[float, float, float]
    position: Tuple[float, float, float] = (0, 0, 0)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    material: MaterialEnum = MaterialEnum.LEAD
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)


class BlenderConnector:
    """Connect to Blender instance via socket"""
    
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.socket = None
        self.blender_pid = None
        self.is_connected = False
    
    def start_blender(self, blender_path: Optional[str] = None, headless: bool = False) -> bool:
        """Start Blender instance
        
        Args:
            blender_path: Path to blender executable. Auto-detect if None.
            headless: Run in background without UI
        
        Returns:
            True if Blender started successfully
        """
        
        if blender_path is None:
            blender_path = self.find_blender_executable()
        
        if not blender_path:
            logger.error("Blender not found. Install Blender 3.0+")
            return False
        
        try:
            # Create Python script to run in Blender
            blender_script = self._create_blender_startup_script()
            
            # Start Blender with socket server
            cmd = [
                str(blender_path),
                "-b" if headless else "",  # Headless mode
                "--python", str(blender_script)
            ]
            cmd = [c for c in cmd if c]  # Remove empty strings
            
            logger.info(f"Starting Blender: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
            )
            
            self.blender_pid = process.pid
            logger.info(f"Blender started with PID {self.blender_pid}")
            
            # Wait for socket to be ready
            time.sleep(2)
            return self.connect()
            
        except Exception as e:
            logger.error(f"Failed to start Blender: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to Blender socket server"""
        try:
            import socket as sock_module
            
            self.socket = sock_module.socket(sock_module.AF_INET, sock_module.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        
        except Exception as e:
            logger.warning(f"Could not connect to Blender: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Blender"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.is_connected = False
            logger.info("Disconnected from Blender")
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command in Blender
        
        Args:
            command: Command dictionary with 'action' and params
        
        Returns:
            Response from Blender
        """
        
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Blender"}
        
        try:
            # Send command as JSON
            cmd_json = json.dumps(command)
            self.socket.sendall((cmd_json + "\n").encode())
            
            # Receive response
            response = self.socket.recv(4096).decode()
            return json.loads(response) if response else {"status": "ok"}
        
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def find_blender_executable() -> Optional[Path]:
        """Find Blender executable in system"""
        
        system = platform.system()
        
        # Common Blender installation paths
        paths = {
            "Windows": [
                Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"),
                Path(f"{Path.home()}/AppData/Local/Programs/Blender Foundation/Blender 4.1/blender.exe"),
            ],
            "Darwin": [
                Path("/Applications/Blender.app/Contents/MacOS/Blender"),
                Path("/Applications/Blender 4.1.app/Contents/MacOS/Blender"),
            ],
            "Linux": [
                Path("/usr/bin/blender"),
                Path("/usr/local/bin/blender"),
                Path(f"{Path.home()}/.local/bin/blender"),
            ]
        }
        
        for path in paths.get(system, []):
            if path.exists():
                logger.info(f"Found Blender at {path}")
                return path
        
        # Try to find via PATH
        try:
            result = subprocess.run(["which" if system != "Windows" else "where", "blender"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                path = Path(result.stdout.strip())
                logger.info(f"Found Blender via PATH at {path}")
                return path
        except:
            pass
        
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
                print(f"Server error: {e}")

server = BlenderServer()
server.run()
'''
        
        script_path = Path.home() / ".lcars" / "blender_server.py"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path


class BlenderObject:
    """Represents a Blender object"""
    
    def __init__(self, name: str, obj_type: str = "CUBE", connector: Optional[BlenderConnector] = None):
        self.name = name
        self.obj_type = obj_type
        self.connector = connector
        self.properties = {}
    
    def create(self) -> bool:
        """Create object in Blender"""
        if not self.connector or not self.connector.is_connected:
            logger.error("Connector not available")
            return False
        
        response = self.connector.execute_command({
            "action": "create_object",
            "type": self.obj_type,
            "name": self.name
        })
        
        return response.get("status") == "ok"
    
    def delete(self) -> bool:
        """Delete object from Blender"""
        if not self.connector or not self.connector.is_connected:
            return False
        
        response = self.connector.execute_command({
            "action": "delete_object",
            "name": self.name
        })
        
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
    
    def add_object(self, obj_type: str = "CUBE", name: Optional[str] = None) -> Optional[BlenderObject]:
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
        color: Tuple[float, float, float] = (1.0, 0.6, 0.2)
    ) -> DetectorObjectDefinition:
        """Додати кристалічний детектор (циліндр)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.CYLINDER,
            dimensions=(radius * 2, radius * 2, height),
            position=position,
            material=material,
            color=color
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
        color: Tuple[float, float, float] = (0.4, 0.4, 0.4)
    ) -> DetectorObjectDefinition:
        """Додати екран (куб)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.BOX,
            dimensions=dimensions,
            position=position,
            material=material,
            color=color
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
        color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    ) -> DetectorObjectDefinition:
        """Додати колімотор (труба)"""
        obj = DetectorObjectDefinition(
            name=name,
            geometry_type=GeometryType.TUBE,
            dimensions=(inner_radius, outer_radius, height),
            position=position,
            material=material,
            color=color
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
            color=(1.0, 0.8, 0.0)  # Золотистий
        )
        
        # Shield
        self.add_shield(
            "Lead_Shield",
            MaterialEnum.LEAD,
            dimensions=(5.0, 5.0, 5.0),
            position=(0, 0, 0),
            color=(0.3, 0.3, 0.3)  # Темно-сірий
        )
        
        # Collimator
        self.add_collimator(
            "Tungsten_Collimator",
            MaterialEnum.TUNGSTEN,
            inner_radius=0.5,
            outer_radius=2.0,
            height=1.0,
            position=(0, 0, 3.0),
            color=(0.9, 0.9, 0.9)  # Світло-сірий
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
                    "color": obj.color
                }
                for obj in self.components
            ]
        }
    
    def to_json(self, filepath: Path):
        """Зберегти конфігурацію до JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_scene_config(), f, indent=2, ensure_ascii=False)
        logger.info(f"Конфігурація збережена: {filepath}")
    
    def export_to_gdml(self, filepath: Path) -> bool:
        """Експортувати до GDML (Geant4)"""
        # TODO: реалізувати GDML export
        logger.warning("GDML export не реалізований")
        return False
    
    def export_to_cpp(self, filepath: Path, class_name: str = "DetectorConstruction") -> bool:
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
