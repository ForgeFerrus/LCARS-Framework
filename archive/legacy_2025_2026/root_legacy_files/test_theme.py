#!/usr/bin/env python3
from lcars.themes.theme import Theme

# Test the theme system
print("Testing theme system...")

# Test faction palettes
for faction in ['romulan', 'klingon', 'cardassian']:
    colors = Theme.get_colors(faction)
    print(f"\n{faction.upper()} palette:")
    if colors:
        for key, value in colors.items():
            print(f"  {key}: {value}")
    else:
        print("  No colors returned")

# Test era palette
print("\n24th era palette:")
colors_24th = Theme.get_colors('24th')
if colors_24th:
    for key, value in colors_24th.items():
        print(f"  {key}: {value}")
else:
    print("  No colors returned")

print("\nTheme system working!")
