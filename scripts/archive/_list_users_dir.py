import pathlib

# Ищем структуру папки Пользователи в Конфигурация
base = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Catalogs')
users_dir = base / 'Пользователи'
if users_dir.exists():
    print('Папка Пользователи существует:')
    for f in sorted(users_dir.rglob('*')):
        print(' ', f.relative_to(base))
else:
    print('Папка Пользователи НЕ найдена')
    print('Все папки в Catalogs:')
    for d in sorted(base.iterdir()):
        if d.is_dir():
            print(' ', d.name)
