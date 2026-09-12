"""
LCARS System Initialization - Core Entry Point
"""
# дайте пояснення для імпорту майбутніх анотацій типів
from __future__ import annotations

import sys
import argparse
import logging
from typing import Optional, Sequence
from pathlib import Path
# Імпорт необхідних класів PyQt6
from PyQt6.QtWidgets import QApplication, QDialog
# Додавання шляху до проекту для коректного імпорту
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Імпорт основного пакету LCARS
import lcars
from lcars.ui.launcher import FactionDialog, DEFAULT_FACTIONS, DEFAULT_ERAS
from lcars.system.loading_screen import LCARSLoadingScreen
from lcars.system.login_screen import LCARSLoginScreen
from lcars.themes.palette import LCARSEra
from plugins import initialize

# --- [SYSTEM BOOT CORE] ---
def boot_full_system(headless: bool = False, use_plugins: bool = True):
    """Головна функція запуску Ядра та Плагінів (використовуючи plugins.initialize)."""
    if not use_plugins:
        from lcars.core.system import Kernel
        return Kernel(headless=headless), None, []
        
    return initialize(headless=headless)

# --- [UI ORCHESTRATION] ---

# Налаштування логування
LOG_FILE = Path(project_root) / "launcher.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
# Отримання логгера для цього модуля
logger = logging.getLogger("lcars.system.initialization")
# Головна функція ініціалізації та запуску системи LCARS
def run_lcars(argv: Optional[Sequence[str]] = None):
    """Точка входу для ініціалізації системи LCARS."""
    try:
        # Аналіз аргументів командного рядка
        argv = list(argv or sys.argv[1:])
        p = argparse.ArgumentParser(prog="lcars-init")
        # ...
    except Exception as e:
        logger.exception("Unhandled exception in %s", __file__)
        raise

        print(f"CRITICAL SYSTEM FAILURE: {e}")
        logger.exception("Failed to initialize LCARS")
        return
    p.add_argument("--headless", action="store_true", help="Run without GUI")
    p.add_argument("--faction", type=str, help="Preselect faction")
    p.add_argument("--era", type=str, help="Preselect era")
    args = p.parse_args(argv)

    if args.headless:
        # Прямий запуск без GUI
        system, _, _ = boot_full_system(headless=True, use_plugins=True)
        system.start()
        logger.info("LCARS started in headless mode")
        return

    app = QApplication.instance() or QApplication(sys.argv)
    QApplication.setStyle('Fusion')

    context = {
        'faction': args.faction,
        'era': args.era,
        'alert_mode': False,
        'loading': None,
        'lock': None,
        'dialog': None,
        'system': None,
        'shell': None
    }

    def _on_loading_finished():
        logger.info("Boot sequence complete. Opening faction/era selection.")
        # Тепер вибір фракції та епохи ПЕРЕД логіном
        context['dialog'] = FactionDialog(DEFAULT_FACTIONS, DEFAULT_ERAS)
        context['dialog'].finished.connect(_on_selection_finished)
        context['dialog'].show()

    def _on_selection_finished(result):
        if result == QDialog.DialogCode.Accepted:
            sel = context['dialog'].selection()
            context['faction'], context['era'], context['alert_mode'] = sel
            logger.info("Selection successful. Era: %s", context['era'])
            
            # Рядок епохи в Enum для палітри
            target_era = LCARSEra.LCARS_25TH
            era_str = context['era'].lower()
            if "22" in era_str: target_era = LCARSEra.COMS_22ND
            elif "23" in era_str: target_era = LCARSEra.PCARS_23RD
            elif "24" in era_str: target_era = LCARSEra.LCARS_24TH
            elif "29" in era_str: target_era = LCARSEra.TCARS_29TH
        
            # If 25th century selected - bypass login protocol
            if "25" in era_str:
                logger.info("25th Century protocol: Bypassing login screen.")
                _start_system()
            else:
                # For other eras - show login screen with appropriate palette
                context['lock'] = LCARSLoginScreen(era=target_era)
                context['lock'].login_successful.connect(_start_system)
                context['lock'].show()
        else:
            sys.exit(0)

    def _start_system():
        # Hide login window if it exists
        if context.get('lock'):
            context['lock'].hide()
            
        faction = context['faction'] or DEFAULT_FACTIONS[0]
        era = context['era'] or DEFAULT_ERAS[0]
        alert_mode = context['alert_mode']

        logger.info("Initializing system: Faction=%s, Era=%s", faction, era)

        # Full initialization of core and plugins
        context['system'], _, _ = boot_full_system(headless=False, use_plugins=True)
        lcars.system(context['system'])
        
        context['system'].config_manager.set('app', 'faction', faction)
        context['system'].config_manager.set('app', 'era', era)
        context['system'].config_manager.set('app', 'alert_mode', bool(alert_mode))
        context['system'].start()

        # Launch Desktop
        logger.info("Launching LCARS Desktop.")
        from desktop import LCARSDesktop
        context['shell'] = LCARSDesktop(era_key=era, faction_key=faction)
        context['shell'].show()
        logger.info("LCARS Desktop online.")

    context['loading'] = LCARSLoadingScreen()
    context['loading'].loading_finished.connect(_on_loading_finished)
    context['loading'].show()

    app.exec()

if __name__ == "__main__":
    run_lcars()
    # System initialization complete
    logger.info("System initialization complete.")
    sys.exit(0)
