"""
metadata_mapper.py — Отображение путей BSL-файлов на UUID модулей 1С.

Задача: получив абсолютный путь вида
    D:\\Git\\Public_Trade_Module\\Конфигурация\\Documents\\РасходТовара\\Ext\\ObjectModule.bsl
вернуть строку UUID-пары «objectUUID:moduleUUID» для RDBG-клиента.

Алгоритм:
1. Парсинг XML-дескрипторов из каталога конфигурации (configRoot).
2. Построение словаря {абсолютный_путь_bsl → uuid_пара}.
3. Fallback: если UUID не найден — возвращает путь как есть (RDBG принимает
   и символические пути в некоторых версиях платформы).
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

_UUID_PATTERN = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    re.IGNORECASE,
)

_BSL_SUFFIX = ".bsl"


def _extract_uuid(xml_path: Path) -> Optional[str]:
    """Извлечь uuid из атрибута корневого элемента XML-дескриптора."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        uuid_val = root.get("uuid") or root.get("id")
        if uuid_val and _UUID_PATTERN.match(uuid_val):
            return uuid_val.lower()
    except ET.ParseError:
        pass
    return None


def _find_descriptor(bsl_path: Path, config_root: Path) -> Optional[Path]:
    """
    Найти XML-дескриптор объекта-владельца BSL-модуля.

    Структура:
      <config_root>/<Type>/<Name>.xml           ← дескриптор объекта
      <config_root>/<Type>/<Name>/Ext/ObjectModule.bsl
    """
    try:
        rel = bsl_path.relative_to(config_root)
    except ValueError:
        return None

    parts = rel.parts
    if len(parts) >= 2:
        descriptor = config_root / parts[0] / (parts[1] + ".xml")
        if descriptor.exists():
            return descriptor
    return None


class MetadataMapper:
    """
    Кэшированное отображение BSL-путей → UUID-пар для RDBG.

    Параметры
    ----------
    config_root : str | Path
        Корневой каталог выгруженной конфигурации (Конфигурация/).
    """

    def __init__(self, config_root: str | Path) -> None:
        self.config_root = Path(config_root).resolve()
        self._cache: dict[str, str] = {}

    def resolve(self, bsl_file_path: str) -> str:
        """
        Получить UUID-пару для BSL-файла.

        Возвращает строку 'objectUUID:moduleUUID' или исходный путь,
        если UUID не удалось определить.
        """
        key = str(Path(bsl_file_path).resolve())
        if key in self._cache:
            return self._cache[key]

        result = self._compute(Path(bsl_file_path))
        self._cache[key] = result
        return result

    def _compute(self, bsl_path: Path) -> str:
        abs_bsl = bsl_path.resolve()

        descriptor = _find_descriptor(abs_bsl, self.config_root)
        obj_uuid = _extract_uuid(descriptor) if descriptor else None

        module_uuid = self._find_module_uuid(abs_bsl)

        if obj_uuid and module_uuid:
            return f"{obj_uuid}:{module_uuid}"
        if obj_uuid:
            return obj_uuid
        return str(abs_bsl)

    def _find_module_uuid(self, bsl_path: Path) -> Optional[str]:
        """
        Некоторые платформы хранят UUID модуля в соседнем .uuid-файле
        или в родительском Form.xml / ObjectModule.xml.
        """
        parent = bsl_path.parent
        for candidate in parent.iterdir():
            if candidate.suffix == ".xml" and candidate.stem == bsl_path.stem:
                uuid_val = _extract_uuid(candidate)
                if uuid_val:
                    return uuid_val
        return None

    def clear_cache(self) -> None:
        self._cache.clear()

    def warmup(self) -> int:
        """
        Предварительное заполнение кэша обходом config_root.

        Возвращает количество закэшированных модулей.
        """
        count = 0
        for bsl in self.config_root.rglob("*" + _BSL_SUFFIX):
            self.resolve(str(bsl))
            count += 1
        return count
