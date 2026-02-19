# -*- coding: utf-8 -*-
import subprocess

cwd = r'D:\Git\Public_Trade_Module'

# Count BPO files by category
result = subprocess.run(
    ['git', 'diff', '--name-only', '960be69', 'c07b62c'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
lines = result.stdout.strip().split('\n')
config_lines = [l for l in lines if l.startswith('Конфигурация/') and '/Проверка/' not in l]

# Categorize more precisely
scanner_specific = []
bpo_core_modules = []  # CommonModules for BPO
bpo_catalogs = []  # Catalogs added by BPO
bpo_enums = []
bpo_registers = []
bpo_subsystems = []
bpo_other = []
ptm_modified = []

bpo_module_prefixes = [
    'МенеджерОборудованияКлиент', 'МенеджерОборудованияВызовСервера',
    'МенеджерОборудованияГлобальный', 'МенеджерОборудованияКлиентПереопределяемый',
    'МенеджерОборудованияКлиентПовтИсп', 'МенеджерОборудованияКлиентСервер',
    'МенеджерОборудованияКлиентСерверПереопределяемый', 'МенеджерОборудованияМаркировка',
    'МенеджерОборудованияПовтИсп', 'МенеджерОборудованияВызовСервераПереопределяемый',
    'ОбщегоНазначенияБПО', 'ИнтеграцияПодсистемБПО', 'КассовыеСмены',
    'РаспределеннаяФискализация', 'РассылкаЭлектронныхЧеков', 'ФорматноЛогическийКонтроль',
    'ЭлектронныеСертификаты', 'СертификатыНУЦМинцифры', 'HttpBridge',
    'ВнешниеКомпонентыБПО', 'ЛогированиеОперацийБПО',
]

bpo_catalog_names = [
    'ДрайверыОборудования', 'ОфлайнОборудование', 'ОчередьЭлектронных',
    'ДенежныеСтатьи', 'ПодключаемоеОборудование', 'РабочиеМеста',
    'ШаблоныЭтикеток', 'ШаблоныМагнитных', '_Демо',
]

ptm_names = ['РабочееМестоКассира', 'ПриходТовара', 'ИнформацияНоменклатуры', 
             'Номенклатура/', 'МенеджерОборудования/', 'МенеджерОборудования.xml',
             'ОбщегоНазначения/', 'ManagedApplicationModule', 'Configuration.xml',
             'ConfigDumpInfo.xml', 'DefinedTypes/Номенклатура']

for f in config_lines:
    if any(k in f for k in ['Сканер', 'Scanner', 'сканер']):
        scanner_specific.append(f)
    elif 'CommonModules/' in f and any(p in f for p in bpo_module_prefixes):
        bpo_core_modules.append(f)
    elif 'Catalogs/' in f and any(p in f for p in bpo_catalog_names):
        bpo_catalogs.append(f)
    elif 'Enums/' in f:
        bpo_enums.append(f)
    elif 'Registers/' in f or 'InformationRegisters/' in f or 'AccumulationRegisters/' in f:
        bpo_registers.append(f)
    elif 'Subsystems/' in f:
        bpo_subsystems.append(f)
    elif any(p in f for p in ptm_names):
        ptm_modified.append(f)
    else:
        bpo_other.append(f)

print(f"TOTAL config files (excl. Проверка/): {len(config_lines)}")
print(f"\nSCANNER-SPECIFIC: {len(scanner_specific)}")
for f in scanner_specific: print(f"  {f}")
print(f"\nPTM MODIFIED (existing objects): {len(ptm_modified)}")
for f in ptm_modified: print(f"  {f}")
print(f"\nBPO CORE MODULES (CommonModules): {len(bpo_core_modules)}")
for f in bpo_core_modules: print(f"  {f}")
print(f"\nBPO CATALOGS: {len(bpo_catalogs)}")
for f in bpo_catalogs[:10]: print(f"  {f}")
if len(bpo_catalogs) > 10: print(f"  ... и ещё {len(bpo_catalogs)-10}")
print(f"\nBPO ENUMS: {len(bpo_enums)}")
for f in bpo_enums: print(f"  {f}")
print(f"\nBPO REGISTERS: {len(bpo_registers)}")
for f in bpo_registers: print(f"  {f}")
print(f"\nBPO SUBSYSTEMS: {len(bpo_subsystems)}")
for f in bpo_subsystems[:5]: print(f"  {f}")
if len(bpo_subsystems) > 5: print(f"  ... и ещё {len(bpo_subsystems)-5}")
print(f"\nBPO OTHER: {len(bpo_other)}")
for f in bpo_other[:15]: print(f"  {f}")
if len(bpo_other) > 15: print(f"  ... и ещё {len(bpo_other)-15}")
