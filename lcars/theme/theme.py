# LCARS Theme System
from lcars.base.type import LCARS

def GetTheme(Era=None):
    return {"era": Era or "LCARS_25TH", "palette": {}}

def GetLcarsFontStyle(size=12, weight="normal"):
    return f"font-size: {size}px; font-weight: {weight};"

def setup_lcars_font(size=12, weight="normal"):
    return GetLcarsFontStyle(size, weight)
