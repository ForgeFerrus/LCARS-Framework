import sys, importlib, traceback
sys.path.insert(0, '.')
mods=['lcars.base.components','lcars.base.defaults','lcars.base.types','lcars.base.interface']
for m in mods:
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception:
        print('ERR', m)
        traceback.print_exc()
