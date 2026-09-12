#!/usr/bin/env python3
"""Headless AccessMenu runner — non-invasive, does not import lcars UI or themes.
Prints a minimal menu summary and accepts simple commands to 'dismiss' or 'quit'.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG = os.path.join(ROOT, 'config', 'config.json')

# Minimal defaults (no theme DB)
DEFAULT_THEME = { 'palette': ['#FFCC00', '#33CCFF', '#CC66FF'], 'accent': '#FFCC00' }
DEFAULT_PAGES = ['APPS', 'ENG', 'SYS', 'PWR']


def load_config():
    try:
        with open(CONFIG, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            ui = cfg.get('ui', {})
            era = ui.get('default_era', '25th')
            faction = ui.get('default_faction')
            return era, faction
    except Exception:
        return '25th', None


if __name__ == '__main__':
    era, faction = load_config()
    theme = DEFAULT_THEME

    print('Headless AccessMenu (safe runner)')
    print(' Era:', era)
    print(' Faction:', faction)
    print(' Palette:', theme.get('palette'))
    print(' Accent:', theme.get('accent'))
    print(' Pages:', DEFAULT_PAGES)
    print('\nCommands:')
    print(" - dismiss  : simulate dismissing the menu")
    print(" - quit     : exit")

    try:
        while True:
            cmd = input('> ').strip().lower()
            if cmd in ('dismiss', 'hide', 'close'):
                print('Menu dismissed (headless).')
            elif cmd in ('quit', 'q', 'exit'):
                print('Exiting.')
                break
            elif cmd == 'status':
                print('Menu visible: no GUI (headless mode)')
            elif cmd == 'help' or cmd == '?':
                print('Commands: dismiss, quit, status, help')
            else:
                if cmd:
                    print("Unknown command. Type 'help'.")
    except (EOFError, KeyboardInterrupt):
        print('\nExiting.')
    sys.exit(0)
