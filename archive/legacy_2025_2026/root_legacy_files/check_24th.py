from lcars.themes.theme import Theme

colors = Theme.get_colors('24th')
print('24th colors:')
for key in ['bg', 'txt', 'btn1', 'btn2', 'btn3', 'acc1', 'acc2']:
    print(f'  {key}: {colors.get(key, "MISSING")}')
print('Total keys:', len(colors.keys()) if colors else 0)
