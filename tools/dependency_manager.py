import os
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEPENDENCY_FILE = "dependencies.json"

class DependencyManager:
    def __init__(self):
        self.dependencies = self.load_dependencies()

    def load_dependencies(self):
        if not os.path.exists(DEPENDENCY_FILE):
            return {}
        with open(DEPENDENCY_FILE, "r") as f:
            return json.load(f)

    def save_dependencies(self):
        with open(DEPENDENCY_FILE, "w") as f:
            json.dump(self.dependencies, f, indent=4)

    def register_dependency(self, source, target):
        if source not in self.dependencies:
            self.dependencies[source] = []
        if target not in self.dependencies[source]:
            self.dependencies[source].append(target)
        self.save_dependencies()

    def update_imports(self, old_path, new_path):
        for source, targets in self.dependencies.items():
            if old_path in targets:
                self.dependencies[source] = [
                    new_path if t == old_path else t for t in targets
                ]
                self.save_dependencies()

                # Update imports in the source file
                self.update_file_imports(source, old_path, new_path)

    def update_file_imports(self, file_path, old_path, new_path):
        with open(file_path, "r") as f:
            content = f.read()
        updated_content = content.replace(old_path, new_path)
        with open(file_path, "w") as f:
            f.write(updated_content)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_moved(self, event):
        if not event.is_directory:
            old_path = event.src_path
            new_path = event.dest_path
            self.manager.update_imports(old_path, new_path)

if __name__ == "__main__":
    manager = DependencyManager()
    path = str(Path(__file__).parent.parent)  # Watch the project root
    event_handler = FileChangeHandler(manager)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    print(f"Watching for file changes in {path}...")
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()