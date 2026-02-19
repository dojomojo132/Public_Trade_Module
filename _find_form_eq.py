# -*- coding: utf-8 -*-
import pathlib

f = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\CommonModules\МенеджерОборудованияКлиент\Ext\Module.bsl")
content = f.read_text("utf-8")

# Find ПодключаемоеОборудованиеНаФорме
keyword = "Функция ПодключаемоеОборудованиеНаФорме"
idx = content.find(keyword)
if idx >= 0:
    end = min(len(content), idx + 1500)
    print(content[idx:end])
else:
    print("NOT FOUND")
    # Search broader
    idx2 = content.find("ПодключаемоеОборудованиеНаФорме")
    if idx2 >= 0:
        print(f"Found at {idx2}")
        print(content[max(0,idx2-100):idx2+500])
