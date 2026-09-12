"""
Run the Learning GUI (safe runner).

This script prefers the canonical `programs.learning.app.LinguisticApp` if present,
falling back to `programs.learning.English.LinguisticApp`.

It creates a QApplication and attempts to show the main window; any import/runtime
errors are printed to stderr so the caller can diagnose missing dependencies.
"""
import sys
from pathlib import Path


def ensure_project_root_on_path():
    project_root = Path(__file__).resolve().parents[1]
    p = str(project_root)
    if p not in sys.path:
        sys.path.insert(0, p)


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    ensure_project_root_on_path()

    try:
        from PyQt6.QtWidgets import QApplication
    except Exception as exc:  # pragma: no cover - environment dependent
        print("PyQt6 not available or failed to import:", exc, file=sys.stderr)
        return 2

    # Ensure lcars.type aliases are resolved from the registry so that
    # modules which subclass `Widget` or `Chassis.Window` at import-time
    # do not fail when the lazy resolver would normally populate them.
    try:
        from lcars.base.registry import registry as _REG
        import lcars.base.types as _types
    except Exception:
        _REG = None
        _types = None

    try:
        # Try to import PyQt6 layout/widget classes as fallbacks
        from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QLabel, QApplication
    except Exception:
        QHBoxLayout = QVBoxLayout = QGridLayout = QFrame = QLabel = QApplication = None

    try:
        if _types is not None and _REG is not None:
            # Populate common UI aliases if available
            _types.Widget = _types.Widget or _REG.get('Technical.Widget') or _REG.get('UI.Widget')
            if hasattr(_types, 'Chassis') and getattr(_types.Chassis, 'Window', None) is None:
                _types.Chassis.Window = _REG.get('Technical.Window') or _REG.get('UI.Window') or _types.Chassis.Window

            # Fill common aliases that many modules expect at import-time.
            existing = getattr(_types, 'HBoxLayout', None)
            if existing is None or existing is object:
                _types.HBoxLayout = _REG.get('Layout.HBox') or _REG.get('UI.HBox') or QHBoxLayout or object

            existing = getattr(_types, 'VBoxLayout', None)
            if existing is None or existing is object:
                _types.VBoxLayout = _REG.get('Layout.VBox') or _REG.get('UI.VBox') or QVBoxLayout or object

            existing = getattr(_types, 'GridLayout', None)
            if existing is None or existing is object:
                _types.GridLayout = _REG.get('Layout.Grid') or QGridLayout or object

            existing = getattr(_types, 'Frame', None)
            if existing is None or existing is object:
                _types.Frame = _REG.get('UI.Frame') or QFrame or object

            existing = getattr(_types, 'Label', None)
            if existing is None or existing is object:
                _types.Label = _REG.get('UI.Label') or QLabel or object

            existing = getattr(_types, 'Application', None)
            if existing is None or existing is object:
                _types.Application = _REG.get('UI.Application') or QApplication or object
            # Provide minimal Directive.Protocol and related Qt fallbacks so
            # components that reference Directive.Protocol.CursorShape etc.
            # do not fail during import when the registry hasn't provided them.
            try:
                from PyQt6.QtCore import Qt, QTimer
                proto_existing = getattr(_types.Directive, 'Protocol', None)
                if proto_existing is None or proto_existing is object:
                    ProtoNs = type('ProtoNs', (), {})
                    setattr(ProtoNs, 'CursorShape', getattr(Qt, 'CursorShape', None))
                    setattr(ProtoNs, 'Align', getattr(Qt, 'AlignmentFlag', None))
                    _types.Directive.Protocol = ProtoNs

                pf_existing = getattr(_types.Directive, 'Protocol_Frameless', None)
                if pf_existing is None or pf_existing is object:
                    _types.Directive.Protocol_Frameless = getattr(Qt, 'WindowType', None).FramelessWindowHint if hasattr(getattr(Qt, 'WindowType', None), 'FramelessWindowHint') else getattr(Qt, 'WindowType', None)

                t_existing = getattr(_types.Directive, 'Timer', None)
                if t_existing is None or t_existing is object:
                    _types.Directive.Timer = QTimer
            except Exception:
                pass
    except Exception:
        pass

    # Ensure LCARS core is bootstrapped so the UI registry is initialized
    try:
        import lcars.bootstrap as _bootstrap
        _bootstrap.boot_system(headless=False, verbose=False)
    except Exception:
        # Non-fatal: proceed and let imports fail with a clear traceback
        pass

    # Attempt to import the canonical app class from known locations
    LinguisticApp = None
    import traceback
    try:
        try:
            # Older layout may have `programs.learning.app`
            from programs.learning.app import LinguisticApp as _LA
            LinguisticApp = _LA
        except Exception:
            from programs.learning.English import LinguisticApp as _LA
            LinguisticApp = _LA
    except Exception as exc:
        print("Failed to import LinguisticApp:", exc, file=sys.stderr)
        traceback.print_exc()
        return 3

    app = QApplication.instance() or QApplication(argv)

    try:
        window = LinguisticApp()
        # Prefer full-screen if implemented; otherwise show normally
        try:
            window.showFullScreen()
        except Exception:
            window.show()

        return app.exec()
    except Exception as exc:
        print("Error while running GUI:", exc, file=sys.stderr)
        traceback.print_exc()
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
