# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Спецификации\MCP_ИНСТРУМЕНТЫ_РЕАЛИЗАЦИЯ.md")
text = p.read_text(encoding="utf-8")
print(text)
