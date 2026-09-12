"""
Shim for eras factory
"""

def get_available_eras(faction_key='federation'):
    return ["22nd", "23rd", "24th", "25th", "29th", "32nd"]

def get_era_description(faction_key, era):
    return f"{era} Century Era"
