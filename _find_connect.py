# -*- coding: utf-8 -*-
import pathlib

f = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\CommonModules\МенеджерОборудованияКлиент\Ext\Module.bsl")
content = f.read_text("utf-8")

# Find НачатьПодключениеОборудованиеПриОткрытииФормы
keyword = "ПриОткрытииФормы"
idx = content.find(keyword)
if idx >= 0:
    start = max(0, idx - 300)
    end = min(len(content), idx + 800)
    print(f"Found '{keyword}' at position {idx}")
    print("=" * 80)
    print(content[start:end])
else:
    print(f"NOT FOUND: '{keyword}'")
    # Try alternative names
    for alt in ["ПодключениеОборудование", "НачатьПодключение", "ОткрытииФормы"]:
        idx2 = content.find(alt)
        if idx2 >= 0:
            print(f"\nFound alternative '{alt}' at {idx2}")
            print(content[max(0,idx2-100):idx2+300])
