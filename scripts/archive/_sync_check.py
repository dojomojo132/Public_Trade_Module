# -*- coding: utf-8 -*-
"""Проверка синхронизации файлов между Конфигурация/ и Конфигурация/Проверка/"""
import pathlib
import filecmp

root = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
proverka = root / "Проверка"

# Файлы, изменённые по git diff
changed_files = [
    "Catalogs/Номенклатура/Forms/ФормаСписка/Ext/Form/Module.bsl",
    "Catalogs/Номенклатура/Forms/ФормаЭлемента/Ext/Form.xml",
    "DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form.xml",
    "DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form/Module.bsl",
    "DataProcessors/ТестыРМК.xml",
    "DataProcessors/ТестыРМК/Forms/Форма.xml",
    "DataProcessors/ТестыРМК/Forms/Форма/Ext/Form.xml",
    "Documents/КассоваяСмена/Forms/ФормаВыбора.xml",
    "Documents/КассоваяСмена/Forms/ФормаВыбора/Ext/Form.xml",
    "Documents/КассоваяСмена/Forms/ФормаВыбора/Ext/Form/Module.bsl",
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
]

print("=" * 70)
print("ПРОВЕРКА СИНХРОНИЗАЦИИ: Конфигурация/ vs Конфигурация/Проверка/")
print("=" * 70)

synced = 0
not_synced = 0
missing_src = 0
missing_prv = 0

for rel in changed_files:
    src = root / rel
    dst = proverka / rel
    
    if not src.exists():
        print(f"  [УДАЛЁН В SRC] {rel}")
        if dst.exists():
            print(f"    ⚠ Ещё существует в Проверка! Нужно удалить там тоже")
            not_synced += 1
        else:
            print(f"    ✓ Тоже отсутствует в Проверка")
            synced += 1
        continue
    
    if not dst.exists():
        print(f"  [НЕТ В ПРОВЕРКА] {rel}")
        missing_prv += 1
        not_synced += 1
        continue
    
    if filecmp.cmp(src, dst, shallow=False):
        synced += 1
    else:
        print(f"  [РАССИНХРОН] {rel}")
        # Show sizes
        src_size = src.stat().st_size
        dst_size = dst.stat().st_size
        print(f"    Конфигурация/: {src_size} байт")
        print(f"    Проверка/:     {dst_size} байт")
        not_synced += 1

print()
print("=" * 70)
print(f"  Синхронизировано: {synced}")
print(f"  НЕ синхронизировано: {not_synced}")
print(f"    - нет в Проверка: {missing_prv}")
print("=" * 70)

if not_synced > 0:
    print("\n⚠ ВНИМАНИЕ: Есть рассинхронизированные файлы!")
    print("  Деплой загружает из Проверка/ — изменения будут ПОТЕРЯНЫ!")
else:
    print("\n✓ Все файлы синхронизированы. Изменения не будут потеряны при деплое.")
