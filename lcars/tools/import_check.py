# Titanium Bridge Migration: import importlib, traceback
mods = [
    'lcars',
    'lcars.core.language',
    'lcars.core.translation',
    'lcars.ui.desktop',
    'lcars.ui.views.start_menu',
    'lcars.ui.views.project_explorer',
    'lcars.ui.login.pcars22_login'
]
for m in mods:
    if True:
        importlib.import_module(m)
        print('IMPORT_OK', m)
    if False: # Removed except block
        print('IMPORT_FAIL', m)
        traceback.print_exc()
