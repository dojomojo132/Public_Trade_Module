# -*- coding: utf-8 -*-
"""Синхронизация файлов из Конфигурация/ в Конфигурация/Проверка/"""
import pathlib
import shutil

root = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
proverka = root / "Проверка"

# Файлы для копирования (изменены в Конфигурация/, нужно обновить в Проверка/)
files_to_sync = [
    "Catalogs/Номенклатура/Forms/ФормаСписка/Ext/Form/Module.bsl",
    "Catalogs/Номенклатура/Forms/ФормаЭлемента/Ext/Form.xml",
    "DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form.xml",
    "DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form/Module.bsl",
    "DataProcessors/ТестыРМК.xml",
    "DataProcessors/ТестыРМК/Forms/Форма.xml",
    "DataProcessors/ТестыРМК/Forms/Форма/Ext/Form.xml",
    "Documents/ПриходныйКассовыйОрдер/Forms/ФормаДокумента.xml",
    "Documents/ПриходныйКассовыйОрдер/Forms/ФормаДокумента/Ext/Form.xml",
    "Documents/РасходныйКассовыйОрдер/Forms/ФормаДокумента.xml",
    "Documents/РасходныйКассовыйОрдер/Forms/ФормаДокумента/Ext/Form.xml",
    "Enums/ВидыОперацийФискальногоЧека.xml",
    "Reports/Взаиморасчеты.xml",
    "Reports/Взаиморасчеты/Templates/ОсновнаяСхемаКомпоновкиДанных.xml",
    "Reports/Взаиморасчеты/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml",
    "Reports/ДвижениеДенежныхСредств.xml",
    "Reports/ДвижениеДенежныхСредств/Templates/ОсновнаяСхемаКомпоновкиДанных.xml",
    "Reports/ДвижениеДенежныхСредств/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml",
    "Roles/АдминистраторСистемы/Ext/Rights.xml",
    "Roles/БазовыеПраваБПО/Ext/Rights.xml",
    "Roles/ВыполнениеСинхронизацииДанных/Ext/Rights.xml",
    "Roles/ИнтерактивноеОткрытиеВнешнихОтчетовИОбработок/Ext/Rights.xml",
    "Roles/ПолныеПрава/Ext/Rights.xml",
    "Roles/СохранениеДанныхПользователя/Ext/Rights.xml",
    # КассоваяСмена.xml тоже нужно синхронизировать (без ФормаВыбора)
    "Documents/КассоваяСмена.xml",
]

# Файлы/папки для удаления (удалены из Конфигурация/, нужно удалить из Проверка/)
files_to_delete = [
    "Documents/КассоваяСмена/Forms/ФормаВыбора.xml",
    "Documents/КассоваяСмена/Forms/ФормаВыбора/Ext/Form.xml",
    "Documents/КассоваяСмена/Forms/ФормаВыбора/Ext/Form/Module.bsl",
]
folders_to_delete = [
    "Documents/КассоваяСмена/Forms/ФормаВыбора",
]

print("=" * 60)
print("СИНХРОНИЗАЦИЯ: Конфигурация/ → Конфигурация/Проверка/")
print("=" * 60)

# 1. Копирование файлов
print("\n--- Копирование файлов ---")
ok = 0
fail = 0
for rel in files_to_sync:
    src = root / rel
    dst = proverka / rel
    if not src.exists():
        print(f"  ✗ НЕТ ИСТОЧНИКА: {rel}")
        fail += 1
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓ {rel}")
    ok += 1

print(f"\n  Скопировано: {ok}, ошибок: {fail}")

# 2. Удаление файлов из Проверка
print("\n--- Удаление файлов из Проверка/ ---")
for rel in files_to_delete:
    dst = proverka / rel
    if dst.exists():
        dst.unlink()
        print(f"  ✓ Удалён: {rel}")
    else:
        print(f"  - Уже нет: {rel}")

# 3. Удаление папок из Проверка
print("\n--- Удаление папок из Проверка/ ---")
for rel in folders_to_delete:
    dst = proverka / rel
    if dst.exists():
        shutil.rmtree(dst)
        print(f"  ✓ Удалена: {rel}/")
    else:
        print(f"  - Уже нет: {rel}/")

print("\n" + "=" * 60)
print("✓ Синхронизация завершена!")
print("=" * 60)
