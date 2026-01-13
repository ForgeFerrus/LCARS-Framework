# PCARS22 UI element descriptors (moved from era22.py)
# This file is imported by era22.py and can be reused by other themes/eras.

PCARS22_ELEMENTS = [
    # Chronometer panel (верхній лівий)
    {"id": "chronometer_panel", "type": "panel", "text": "", "color_role": "panel", "width": 400, "height": 120, "x": 60, "y": 40,
     "children": [
         {"id": "chronometer_label", "type": "label", "text": "CHRONOMETER", "color_role": "text", "width": 120, "height": 20},
         {"id": "stardate_display", "type": "label", "text": "-3755.53415", "color_role": "text", "width": 220, "height": 44}
     ]
    },
    # Left vertical strip (з трьома індикаторами)
    {"id": "left_strip", "type": "panel", "text": "", "color_role": "panel", "width": 60, "height": 320, "x": 40, "y": 180,
     "children": [
         {"id": "swatch_top", "type": "indicator", "width": 36, "height": 36, "color_role": "primary"},
         {"id": "swatch_mid", "type": "indicator", "width": 36, "height": 36, "color_role": "accent"},
         {"id": "swatch_bot", "type": "indicator", "width": 36, "height": 36, "color_role": "secondary"}
     ]
    },
    # Main display area (центр)
    {"id": "main_big_display", "type": "panel", "text": "", "color_role": "background", "width": 600, "height": 260, "x": 520, "y": 60},
    # Navigation buttons (вертикально)
    {"id": "nav_v_scn", "type": "button", "text": "SCN", "color_role": "primary", "width": 48, "height": 36, "x": 120, "y": 200},
    {"id": "nav_v_nav", "type": "button", "text": "NAV", "color_role": "secondary", "width": 48, "height": 36, "x": 120, "y": 250},
    {"id": "nav_v_sen", "type": "button", "text": "SEN", "color_role": "accent", "width": 48, "height": 36, "x": 120, "y": 300},
    # Control buttons (праворуч)
    {"id": "control_engage", "type": "button", "text": "ENGAGE", "color_role": "primary", "width": 120, "height": 36, "x": 1150, "y": 120},
    {"id": "control_standby", "type": "button", "text": "STANDBY", "color_role": "secondary", "width": 120, "height": 36, "x": 1150, "y": 170},
    # Logo panel (центр низ)
    {"id": "logo_panel", "type": "panel", "text": "", "color_role": "panel", "width": 320, "height": 160, "x": 600, "y": 360,
     "children": [
         {"id": "logo_label", "type": "label", "text": "ENTERPRISE LOGO", "color_role": "accent", "width": 200, "height": 80}
     ]
    },
    # Status indicator (праворуч від центру)
    {"id": "status_indicator", "type": "indicator", "color_role": "primary", "width": 36, "height": 36, "x": 950, "y": 340},
    # Info panel (низ ліворуч)
    {"id": "info_panel", "type": "panel", "text": "SYSTEM INFO", "color_role": "panel", "width": 320, "height": 120, "x": 60, "y": 500,
     "children": [
         {"id": "info_label_1", "type": "label", "text": "POWER", "color_role": "text", "width": 80, "height": 24},
         {"id": "info_value_1", "type": "label", "text": "100%", "color_role": "accent", "width": 60, "height": 24},
         {"id": "info_label_2", "type": "label", "text": "SHIELDS", "color_role": "text", "width": 80, "height": 24},
         {"id": "info_value_2", "type": "label", "text": "UP", "color_role": "primary", "width": 60, "height": 24}
     ]
    },
    # Велика кнопка RED ALERT (низ праворуч)
    {"id": "big_action_btn", "type": "button", "text": "RED ALERT", "color_role": "accent", "width": 320, "height": 72, "x": 950, "y": 500},
]
