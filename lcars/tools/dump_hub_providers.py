"""Dump InitHub providers to a JSON file for inspection."""
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path

from lcars.system import initialization as init

out = Path(__file__).resolve().parents[1] / "providers_map.json"

init.initialize_system(headless=True)
hub = init.get_system_init().get_hub()
providers = hub.list_providers()

data = {
    "count": len(providers),
    "providers": providers,
}

out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"Wrote {out}")
