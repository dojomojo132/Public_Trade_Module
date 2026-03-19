"""Восстанавливает оригинальный Module.bsl из backup"""
import os, shutil

src = r'D:\Git\Public_Trade_Module\Конфигурация\HTTPServices\МобильнаяКасса\Ext\Module.bsl'
bak = src + '.orig'

if not os.path.exists(bak):
    print('ERROR: backup not found:', bak)
    exit(1)

with open(bak, encoding='utf-8-sig') as r:
    content = r.read()
    
with open(src, 'w', encoding='utf-8-sig') as w:
    w.write(content)
    
print(f'Restored: {src} ({len(content)} chars)')
bom_in_content = content.startswith('\ufeff')
print('BOM in content string:', bom_in_content)

# Check file bytes
with open(src, 'rb') as rb:
    first3 = rb.read(3)
print('File BOM bytes:', first3.hex(), '= UTF-8 BOM' if first3 == b'\xef\xbb\xbf' else '= OTHER')
