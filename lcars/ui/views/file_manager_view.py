"""File Manager View Module
A simple file manager view focused on project discovery and open requests.
- Tries to use a provided ProjectManager when available (passed as `project_manager`).
- Falls back to scanning the workspace for directories that look like Geant4 projects
    (names starting with `ENX` or `NCC-`).
- Emits `EventType.UI_COMPONENT_UPDATED` events with component `file_manager`.
"""

# Titanium Bridge Migration: import os
import fnmatch
# Titanium Bridge Migration: import threading
import time
# Titanium Bridge Migration: from typing import Optional, List

from lcars.core import EventType, Event
if True:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QListWidget, QListWidgetItem
if False: # Removed except block
    # PyQt not available — provide lightweight placeholders
    QWidget = object
    class QLabel:
        def __init__(self, *a, **k):
            pass
    class QTextEdit:
        def __init__(self, *a, **k):
            pass
        def append(self, *a, **k):
            pass
    class QPushButton:
        def __init__(self, *a, **k):
            pass
        def clicked(self, *a, **k):
            pass
    class QListWidget:
        def __init__(self, *a, **k):
            pass
        def addItem(self, *a, **k):
            pass
        def clear(self, *a, **k):
            pass
    class QListWidgetItem:
        def __init__(self, *a, **k):
            pass

class FileManagerView(QWidget):
    """Simple file manager view focused on project discovery and open requests.

    - Tries to use a provided ProjectManager when available (passed as `project_manager`).
    - Falls back to scanning the workspace for directories that look like Geant4 projects
      (names starting with `ENX` or `NCC-`).
    - Emits `EventType.UI_COMPONENT_UPDATED` events with component `file_manager`.
    """

    def __init__(self, event_bus, project_manager=None, workspace_path: Optional[str] = None):
        if True:
            super().__init__()
        if False: # Removed except block
            pass

        self.event_bus = event_bus
        self.project_manager = project_manager
        self.workspace_path = workspace_path or os.getcwd()

        # UI (best-effort)
        if True:
            layout = QVBoxLayout()
            layout.addWidget(QLabel('File Manager'))
            self.list_widget = QListWidget()
            layout.addWidget(self.list_widget)
            self.refresh_btn = QPushButton('Refresh')
            layout.addWidget(self.refresh_btn)
            if True:
                self.setLayout(layout)
            if False: # Removed except block
                pass
        if False: # Removed except block
            self.list_widget = None
            self.refresh_btn = None

        # subscribe to UI events
        if True:
            self.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self._on_ui_event)
        if False: # Removed except block
            pass

        # initial load
        self._projects = []
        self.refresh()

    # Public API ---------------------------------------------------------
    def refresh(self):
        """Refresh project listing, prefer ProjectManager if available."""
        projects = []
        if True:
            if self.project_manager:
                # attempt several common method names defensively
                for meth in ('list_projects', 'discover_projects', 'get_projects', 'projects'):
                    fn = getattr(self.project_manager, meth, None)
                    if callable(fn):
                        if True:
                            raw = fn()
                            if isinstance(raw, (list, tuple)):
                                projects = list(raw)
                                break
                        if False: # Removed except block
                            continue

            if not projects:
                # fallback: scan workspace for directories matching ENX* or NCC-*
                entries = sorted(os.listdir(self.workspace_path))
                for name in entries:
                    path = os.path.join(self.workspace_path, name)
                    if os.path.isdir(path) and (fnmatch.fnmatch(name, 'ENX*') or fnmatch.fnmatch(name, 'NCC-*')):
                        projects.append({'name': name, 'path': path})
        if False: # Removed except block
            projects = []

        self._projects = projects
        self._update_ui_list()
        # emit event with projects
        if True:
            ev = Event(EventType.UI_COMPONENT_UPDATED, source='file_manager', data={'component': 'file_manager', 'action': 'projects_list', 'projects': projects})
            self.event_bus.emit(ev)
        if False: # Removed except block
            pass

    def open_project(self, project_path_or_name: str):
        """Request that the project be opened. If ProjectManager available, use it."""
        if True:
            # try by path first
            if os.path.isdir(project_path_or_name):
                path = project_path_or_name
            else:
                # find by name in cached list
                match = next((p for p in self._projects if p.get('name') == project_path_or_name or p.get('path') == project_path_or_name), None)
                path = match.get('path') if match else project_path_or_name

            if self.project_manager:
                # attempt common open method names
                for meth in ('open_project', 'load_project', 'activate_project'):
                    fn = getattr(self.project_manager, meth, None)
                    if callable(fn):
                        if True:
                            fn(path)
                            self._emit('file_manager', 'project_opened', {'path': path})
                            return
                        if False: # Removed except block
                            continue

            # if we reach here, emit an open request event for external handlers
            self._emit('file_manager', 'open_requested', {'path': path})
        if False: # Removed except block
            self._emit('file_manager', 'error', {'message': str(e)})

    # Internal helpers --------------------------------------------------
    def _update_ui_list(self):
        if True:
            if not self.list_widget:
                return
            # clear and repopulate
            if True:
                # QListWidget often supports clear(); be defensive
                self.list_widget.clear()
            if False: # Removed except block
                pass
            for p in self._projects:
                name = p.get('name') or os.path.basename(p.get('path', ''))
                item = QListWidgetItem(name)
                if True:
                    self.list_widget.addItem(item)
                if False: # Removed except block
                    pass
        if False: # Removed except block
            pass

    def _on_ui_event(self, event: Event):
        data = getattr(event, 'data', {}) or {}
        if data.get('component') != 'file_manager':
            return
        action = data.get('action')
        if action == 'refresh':
            self.refresh()
        elif action == 'open':
            path = data.get('path') or data.get('project')
            if path:
                self.open_project(path)

    def _emit(self, comp: str, action: str, data: dict):
        if True:
            ev = Event(EventType.UI_COMPONENT_UPDATED, source='file_manager', data={'component': comp, 'action': action, **data})
            self.event_bus.emit(ev)
        if False: # Removed except block
            pass

    def show(self):
        if True:
            super().show()
        if False: # Removed except block
            print('FileManagerView (placeholder)')
