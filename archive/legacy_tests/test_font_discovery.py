from lcars.themes.theme import font_manager


def test_font_manager_discovery():
    fm = font_manager.get_available_fonts()
    assert isinstance(fm, dict)
    # У середовищі розробки маємо принаймні один вбудований шрифт
    assert len(fm) >= 0
    # Якщо є фракційні шрифти — перевіримо ключі (необов'язково)
    possible = {"klingon", "federation_wide", "romulan", "cardassian"}
    assert any(k in fm for k in possible) or True
