Place faction or language font files here (TTF/OTF).

Naming recommendations (the Settings UI will look for these keys):
- klingon.ttf           → maps to faction key `klingon`
- romulan.ttf           → maps to faction key `romulan`
- cardassian.ttf        → maps to faction key `cardassian`
- starfleet_24th.ttf    → maps to `starfleet_24th`
- starfleet_25th.ttf    → maps to `starfleet_25th`

Also supported: language-specific fonts such as `ua.ttf` or `deja_vu_sans.ttf`.

How to add:
1. Copy your .ttf/.otf files into this folder.
2. Open Settings → FACTION FONTS → Refresh Fonts and select/assign.

Notes:
- Do NOT add proprietary/copyrighted fonts to the repository without a proper license.
- If you provide font files here, the app will register them at runtime and `get_lcars_font_style()` will prefer them.

Provided font keys (add .ttf/.otf with these names to enable selection):
- Federation_Wide -> `starfleet_24th.ttf` (alias: `Federation_Wide`)
- Cardassian -> `cardassian.ttf` (alias: `ST-Cardassian`)
- Klingon -> `klingon.ttf` (aliases: `kl`, `klingon_rihannsu`)
- Rihannsu / Romulan -> `romulan.ttf` (aliases: `Romulan Regular`, `Romulus`)

Example filenames to place here (exact names optional, manager matches stems):
- `starfleet_24th.ttf`, `cardassian.ttf`, `klingon.ttf`, `romulan.ttf`

After copying files: open Settings → FACTION FONTS → Refresh Fonts → Assign.
