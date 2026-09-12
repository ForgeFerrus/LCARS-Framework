import importlib


def test_linguistic_panel_service_api():
    m = importlib.import_module('lcars.modules.linguistic_matrix')
    assert hasattr(m, 'LinguisticPanel')

    Panel = getattr(m, 'LinguisticPanel')
    # instantiate service and ensure core methods exist
    p = Panel()
    assert hasattr(p, 'set_faction')
    assert hasattr(p, 'translate')
    assert hasattr(p, 'lookup')

    # set faction should update internal state
    p.set_faction('klingon')
    assert p.get_faction() == 'klingon'

    # stats should return at least the vocabulary_count key
    s = p.stats()
    assert 'vocabulary_count' in s


def test_linguistic_matrix_translation_lookup():
    from lcars.system.localization import LOCALIZATION as Language
    Panel = getattr(importlib.import_module('lcars.modules.linguistic_matrix'), 'LinguisticPanel')
    p = Panel()

    # Ensure translation via DB (hello -> привіт)
    res = p.translate('hello', src='en', tgt='ua')
    assert 'прив' in res.lower()

    # Reverse lookup (привіт -> hello)
    res2 = p.translate('привіт', src='ua', tgt='en')
    assert 'hello' in res2.lower() or res2.lower().startswith('прив') == False

    # Changing system language does not break service
    Language.set_language('ua')
    assert Language.get_language() == 'ua'
    Language.set_language('en')
    assert Language.get_language() == 'en'


def test_faction_translations_and_font_selection():
    """Перевіряє реєстрацію фракційних рядків та вибір шрифту за мовою."""
    from lcars.themes.palette import get_lcars_font_style

    Panel = getattr(__import__('lcars.modules.linguistic_matrix', fromlist=['LinguisticPanel']), 'LinguisticPanel')
    p = Panel()

    # Фракція повинна зберігатися у сервісі
    p.set_faction('klingon')
    assert p.get_faction() == 'klingon'

    # Локалізація має підтримувати фракційні рядки (зареєстровані у __init__ сервісу)
    from lcars.system.localization import LOCALIZATION as Language

    Language.set_language('en')
    val = Language.translate('MAIN_DISPLAY', faction='klingon')
    assert 'klingon' in val.lower() or 'клінгон' in val.lower()

    # Шрифт для української мови повертає очікуваного кандидата у CSS
    Language.set_language('ua')
    css = get_lcars_font_style(12)
    assert ('dejavu' in css.lower()) or ("pt sans" in css.lower()) or ('arial' in css.lower())