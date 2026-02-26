# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Check full structure of Номенклатура forms
nom_forms = base / "Catalogs" / "Номенклатура" / "Forms"
if nom_forms.exists():
    for p in sorted(nom_forms.rglob("*")):
        if p.is_file():
            size = p.stat().st_size
            data = p.read_bytes()
            crlf = data.count(b'\r\n')
            lf_only = data.count(b'\n') - crlf
            has_bom = data[:3] == b'\xef\xbb\xbf'
            print(f"  {size:>6}B {'BOM' if has_bom else 'NO-BOM'} CRLF={crlf} LF={lf_only} | {p.relative_to(nom_forms)}")
        else:
            print(f"  [DIR] | {p.relative_to(nom_forms)}")
