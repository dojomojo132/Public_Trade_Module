"""Переименовать сиротские файлы DataProcessors в .orphan"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module") / "Конфигурация" / "DataProcessors"

for name in ["ВыручкаЗаСмену", "ПродажиПоКассам"]:
    xml = base / (name + ".xml")
    folder = base / name
    if xml.exists():
        target = xml.with_suffix(".xml.orphan")
        xml.rename(target)
        print(f"Renamed {name}.xml -> .xml.orphan")
    if folder.is_dir():
        target = base / (name + ".orphan")
        folder.rename(target)
        print(f"Renamed {name}/ -> .orphan/")

print("Done")
