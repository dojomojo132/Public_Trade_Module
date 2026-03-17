"""Анализ структуры Form.xml для планирования автоматизации генерации."""
import re
import pathlib

BASE = pathlib.Path(r"d:/Git/Public_Trade_Module/Конфигурация")

forms_to_analyze = [
    BASE / "Catalogs/Номенклатура/Forms/ФормаСписка/Ext/Form.xml",
    BASE / "Catalogs/Номенклатура/Forms/ФормаЭлемента/Ext/Form.xml",
    BASE / "DataProcessors/РабочееМестоКассира/Forms/Форма/Ext/Form.xml",
    BASE / "Documents/ЧекККМ/Forms",
]

element_tags = [
    "Table", "UsualGroup", "LabelField", "InputField", "Button", "CommandBar",
    "AutoCommandBar", "ButtonGroup", "CheckBox", "RadioButton", "PictureField",
    "ProgressBar", "Decoration", "HTMLDocumentField", "SpreadsheetDocumentField",
    "ChartField", "FormattedDocumentField", "PlannerField", "GanttChart",
    "Pages", "Page", "ViewField",
]

def analyze_form(path):
    if not path.exists():
        return {"error": "not found"}
    content = path.read_text(encoding="utf-8")
    ids = [int(x) for x in re.findall(r' id="(-?\d+)"', content)]
    ids_positive = [x for x in ids if x > 0]
    result = {
        "lines": content.count("\n"),
        "chars": len(content),
        "total_ids": len(ids_positive),
        "max_id": max(ids_positive) if ids_positive else 0,
        "has_DataSource": "DataSource" in content,
        "has_Attributes": "<Attributes>" in content,
        "has_Events": "<Events>" in content,
        "elements": {},
        "top_level_blocks": [],
    }
    for tag in element_tags:
        count = len(re.findall(f"<{tag}[ >]", content))
        if count:
            result["elements"][tag] = count
    # Top-level blocks
    for tag in ["AutoCommandBar", "Events", "ChildItems", "Attributes", "DataSources",
                "CommandInterface", "Parameters", "Categories"]:
        if f"<{tag}" in content:
            result["top_level_blocks"].append(tag)
    return result


# Анализируем FormaSpiska
print("=== Catalog ФормаСписка ===")
r = analyze_form(forms_to_analyze[0])
for k, v in r.items():
    print(f"  {k}: {v}")

print()
print("=== Catalog ФормаЭлемента ===")
r = analyze_form(forms_to_analyze[1])
for k, v in r.items():
    print(f"  {k}: {v}")

print()
print("=== DataProcessor РабочееМестоКассира.Форма ===")
r = analyze_form(forms_to_analyze[2])
for k, v in r.items():
    print(f"  {k}: {v}")

# Ищем форму ЧекКМ
doc_forms = BASE / "Documents/ЧекККМ"
if doc_forms.exists():
    print("\n=== Document ЧекККМ structure ===")
    for p in sorted(doc_forms.rglob("*.xml")):
        rel = p.relative_to(BASE)
        print(f"  {rel}")
    for p in sorted(doc_forms.rglob("*.bsl")):
        rel = p.relative_to(BASE)
        print(f"  {rel}")
