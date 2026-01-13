"""
Project Manager - manages Geant4 projects (ENX01-ENX09, NCC-00-NCC-02)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProjectInfo:
    """Information about a Geant4 project"""
    name: str
    path: Path
    build_dir: Optional[Path] = None
    executable: Optional[Path] = None
    data_dir: Optional[Path] = None
    description: str = ""
    
    def to_dict(self):
        return {
            "name": self.name,
            "path": str(self.path),
            "build_dir": str(self.build_dir) if self.build_dir else None,
            "executable": str(self.executable) if self.executable else None,
            "data_dir": str(self.data_dir) if self.data_dir else None,
            "description": self.description,
        }


class ProjectManager:
    """Manages discovery and loading of Geant4 projects"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.projects: Dict[str, ProjectInfo] = {}
        self.discover_projects()
    
    def discover_projects(self):
        """Discover all Geant4 projects in predefined directories"""
        search_roots = [
            self.root_path,
            Path(r"C:\Users\Forge\MyProject\Geant4\Enterprise")
        ]
        
        project_patterns = ["ENX*", "NCC-*"]
        
        for root in search_roots:
            if not root.exists(): continue
            logger.info(f"Discovering projects in {root}")
            for pattern in project_patterns:
                for project_dir in root.glob(pattern):
                    if project_dir.is_dir():
                        project = self._analyze_project(project_dir)
                        if project:
                            self.projects[project.name] = project
                            logger.info(f"Found project: {project.name}")
    
    def _analyze_project(self, project_dir: Path) -> Optional[ProjectInfo]:
        """Analyze a project directory"""
        name = project_dir.name
        
        # Check for build directory
        build_dir = None
        if (project_dir / "build").exists():
            build_dir = project_dir / "build"
        elif (project_dir / "Release").exists():
            build_dir = project_dir / "Release"
        
        # Check for data directory
        data_dir = None
        if (project_dir / "data").exists():
            data_dir = project_dir / "data"
        elif (project_dir / "Release").exists():
            data_dir = project_dir / "Release"
        
        # Find executable
        executable = self._find_executable(project_dir, name)
        
        # Get description from README
        description = self._get_description(project_dir)
        
        return ProjectInfo(
            name=name,
            path=project_dir,
            build_dir=build_dir,
            executable=executable,
            data_dir=data_dir,
            description=description,
        )
    
    def _find_executable(self, project_dir: Path, name: str) -> Optional[Path]:
        """Find project executable"""
        # Look for common executable names
        exe_names = [f"{name}.exe", f"{name}.out", name]
        
        search_dirs = [project_dir, project_dir / "Release", project_dir / "build"]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for exe_name in exe_names:
                    exe_path = search_dir / exe_name
                    if exe_path.exists():
                        return exe_path
        
        return None
    
    def _get_description(self, project_dir: Path) -> str:
        """Get project description from README"""
        readme_files = ["README.txt", "README.md", "README"]
        
        for readme_name in readme_files:
            readme_path = project_dir / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline().strip()
                        return first_line[:100]  # First 100 chars
                except:
                    pass
        
        return ""
    
    def get_project(self, name: str) -> Optional[ProjectInfo]:
        """Get project by name"""
        return self.projects.get(name)
    
    def get_all_projects(self) -> List[ProjectInfo]:
        """Get all discovered projects"""
        return list(self.projects.values())
    
    def get_project_names(self) -> List[str]:
        """Get list of project names"""
        return sorted(self.projects.keys())
    
    def export_config(self, output_path: Path):
        """Export project configuration to JSON"""
        config = {
            "projects": {name: proj.to_dict() for name, proj in self.projects.items()},
            "root_path": str(self.root_path),
        }
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Exported config to {output_path}")
    
    def add_project(self, name: str, path: str, description: str = "") -> bool:
        """Add a new project manually"""
        project_path = Path(path)
        if not project_path.exists() or not project_path.is_dir():
            logger.error(f"Invalid project path: {path}")
            return False

        if name in self.projects:
            logger.warning(f"Project with name {name} already exists.")
            return False

        project_info = ProjectInfo(
            name=name,
            path=project_path,
            description=description
        )
        self.projects[name] = project_info
        logger.info(f"Added project: {name}")
        return True

    def remove_project(self, name: str) -> bool:
        """Remove a project by name"""
        if name in self.projects:
            del self.projects[name]
            logger.info(f"Removed project: {name}")
            return True
        else:
            logger.error(f"Project {name} not found.")
            return False
