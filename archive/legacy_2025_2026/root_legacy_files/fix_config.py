import json, pathlib
cfg = {
  "era": "22nd",
  "ui": {
    "default_faction": "Federation",
    "default_era": "22nd",
    "hotkeys": {
      "toggle_lock": "Ctrl+L",
      "open_console": "Ctrl+`",
      "launch_engineering": "Ctrl+E"
    },
    "colors": {
      "alert_normal": "#FF9900",
      "alert_yellow": "#FFCC33",
      "alert_red": "#CC0000"
    }
  }
}
path = pathlib.Path('config/config.json')
path.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
print('config rewritten')
