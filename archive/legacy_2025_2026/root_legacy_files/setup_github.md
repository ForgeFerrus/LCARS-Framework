# GitHub Setup Instructions for LCARS-Framework

## Після створення репозиторію на GitHub:

1. **Додайте remote до вашого репозиторію:**
```bash
git remote add origin https://github.com/ВАШ_НИК/LCARS-Framework.git
```

2. **Перевірте remote:**
```bash
git remote -v
```

3. **Запушіть поточну гілку:**
```bash
git push -u origin feature/os-mvp
```

4. **Для майбутніх комітів:**
```bash
git add .
git commit -m "Ваш опис змін"
git push
```

## Якщо потрібно перейменувати гілку на main:
```bash
git branch -M main
git push -u origin main
```

## Поточний статус проєкту:
- Гілка: feature/os-mvp
- Останній коміт: e526021 feat: Add OS MVP with Start Menu, Process Supervisor, and Session Manager
- Багато незакомічених змін (нові файли, видалення старих)
- Готовий до push на GitHub
