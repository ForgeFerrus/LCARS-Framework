"""
wrapper that exposes the shared ProjectManager implementation from the
framework modules.  Keeping a local file makes imports in the geant4
package simpler, but it isn't a separate copy of the logic; all code
is in lcars.modules.project_manager.
"""

from lcars.modules.project_manager import ProjectManager, ProjectInfo


class ProjectManager:
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.projects: Dict[str, ProjectInfo] = {}
        self.cache_file = self.root_path / "projects_cache.json"
        if self.cache_file.exists():
            self.load_cache()
        else:
            self.discover_projects()
            self.save_cache()

    def discover_projects(self):
        search_roots = [
            self.root_path,
            Path(r"C:\Users\Forge\MyProject\Geant4\Enterprise"),
        ]
        project_patterns = ["ENX*", "NCC-*"]
        for root in search_roots:
            if not root.exists():
                continue
            logger.info(f"Discovering projects in {root}")
            for pattern in project_patterns:
                for project_dir in root.glob(pattern):
                    if project_dir.is_dir():
                        project = self._analyze_project(project_dir)
                        if project:
                            self.projects[project.name] = project
                            logger.info(f"Found project: {project.name}")

    def _analyze_project(self, project_dir: Path) -> Optional[ProjectInfo]:
        name = project_dir.name
        build_dir = None
        if (project_dir / "build").exists():
            build_dir = project_dir / "build"
        elif (project_dir / "Release").exists():
            build_dir = project_dir / "Release"
        data_dir = None
        if (project_dir / "data").exists():
            data_dir = project_dir / "data"
        elif (project_dir / "Release").exists():
            data_dir = project_dir / "Release"
        executable = self._find_executable(project_dir, name)
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
        readme_files = ["README.txt", "README.md", "README"]
        for readme_name in readme_files:
            readme_path = project_dir / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                        first_line = f.readline().strip()
                        return first_line[:100]
                except Exception:
                    logger.debug(f"Failed reading README: {readme_path}")
                    pass
        return ""

    def load_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                for name, proj_data in data.get("projects", {}).items():
                    self.projects[name] = ProjectInfo(
                        name=proj_data["name"],
                        path=Path(proj_data["path"]),
                        build_dir=(
                            Path(proj_data["build_dir"]) if proj_data["build_dir"] else None
                        ),
                        executable=(
                            Path(proj_data["executable"]) if proj_data["executable"] else None
                        ),
                        data_dir=(
                            Path(proj_data["data_dir"]) if proj_data["data_dir"] else None
                        ),
                        description=proj_data.get("description", ""),
                    )
            logger.info(f"Loaded {len(self.projects)} projects from cache")
        except Exception as e:
            logger.exception("Unhandled exception while loading cache: %s", e)
            try:
                self.discover_projects()
                self.save_cache()
            except Exception as e2:
                logger.warning(f"Failed to recover cache: {e2}")
            return

    def save_cache(self):
        try:
            config = {
                "projects": {
                    name: proj.to_dict() for name, proj in self.projects.items()
                },
                "root_path": str(self.root_path),
            }
            with open(self.cache_file, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved {len(self.projects)} projects to cache")
        except Exception as e:
            logger.exception("Unhandled exception while saving cache: %s", e)
            logger.warning(f"Failed to save cache: {e}")

    def refresh_cache(self):
        self.projects.clear()
        self.discover_projects()
        self.save_cache()
        logger.info("Project cache refreshed")

    def get_project(self, name: str) -> Optional[ProjectInfo]:
        return self.projects.get(name)

    def get_all_projects(self) -> List[ProjectInfo]:
        return list(self.projects.values())

    def get_project_names(self) -> List[str]:
        return sorted(self.projects.keys())

    def export_config(self, output_path: Path):
        config = {
            "projects": {name: proj.to_dict() for name, proj in self.projects.items()},
            "root_path": str(self.root_path),
        }
        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Exported config to {output_path}")

    def add_project(self, name: str, path: str, description: str = "") -> bool:
        project_path = Path(path)
        if not project_path.exists() or not project_path.is_dir():
            logger.error(f"Invalid project path: {path}")
            return False
        if name in self.projects:
            logger.warning(f"Project with name {name} already exists.")
            return False
        project_info = ProjectInfo(name=name, path=project_path, description=description)
        self.projects[name] = project_info
        logger.info(f"Added project: {name}")
        return True

    def remove_project(self, name: str) -> bool:
        if name in self.projects:
            del self.projects[name]
            logger.info(f"Removed project: {name}")
            return True
        else:
            logger.error(f"Project {name} not found.")
            return False