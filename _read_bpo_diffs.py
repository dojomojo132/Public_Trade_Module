# -*- coding: utf-8 -*-
import subprocess

cwd = r'D:\Git\Public_Trade_Module'

# Show the diff of RMK form module between pre-BPO and BPO commit
result = subprocess.run(
    ['git', 'diff', '960be69', 'c07b62c', '--',
     'Конфигурация/DataProcessors/РабочееМестоКассира/Forms/Форма/Ext/Form/Module.bsl'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
print("=== RMK MODULE DIFF ===")
print(result.stdout[:5000] if result.stdout else "No diff or error")
print(f"\n(Total diff length: {len(result.stdout)} chars)")

print("\n\n=== ПРИХОД ТОВАРА MODULE DIFF ===")
result2 = subprocess.run(
    ['git', 'diff', '960be69', 'c07b62c', '--',
     'Конфигурация/Documents/ПриходТовара/Forms/ФормаДокумента/Ext/Form/Module.bsl'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
print(result2.stdout[:5000] if result2.stdout else "No diff or error")

print("\n\n=== ИнформацияНоменклатуры MODULE DIFF ===")
result3 = subprocess.run(
    ['git', 'diff', '960be69', 'c07b62c', '--',
     'Конфигурация/DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form/Module.bsl'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
# This is a new file, so check git show instead
if not result3.stdout:
    result3 = subprocess.run(
        ['git', 'show', 'c07b62c:Конфигурация/DataProcessors/ИнформацияНоменклатуры/Forms/Форма/Ext/Form/Module.bsl'],
        capture_output=True, text=True, encoding='utf-8',
        cwd=cwd
    )
    print("(File content at BPO commit:)")
    print(result3.stdout[:3000] if result3.stdout else "Not found")
else:
    print(result3.stdout[:3000])

# Also check МенеджерОборудования diff
print("\n\n=== МенеджерОборудования MODULE DIFF ===")
result4 = subprocess.run(
    ['git', 'diff', '960be69', 'c07b62c', '--',
     'Конфигурация/CommonModules/МенеджерОборудования/Ext/Module.bsl'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
print(result4.stdout[:5000] if result4.stdout else "No diff or error")

# Check the ManagedApplicationModule diff  
print("\n\n=== ManagedApplicationModule DIFF ===")
result5 = subprocess.run(
    ['git', 'diff', '960be69', 'c07b62c', '--',
     'Конфигурация/Ext/ManagedApplicationModule.bsl'],
    capture_output=True, text=True, encoding='utf-8',
    cwd=cwd
)
print(result5.stdout[:3000] if result5.stdout else "No diff or error")
