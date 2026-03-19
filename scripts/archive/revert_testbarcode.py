"""Откат: удаляем testbarcodeGET из Module.bsl"""
import pathlib

p = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics\HTTPServices\Анл_МобильнаяКасса\Ext\Module.bsl')
bsl = p.read_text(encoding='utf-8-sig')

marker = '// ============================================================\n// Тест производительности'
idx = bsl.find(marker)
if idx != -1:
    clean = bsl[:idx].rstrip() + '\n'
    p.write_text(clean, encoding='utf-8-sig')
    print('Reverted. Lines:', len(clean.splitlines()))
else:
    print('Already clean, lines:', len(bsl.splitlines()))
