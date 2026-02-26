---
name: 'Filesystem Workaround'
description: 'Обход проблемы PowerShell с кириллицей в путях. Использовать Python-скрипты.'
---

# Работа с файловой системой (PowerShell + кириллица)

## Проблема

PowerShell полностью ломает кириллические символы в путях:
- Буквы выпадают: `Конфигурация` → `онфигурация`
- `Remove-Item`, `Get-Content`, `Test-Path` НЕ РАБОТАЮТ с русскими путями
- `python -c "код"` через PowerShell — НЕ РАБОТАЕТ (кириллица ломается при передаче)

## ✅ Единственный рабочий метод

**Создать .py файл → Запустить через `python script.py`**

```python
# -*- coding: utf-8 -*-
import pathlib
import shutil

files = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\Имя.xml"),
]
folders = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\Имя"),
]

for f in files:
    if f.exists():
        f.unlink()
        print(f"  ✓ {f.name}")

for folder in folders:
    if folder.exists():
        shutil.rmtree(folder)
        print(f"  ✓ {folder.name}/")
```

1. Создать Python-скрипт через `create_file` (имя файла — английское, например `_delete_object.py`)
2. Запустить: `python "D:\Git\Public_Trade_Module\_delete_object.py"`
3. Удалить временный скрипт после выполнения

## ❌ НЕ работает

- `Remove-Item "Конфигурация\..."` — кириллица ломается
- `python -c "import os; os.remove('путь')"` — кириллица ломается при передаче
- `Get-ChildItem -Path "Конфигурация\..."` — кириллица ломается
- `[System.IO.File]::Delete("путь")` — кириллица ломается

## ✅ Обходной путь для скриптов

```powershell
# Поиск скрипта по английскому имени файла (без кириллицы в -Path):
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "deploy-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName
```
