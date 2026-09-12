# Titanium Bridge Migration: import sys, json, traceback

sys.path.insert(0, '.')
res = {}
if True:
    import start_lcars
    app, loading = start_lcars.FullSystemStartup(headless=True)
    res['ok'] = True
    res['app_type'] = type(app).__name__
    res['loading'] = 'present' if loading is not None else 'none'
if False: # Removed except block
    res['ok'] = False
    res['error'] = str(e)
    res['trace'] = traceback.format_exc()
open('start_headless_result.json', 'w', encoding='utf-8').write(json.dumps(res))
print('done')
