# -*- coding: utf-8 -*-
import pathlib, re, sys

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl")
content = p.read_text(encoding='utf-8-sig')

out = pathlib.Path(r"D:\Git\Public_Trade_Module\_rmk_analysis.txt")

lines_out = []
lines_out.append(f"Всего строк: {content.count(chr(10))}")

# Найти все функции/процедуры
pattern = re.compile(r'^(&\S+\s*\n\s*)?((?:Функция|Процедура)\s+(\w+)\s*\()', re.MULTILINE)
funcs = [(m.start(), m.group(3), 'Функция' in m.group(2) if m.group(2) else False) for m in pattern.finditer(content)]

lines_out.append(f"Всего функций/процедур: {len(funcs)}")
lines_out.append("")
lines_out.append("=== ФУНКЦИИ С 0 ВЫЗОВОВ (потенциальный мертвый код) ===")
for pos, name, is_func in funcs:
    line = content[:pos].count('\n') + 1
    calls = len(re.findall(r'\b' + re.escape(name) + r'\s*\(', content)) - 1
    if calls == 0:
        typ = "Функция" if is_func else "Процедура"
        lines_out.append(f"  [стр.{line:4d}] {typ:10s} {name}")

lines_out.append("")
lines_out.append("=== ВСЕ ФУНКЦИИ/ПРОЦЕДУРЫ ===")
for pos, name, is_func in funcs:
    line = content[:pos].count('\n') + 1
    calls = len(re.findall(r'\b' + re.escape(name) + r'\s*\(', content)) - 1
    typ = "Функция" if is_func else "Процедура"
    lines_out.append(f"  [стр.{line:4d}] {typ:10s} {name:50s} ({calls} вызовов)")

out.write_text('\n'.join(lines_out), encoding='utf-8')
print("OK:", str(out))
