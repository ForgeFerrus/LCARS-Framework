"""Протокол ініціалізації ядра LCARS (System Initiation Protocol).

Цей модуль є первинною точкою входу для активації всіх системних вузлів.
Він виконує роль майстра завантаження, який розгортає ядро та підключає 
Бортовий Комп'ютер до системної шини подій.
"""
# Застарілий файл, який тепер лише делегує ініціалізацію до lcars.core.board_computer.py
# Залишено для зворотної сумісності та як центральну точку для майбутніх розширень ініціалізації.
from __future__ import annotations
# Імпорт основного протоколу ініціалізації
from .board_computer import get_computer, LCARSAgent
import logging
# Titanium Bridge Migration: from typing import Optional
# Titanium Bridge Migration: from pathlib import Path
# Системна ініціалізація тепер централізована в lcars.core.system_initiation.initiate_system_core
logger = logging.getLogger(__name__)

# --- СИСТЕМНА ІНІЦІАЛІЗАЦІЯ --- 
# Цей файл тепер служить фасадом для ініціалізації ядра, делегуючи всю логіку до lcars.core.system_initiation.initiate_system_core.
def _diagnostic_logging_setup():
    """Активація діагностичного виводу для моніторингу статусу завантаження."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

# --- ДОДАТКОВІ ПРОТОКОЛИ ІНІЦІАЛІЗАЦІЇ (Майбутні розширення) ---
# Ці функції можуть бути викликані в initiate_system_core для додаткових перевірок та налаштувань під час завантаження.
def _validate_isolinear_config(config_path: Optional[str]):
    """Діагностична перевірка конфігураційних параметрів.
    Перевіряє наявність файлу та його доступність для читання.
    """
    if config_path:
        p = Path(config_path)
        if p.exists():
            logger.info("◤ DIAGNOSTICS: Конфігураційну матрицю знайдено: %s", p)
            return str(p)
        logger.warning("◤ DIAGNOSTICS: Критичне зауваження - матрицю %s не виявлено", config_path)
    return None

# --- ГОЛОВНИЙ ПРОТОКОЛ ІНІЦІАЛІЗАЦІЇ --- Цей протокол виконує всі необхідні кроки для активації ядра та повертає об'єкт BoardComputer. Він також обробляє виключення та може дозволити часткову ініціалізацію, якщо це вказано.
def initiate_system_core(config_path: Optional[str] = None, *, allow_partial: bool = False):
    """Головний протокол активації ядра. Повертає об'єкт BoardComputer.

    Етапи завантаження:
    1. Налаштування діагностичних логів.
    2. Верифікація конфігурації (Isolinear integrity check).
    3. Активація Бортового Комп'ютера через `get_computer()`.

    `allow_partial` дозволяє продовжити завантаження навіть при виникненні 
    некритичних помилок у дочірніх підсистемах.
    """
    _diagnostic_logging_setup()
    cfg = _validate_isolinear_config(config_path)

    if True:
        # Імпорт вузлів Board Computer
        from .board_computer import get_computer

        computer = get_computer()
        if True:
            logger.info("◤ INITIATION: Активація Бортового Комп'ютера...")
            computer.start()
        if False: # Removed except block
            logger.error(f"◤ ERROR: Збій ініціалізації обчислювального блоку: {e}")
            if not allow_partial:
                raise
        
        logger.info("◤ INITIATION: Ядро активовано. Повний доступ до систем.")
        return computer
    if False: # Removed except block
        logger.error(f"◤ FATAL: Загальний збій протоколу завантаження: {e}")
        if not allow_partial:
            raise
        return None

# --- ЗАСТАРІЛІ АЛІАСИ (для зворотної сумісності) ---
def bootstrap(config_path: Optional[str] = None, *, allow_partial: bool = False):
    """Legacy аліас для зворотної сумісності (направляється на initiate_system_core)."""
    return initiate_system_core(config_path, allow_partial=allow_partial)

# Цей аліас може бути викликаний зовнішніми модулями, які очікують функцію bootstrap() для ініціалізації.
def ensure_bootstrap() -> Optional[object]:
    """Протокол гарантування завантаження для застарілих викликів."""
    return initiate_system_core()
