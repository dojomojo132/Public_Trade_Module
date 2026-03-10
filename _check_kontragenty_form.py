# -*- coding: utf-8 -*-
import pathlib

form_path = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаГруппы\Ext\Form.xml')
print("Exists:", form_path.exists())
if form_path.exists():
    content = form_path.read_bytes()
    print("BOM:", content[:3] == b'\xef\xbb\xbf')
    text = content.lstrip(b'\xef\xbb\xbf').decode('utf-8', errors='replace')
    # Найдём все DataPath
    import re
    for m in re.finditer(r'<DataPath>(.*?)</DataPath>', text):
        print("DataPath:", m.group(1))
    # Найдём все InputField names
    for m in re.finditer(r'<InputField name="(.*?)"', text):
        print("InputField:", m.group(1))
    print("\n--- FULL CONTENT ---")
    print(text[:2000])
