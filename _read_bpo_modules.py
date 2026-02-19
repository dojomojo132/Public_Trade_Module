# -*- coding: utf-8 -*-
import subprocess

cwd = r'D:\Git\Public_Trade_Module'

# Get BPO commit МенеджерОборудованияКлиент module
files_to_check = [
    'Конфигурация/CommonModules/МенеджерОборудованияКлиент/Ext/Module.bsl',
    'Конфигурация/CommonModules/МенеджерОборудованияГлобальный/Ext/Module.bsl',
    'Конфигурация/CommonModules/МенеджерОборудованияВызовСервера/Ext/Module.bsl',
    'Конфигурация/CommonModules/МенеджерОборудованияКлиентПереопределяемый/Ext/Module.bsl',
]

for f in files_to_check:
    print(f"\n{'='*80}")
    print(f"FILE: {f}")
    print(f"{'='*80}")
    result = subprocess.run(
        ['git', 'show', f'c07b62c:{f}'],
        capture_output=True, text=True, encoding='utf-8',
        cwd=cwd
    )
    if result.returncode == 0:
        content = result.stdout
        # Print first 100 lines
        lines = content.split('\n')
        for i, line in enumerate(lines[:100]):
            print(f"{i+1:4d} | {line}")
        if len(lines) > 100:
            print(f"... ({len(lines)} lines total, showing first 100)")
    else:
        print(f"ERROR: {result.stderr.strip()}")
