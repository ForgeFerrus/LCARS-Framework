import os, sys, traceback
# Use offscreen platform to avoid opening real windows
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt6.QtWidgets import QApplication
    from desktop import LCARSDesktop
    print('PYQT_OK')
    app = QApplication(sys.argv)
    d = LCARSDesktop()
    # Use a non-fullscreen setup to avoid system-specific behavior
    d.setup_desktop('Federation', '25th')

    info = {
        'has_sidebar': hasattr(d, 'sidebar_frame') and d.sidebar_frame is not None,
        'has_viewport': hasattr(d, 'viewport') and d.viewport is not None,
        'stack_count': d.stack.count() if hasattr(d, 'stack') else None,
        'views': []
    }
    if hasattr(d, 'stack'):
        for i in range(d.stack.count()):
            w = d.stack.widget(i)
            info['views'].append(type(w).__name__)

    # Try toggling sidebar and switching view
    try:
        d.toggle_sidebar()
        d.show_console()
    except Exception as e:
        info['runtime_ops_error'] = str(e)

    print('DESKTOP_SUMMARY:', info)
    # Clean up
    d.close()
    app.quit()
    sys.exit(0)
except Exception:
    traceback.print_exc()
    sys.exit(2)
