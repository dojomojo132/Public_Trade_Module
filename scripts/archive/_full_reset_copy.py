# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
test = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Полностью удалить Проверку
if test.exists():
    print("Удаление папки Проверка...")
    shutil.rmtree(test)
    print("✓ Удалена")

# Скопировать всё из основной конфигурации в Проверку
print("\nКопирование конфигурации...")
shutil.copytree(base, test, ignore=shutil.ignore_patterns('Проверка', '_*'))
print(f"✓ Скопировано в {test}")

print("\nГотово!")
