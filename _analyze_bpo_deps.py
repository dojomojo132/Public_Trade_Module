# -*- coding: utf-8 -*-
"""Анализ зависимостей модулей БПО для сканера"""
import pathlib
import re

BPO_ROOT = pathlib.Path(r"D:\Git\БПО_ДЕМО")

# Модули, которые мы хотим внедрить
TARGET_MODULES = [
    "МенеджерОборудования",
    "МенеджерОборудованияВызовСервера",
    "МенеджерОборудованияКлиент",
    "МенеджерОборудованияКлиентПовтИсп",
    "МенеджерОборудованияКлиентСервер",
    "МенеджерОборудованияГлобальный",
    "МенеджерОборудованияПовтИсп",
    "МенеджерОборудованияВызовСервераПереопределяемый",
    "МенеджерОборудованияКлиентПереопределяемый",
    "МенеджерОборудованияКлиентСерверПереопределяемый",
    "ОборудованиеУстройстваВвода",
    "ОборудованиеУстройстваВводаВызовСервера",
    "ОборудованиеУстройстваВводаКлиент",
    "ВнешниеКомпонентыБПО",
    "ВнешниеКомпонентыБПОКлиент",
    "ВнешниеКомпонентыБПОПереопределяемый",
    "ОбщегоНазначенияБПО",
    "ОбщегоНазначенияБПОКлиент",
    "ОбщегоНазначенияБПОКлиентСервер",
    "ОбщегоНазначенияБПОПереопределяемый",
    "ОбщегоНазначенияБПОПовтИсп",
    "ОбщегоНазначенияБПОСлужебныйВызовСервера",
    "ИнтеграцияПодсистемБПО",
    "ИнтеграцияПодсистемБПОКлиент",
    "ИнтеграцияПодсистемБПОКлиентПовтИсп",
    "ИнтеграцияПодсистемБПОСлужебныйВызовСервера",
    "НастройкиПрограммыБПО",
    "НастройкиПрограммыБПОКлиент",
    "НастройкиПрограммыБПОПереопределяемый",
    "ПодключаемоеОборудованиеДрайверКлиент",
    "ЛогированиеОперацийБПО",
    "ЛогированиеОперацийБПОКлиент",
    "ЛогированиеОперацийБПОПереопределяемый",
    "ЛогированиеОперацийБПОСлужебныйВызовСервера",
]

# Все модули в BPO
all_modules_dir = BPO_ROOT / "CommonModules"
all_modules = set()
if all_modules_dir.exists():
    for d in all_modules_dir.iterdir():
        if d.is_dir():
            all_modules.add(d.name)
        elif d.name.endswith('.xml') and not d.name.startswith('.'):
            all_modules.add(d.stem)

print(f"Всего модулей в БПО: {len(all_modules)}")
print(f"Целевых модулей: {len(TARGET_MODULES)}")

# Анализируем каждый целевой модуль — какие другие модули он вызывает
missing_deps = set()
module_deps = {}

for mod_name in TARGET_MODULES:
    bsl_path = BPO_ROOT / "CommonModules" / mod_name / "Ext" / "Module.bsl"
    if not bsl_path.exists():
        print(f"\n[WARN] Модуль не найден: {mod_name}")
        continue
    
    with open(bsl_path, encoding='utf-8-sig') as f:
        code = f.read()
    
    # Ищем обращения к другим модулям: ИмяМодуля.Метод(
    refs = set(re.findall(r'(\w+)\.\w+\(', code))
    
    # Оставляем только реальные модули
    real_refs = refs & all_modules
    deps = real_refs - set(TARGET_MODULES)
    
    if deps:
        module_deps[mod_name] = deps
        missing_deps.update(deps)

print(f"\n{'='*60}")
print("НЕДОСТАЮЩИЕ ЗАВИСИМОСТИ:")
print(f"{'='*60}")

for mod, deps in sorted(module_deps.items()):
    print(f"\n  {mod} → зависит от:")
    for d in sorted(deps):
        print(f"    ❌ {d}")

print(f"\n{'='*60}")
print(f"ИТОГО: Нужно добавить {len(missing_deps)} модулей:")
print(f"{'='*60}")
for m in sorted(missing_deps):
    print(f"  + {m}")

# Рекурсивный анализ — проверяем зависимости недостающих модулей
print(f"\n{'='*60}")
print("РЕКУРСИВНЫЙ АНАЛИЗ ЗАВИСИМОСТЕЙ...")
print(f"{'='*60}")

all_needed = set(TARGET_MODULES)
to_check = list(missing_deps)
checked = set(TARGET_MODULES)
level = 1

while to_check:
    print(f"\n--- Уровень {level} ---")
    next_check = []
    for mod_name in to_check:
        if mod_name in checked:
            continue
        checked.add(mod_name)
        all_needed.add(mod_name)
        
        bsl_path = BPO_ROOT / "CommonModules" / mod_name / "Ext" / "Module.bsl"
        if not bsl_path.exists():
            continue
        
        with open(bsl_path, encoding='utf-8-sig') as f:
            code = f.read()
        
        refs = set(re.findall(r'(\w+)\.\w+\(', code))
        real_refs = refs & all_modules
        new_deps = real_refs - all_needed
        
        if new_deps:
            print(f"  {mod_name} → нужны:")
            for d in sorted(new_deps):
                print(f"    + {d}")
                next_check.append(d)
                all_needed.add(d)
    
    if not next_check:
        break
    to_check = next_check
    level += 1

print(f"\n{'='*60}")
print(f"ПОЛНЫЙ СПИСОК МОДУЛЕЙ ДЛЯ ОБЪЕДИНЕНИЯ ({len(all_needed)}):")
print(f"{'='*60}")
for m in sorted(all_needed):
    print(f"  ✓ {m}")

# Проверяем МенеджерОборудованияГлобальный подробно
print(f"\n{'='*60}")
print("ДЕТАЛИ: МенеджерОборудованияГлобальный")
print(f"{'='*60}")
glob_path = BPO_ROOT / "CommonModules" / "МенеджерОборудованияГлобальный" / "Ext" / "Module.bsl"
if glob_path.exists():
    with open(glob_path, encoding='utf-8-sig') as f:
        lines = f.readlines()
    for i, line in enumerate(lines[:50], 1):
        print(f"  {i:3}: {line.rstrip()}")
