# -*- coding: utf-8 -*-
import pathlib

f = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\CommonModules\МенеджерОборудования\Ext\Module.bsl")
content = f.read_text("utf-8")

# Find the function that creates ПодключаемоеОборудованиеБПО attribute
keyword = "ПодключаемоеОборудованиеБПО"
idx = content.find(keyword)
print(f"First occurrence at {idx}")

# Show the surrounding function
start = max(0, idx - 500)
end = min(len(content), idx + 800)
print(content[start:end])
