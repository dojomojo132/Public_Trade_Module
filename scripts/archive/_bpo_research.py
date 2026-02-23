# -*- coding: utf-8 -*-
import subprocess
import sys

# Get diff between commits
result = subprocess.run(
    ['git', 'diff', '--name-only', '960be69', 'c07b62c'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=r'D:\Git\Public_Trade_Module'
)

lines = result.stdout.strip().split('\n')

# Filter only Конфигурация/ lines
config_lines = [l for l in lines if l.startswith('Конфигурация/')]
other_lines = [l for l in lines if not l.startswith('Конфигурация/')]

print(f"=== TOTAL FILES CHANGED: {len(lines)} ===")
print(f"=== CONFIG FILES: {len(config_lines)} ===")
print(f"=== OTHER FILES: {len(other_lines)} ===")

print("\n--- OTHER FILES ---")
for l in other_lines:
    print(l)

print("\n--- CONFIG FILES (categorized) ---")

# Categorize
scanner_keywords = ['Сканер', 'сканер', 'Scanner', 'Штрих', 'штрих', 'Barcode', 'barcode']
bpo_keywords = ['БПО', 'BPO', 'Драйвер', 'драйвер', 'Driver', 'Оборудовани', 'оборудовани', 'Подключаемое', 'Офлайн', 'офлайн', 'ШаблоныЭтикеток', 'ШаблоныМагнитных', 'ОчередьЭлектронных', 'ДенежныеСтатьи', 'ДрайверыОборудования', 'ПодключаемоеОборудование', 'Фискальн', 'фискальн', 'ОфлайнОборудование', 'РабочиеМеста', '_Демо']
existing_ptm = ['МенеджерОборудования', 'РабочееМестоКассира', 'ПриходТовара', 'ИнформацияНоменклатуры', 'Номенклатура', 'Организации', 'Контрагенты', 'Склады']

scanner_files = []
bpo_lib_files = []
ptm_modified = []
other_config = []

for f in config_lines:
    is_scanner = any(k in f for k in scanner_keywords)
    is_bpo = any(k in f for k in bpo_keywords)
    is_ptm = any(k in f for k in existing_ptm)
    
    if is_scanner:
        scanner_files.append(f)
    elif is_bpo and not is_ptm:
        bpo_lib_files.append(f)
    elif is_ptm:
        ptm_modified.append(f)
    else:
        other_config.append(f)

print(f"\n=== SCANNER-SPECIFIC FILES ({len(scanner_files)}) ===")
for f in scanner_files:
    print(f"  {f}")

print(f"\n=== BPO LIBRARY FILES ({len(bpo_lib_files)}) ===")
for f in bpo_lib_files:
    print(f"  {f}")

print(f"\n=== PTM EXISTING OBJECTS MODIFIED ({len(ptm_modified)}) ===")
for f in ptm_modified:
    print(f"  {f}")

print(f"\n=== OTHER CONFIG FILES ({len(other_config)}) ===")
for f in other_config:
    print(f"  {f}")

# Also get commit messages
print("\n\n=== COMMIT DETAILS ===")
for commit in ['c07b62c', 'f8d6d1a', '960be69']:
    result2 = subprocess.run(
        ['git', 'log', '--format=%H %s', '-1', commit],
        capture_output=True, text=True, encoding='utf-8',
        cwd=r'D:\Git\Public_Trade_Module'
    )
    print(f"  {result2.stdout.strip()}")
