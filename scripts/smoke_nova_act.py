import sys
import time
from pathlib import Path
# Ensure project root is on sys.path for direct imports used by LCARS tests/scripts
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import plugins

c,a,loaded = plugins.initialize(headless=True)
print('LOADED PLUGINS:', [p['name'] for p in loaded])
print('API STORAGE KEYS:', list(getattr(a,'storage',{}).keys()))
if 'nova_act' not in a.storage:
    raise SystemExit('nova_act not registered in PluginAPI.storage')
adapter = a.storage['nova_act']
print('ADAPTER:', type(adapter), hasattr(adapter,'connect'))
print('CONNECT-returned', adapter.connect(use_sdk=False))
# Give telemetry thread a moment to publish
time.sleep(0.3)
print('TELEMETRY:', c.kernel.nexus.get_data('nova_act.telemetry'))
print('SMOKE OK')
