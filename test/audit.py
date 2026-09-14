from lcars.base.type import LCARS
from lcars.base.register import registry

# Поточні рядкові замінники в LCARS (значення = ключі реєстру)
Covered = {v for k, v in vars(LCARS).items()
           if isinstance(v, str) and not k.startswith('_') and v in registry}

# Всі ключі реєстру що НЕ покриті
Uncovered = sorted(k for k in registry if k not in Covered)

# Фільтруємо: тільки "листові" ключі (немає дочірніх підключів)
# і ключі де назва не надто довга (розумний shortcut)
def LastPart(key): return key.split('.')[-1]
def IsLeaf(key): return not any(k.startswith(key + '.') for k in registry)
def IsShortName(key): return len(LastPart(key)) <= 20

Candidates = [k for k in Uncovered if IsLeaf(k) and IsShortName(k)]

# Групуємо по першому сегменту шляху
from collections import defaultdict
Groups = defaultdict(list)
for k in Candidates:
    Groups[k.split('.')[0]].append(k)

print(f"Реєстр всього      : {len(registry)}")
print(f"Покрито в LCARS    : {len(Covered)}")
print(f"Непокрито всього   : {len(Uncovered)}")
print(f"Кандидати shortcuts: {len(Candidates)}")
print()

for Group, Keys in sorted(Groups.items()):
    print(f"=== {Group} ({len(Keys)}) ===")
    for k in sorted(Keys):
        Name = LastPart(k)
        # Чи є конфлікт з наявним атрибутом
        Conflict = hasattr(LCARS, Name) and getattr(LCARS, Name) != k
        Flag = " [CONFLICT]" if Conflict else ""
        print(f"  {Name:30s} = \"{k}\"{Flag}")
    print()
