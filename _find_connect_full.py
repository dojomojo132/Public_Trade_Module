# -*- coding: utf-8 -*-
import pathlib

# Search in МенеджерОборудованияКлиент for how НачатьПодключениеОборудованиеПриОткрытииФормы works
f = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\CommonModules\МенеджерОборудованияКлиент\Ext\Module.bsl")
content = f.read_text("utf-8")

# Find the full function
keyword = "Процедура НачатьПодключениеОборудованиеПриОткрытииФормы"
idx = content.find(keyword)
if idx >= 0:
    # Find the end of the procedure 
    end_marker = "КонецПроцедуры"
    end_idx = content.find(end_marker, idx)
    if end_idx >= 0:
        end_idx += len(end_marker)
    else:
        end_idx = idx + 3000
    
    print(f"Function at position {idx}, length {end_idx - idx}")
    print(content[idx:end_idx])
