# LCARS Interface Palettes & Button Styles

This document summarizes the color palettes and button styles for all major LCARS interfaces in the framework. Use this as a reference for UI consistency, theme extension, and new interface development.

---

## 1. Romulan Interface
- **Palette:**
  - background: `#0A1A1A`
  - text: `#00FF99`
  - primary: `#006666`
  - secondary: `#008B8B`
  - tertiary: `#20B2AA`
  - accent1: `#32CD32` (green)
  - accent2: `#40E0D0` (turquoise)
  - accent3: `#48D1CC` (light turquoise)
  - accent4: `#FFB6C1` (pink)
  - accent5: `#FFD700` (yellow)
  - accent6: `#217AFF` (blue)
  - accent7: `#B2DF28` (lime)
  - accent8: `#888888` (gray)
  - accent9: `#FFFFFF` (white)
  - warning: `#FF0000`
  - success: `#00FF7F`
  - alert: `#FFD700`
  - cloak: `#1E90FF`
  - strategic: `#483D8B`
- **Button Style:**
  - Shape: Trapezoidal (custom paint)
  - Flat color (no gradients if FLAT_MODE)
  - Border: accent1 (green)
  - Text: text (bright green)

---

## 2. Klingon Interface
- **Palette:**
  - background: `#1A0000`
  - text: `#FFCCCC`
  - primary: `#8B0000`
  - secondary: `#A00000`
  - tertiary: `#B22222`
  - accent1: `#FF4500` (orange-red)
  - accent2: `#FFD700` (gold)
  - warning: `#FF0000`
  - success: `#00FF00`
  - alert: `#FFD700`
- **Button Style:**
  - Shape: Rectangular, bold
  - Flat or gradient (configurable)
  - Border: accent1 (orange-red)
  - Text: text (red or gold)

---

## 3. 22nd Century (NX-01)
- **Palette:**
  - background: `#000000`
  - panel: `#222222`
  - border: `#FFFFFF`
  - text: `#FFFFFF`
  - text_dim: `#888888`
  - primary: `#FFFF00` (yellow)
  - secondary: `#00BFFF` (blue)
  - tertiary: `#444444`
  - field_bg: `#FFAE00`
  - field_fg: `#000000`
  - button_bg: `#217AFF`
  - button_fg: `#FFFFFF`
  - button_alt_bg: `#FFFF00`
  - button_alt_fg: `#000000`
  - inactive: `#888888`
  - active: `#00A100FF`
  - alert: `#FF0000`
  - warning: `#FFA500`
  - ok: `#00FF95`
  - epoch: `#05C2FF`
  - convert: `#038336`
  - switch: `#00C4B3`
  - set: `#888888`
- **Button Style:**
  - Shape: Rectangular, slightly rounded
  - Flat color
  - Border: white
  - Text: white or black

---

## 4. 23rd Century (Constitution/Excelsior)
- **Palette:**
  - background: #000000
  - primary: #CD853F (Excelsior: #37A6D1)
  - secondary: #2F3749
  - tertiary: #3EDB8E
  - text: #FFD700 (Excelsior: #B8F6FF)
  - accent1: #6D748C
  - accent2: #3EDB8E
  - success: #3EDB8E
  - warning: #FF6753
- **Button Style:**
  - Shape: Rounded rectangle
  - Flat color
  - Border: secondary
  - Text: primary or background

---

## 5. 24th Century (TNG/DS9/VOY)
- **Palette:**
  - background: #000000
  - text: #99CCFF
  - primary: #FF9900
  - secondary: #3366CC
  - tertiary: #4477DD
  - accent1: #FFCC66
  - accent2: #66CCFF
  - warning: #FF4444
  - success: #00CC66
  - temporal: #AA00FF
  - accent: #FF9900
- **Button Style:**
  - Shape: Rounded rectangle
  - Flat color
  - Border: none
  - Text: black or background

---

## 6. 25th Century (PIC/SNW)
- **Palette:**
  - background: #000000
  - text: #FFFFFF
  - orange1: #FF977B
  - orange2: #FF6753
  - primary: #FF6753
  - secondary: #1C3C55
  - blue1: #334466
  - blue2: #3366CC
  - blue3: #66CCFF
  - warning: #FF0000
  - success: #37A6D1
- **Button Style:**
  - Shape: Rounded rectangle
  - Flat color (orange1/orange2)
  - Border: none or blue2
  - Text: background

---

## 7. 29th Century (TCARS)
- **Palette:**
  - background: #000B14
  - primary: #00F0FF
  - secondary: #FF00FF
  - accent: #80FF00
  - warning: #FF3300
  - text: #FFFFFF
  - temporal: #FF00FF
- **Button Style:**
  - Shape: Rounded rectangle
  - Flat color (primary, accent)
  - Border: primary
  - Text: primary or secondary

---

## 8. Adding New Themes

To add a new theme to the LCARS framework, follow these steps:

1. **Define the Palette:**
   - Open `lcars/ui/theme.py`.
   - Add a new class for your theme, inheriting from `Theme`.
   - Define the color attributes (e.g., `primary`, `secondary`, `accent`, etc.).

   ```python
   class MyNewTheme(Theme):
       def __init__(self):
           super().__init__()
           self.primary_color = "#123456"
           self.secondary_color = "#654321"
           self.accent_color = "#abcdef"
           # Define other colors as needed
   ```

2. **Register the Theme:**
   - Add the new theme to the `FactionEra` enumeration in `lcars/themes/lcars_theme.py`.
   - Map the theme to a faction and era.

   ```python
   class FactionEra(Enum):
       MY_FACTION_MY_ERA = "my_faction_my_era"
   ```

3. **Update the Demo:**
   - Open `full_theme_demo.py`.
   - Add the new theme to the `quick_themes` list in the `create_control_panel` method.

   ```python
   quick_themes.append(("My Faction Era", FactionEra.MY_FACTION_MY_ERA))
   ```

4. **Test the Theme:**
   - Run the `full_theme_demo.py` script to verify the new theme.
   - Ensure all UI elements adapt to the new palette.

---

## 9. Examples of Palette Integration

### Example 1: Applying a Theme to a Button

```python
from lcars.themes.lcars_theme import get_faction_era_theme, FactionEra

def style_button(button, faction_era):
    theme = get_faction_era_theme(faction_era)
    button.setStyleSheet(f"""
        background-color: {theme.primary_color};
        color: {theme.text_color};
        border: 2px solid {theme.border_color};
        border-radius: 8px;
    """)
```

### Example 2: Dynamic Theme Switching

```python
from lcars.themes.lcars_theme import get_faction_era_theme, FactionEra

def switch_theme(window, faction_era):
    theme = get_faction_era_theme(faction_era)
    window.setStyleSheet(f"""
        background-color: {theme.background_color};
        color: {theme.text_color};
    """)
```

---

For more details, refer to the `lcars_palette.py` file and the `full_theme_demo.py` script.
