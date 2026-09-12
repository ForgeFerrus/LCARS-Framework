# Developer Preferences

Project-level conventions recorded by the maintainer:

- Top-level imports: STRICT. Do not wrap package-level imports in broad
  try/except blocks. Missing modules should fail loudly so issues are
  discovered and fixed (no silent fallbacks).
- Single initializer: use `lcars.initialize()` as the single controlled
  bootstrap entrypoint for wiring services, themes and fonts.
- Theme & fonts: `lcars.themes.lcars_palette` helpers are standard API —
  `get_random_button_color`, `get_alert_color`, and `setup_lcars_font` must
  be called from the bootstrap without suppression.

Follow these rules when adding modules or modifying `__init__` files.

- Коментарі українською: Усі нові та змінені файли повинні містити короткі
  закоментовані пояснення українською мовою на початку файлу та біля ключових
  класів/функцій. Це допомагає читабельності та спрощує співпрацю командою.

