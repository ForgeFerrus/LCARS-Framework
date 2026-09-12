# Minimal linguistic matrix for faction languages
# This module provides sample glyph sets for different factions and a helper to retrieve them.

LANGUAGE_MATRIX = {
    'federation': ['A','B','C','D','E','F','G','H'],
    'klingon': ['Q','W','E','R','T','Y','U'],
    'romulan': ['α','β','γ','δ','ε','ζ'],
    'cardassian': ['∑','∆','Φ','Ψ','Ω']
}

def get_glyphs(faction: str):
    return LANGUAGE_MATRIX.get(faction.lower(), [])
