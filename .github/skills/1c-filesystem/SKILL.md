---
name: 1c-filesystem
description: 'Работа с файлами при кириллице в путях. PowerShell ломает русские пути — используем Python-скрипты.'
---

# Файловые операции с кириллицей

Подробные инструкции: [filesystem workaround](../../instructions/filesystem.instructions.md)

При необходимости удалить/переместить/переименовать файлы с кириллицей:
1. Создать Python-скрипт через `create_file` (имя — английское, например `_delete_object.py`)
2. Запустить: `python "D:\Git\Public_Trade_Module\_delete_object.py"`
3. Удалить временный скрипт после выполнения
