# -*- coding: utf-8 -*-
"""Move misplaced CDI entries from after </ConfigVersions> to inside it."""
import pathlib
import re

REPO = pathlib.Path(r"D:\Git\Public_Trade_Module")

for folder in ["Конфигурация", "Конфигурация/Проверка"]:
    cdi_path = REPO / folder / "ConfigDumpInfo.xml"
    if not cdi_path.exists():
        continue
    
    content = cdi_path.read_text(encoding="utf-8-sig")
    
    # Find entries between </ConfigVersions> and </ConfigDumpInfo>
    pattern = r'(</ConfigVersions>)\s*(<Metadata\s.*?)(</ConfigDumpInfo>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        close_cv = match.group(1)
        entries = match.group(2).strip()
        close_cdi = match.group(3)
        
        # Count entries
        entry_count = entries.count("<Metadata name=")
        print(f"{folder}: Перемещаю {entry_count} записей внутрь <ConfigVersions>")
        
        # Remove entries from wrong position
        content = content[:match.start()] + close_cv + "\n" + close_cdi + content[match.end():]
        
        # Insert entries before </ConfigVersions>
        # Add proper indentation (matching existing entries - using tabs)
        # The entries already have indentation, just need to ensure they're before </ConfigVersions>
        content = content.replace(
            "</ConfigVersions>",
            "\t\t" + entries.replace("\n\t\t", "\n\t\t\t\t") + "\n\t</ConfigVersions>"
        )
        
        cdi_path.write_text(content, encoding="utf-8-sig")
        print(f"  ✓ Записи перемещены")
    else:
        print(f"{folder}: Нет записей вне <ConfigVersions>")

print("\n✓ Готово!")
