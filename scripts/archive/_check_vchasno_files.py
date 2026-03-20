import sys
sys.stdout.reconfigure(encoding='utf-8')
import pathlib

base = pathlib.Path('D:/Git/Public_Trade_Module/Конфигурация_PTM_Driver_Vchasno/DataProcessors/Вчсн_КассаПанель')
files = [
    base / 'Forms' / 'Форма' / 'Ext' / 'Form.xml',
    base / 'Forms' / 'Форма' / 'Ext' / 'Form' / 'Module.bsl',
    base / 'Ext' / 'ObjectModule.bsl',
    base / 'Вчсн_КассаПанель.xml',
    base.parent.parent / 'Subsystems' / 'Вчсн_ВчасноКаса.xml',
    base.parent.parent / 'Configuration.xml',
    base.parent.parent / 'ConfigDumpInfo.xml',
]
BOM = b'\xef\xbb\xbf'
for f in files:
    if f.exists():
        b = f.read_bytes()
        has_bom = b[:3] == BOM
        has_crlf = b'\r\n' in b
        print(f"OK  {f.name}: BOM={has_bom}, CRLF={has_crlf}, size={len(b)}")
    else:
        print(f"MISSING: {f}")
