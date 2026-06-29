"""
Читает .github/project-config.yml и предоставляет настройки проекта.
Используется всеми скриптами вместо хардкода путей.
"""
import pathlib
import re

PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJ_ROOT / ".github" / "project-config.yml"

_config_cache: dict | None = None


def _parse_yaml_simple(text: str) -> dict:
    """Минимальный парсер YAML (без зависимости от PyYAML).
    Поддерживает: скалярные ключи, вложенные словари, списки (- item / - key: val)."""
    root: dict = {}
    # Stack: (indent, container) where container is dict or list
    stack: list[tuple[int, object]] = [(-1, root)]

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(stripped)

        # Pop stack to find parent at lower indent
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent_indent, parent = stack[-1]

        # List item
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            # Parent should be a list; if it's a dict, the last key's value should be a list
            target_list = None
            if isinstance(parent, list):
                target_list = parent
            elif isinstance(parent, dict):
                # Find the last key whose value is a list
                for k in reversed(list(parent.keys())):
                    if isinstance(parent[k], list):
                        target_list = parent[k]
                        break

            if target_list is None:
                i += 1
                continue

            if ":" in item_text:
                # Dict item in list: "- key: value"
                obj: dict = {}
                k, _, v = item_text.partition(":")
                v = v.strip()
                if v and "#" in v:
                    v = v[:v.index("#")].strip()
                obj[k.strip().strip('"')] = _cast(v) if v else {}
                # Read continuation lines at deeper indent
                j = i + 1
                while j < len(lines):
                    nline = lines[j]
                    nstripped = nline.lstrip()
                    if not nstripped or nstripped.startswith("#"):
                        j += 1
                        continue
                    nindent = len(nline) - len(nstripped)
                    if nindent <= indent:
                        break
                    if ":" in nstripped and not nstripped.startswith("- "):
                        nk, _, nv = nstripped.partition(":")
                        nv = nv.strip()
                        if nv and "#" in nv:
                            nv = nv[:nv.index("#")].strip()
                        obj[nk.strip().strip('"')] = _cast(nv) if nv else {}
                    j += 1
                target_list.append(obj)
                i = j
                continue
            else:
                # Simple scalar in list
                target_list.append(_cast(item_text.strip('"')))
                i += 1
                continue

        if ":" not in stripped:
            i += 1
            continue

        key, _, value = stripped.partition(":")
        key = key.strip().strip('"')
        value = value.strip()

        # Inline comment
        if value and "#" in value:
            value = value[:value.index("#")].strip()

        if not value:
            # Check if next non-empty line starts with "- " (list) or key: (dict)
            j = i + 1
            is_list = False
            while j < len(lines):
                nstripped = lines[j].lstrip()
                if nstripped and not nstripped.startswith("#"):
                    is_list = nstripped.startswith("- ")
                    break
                j += 1
            if is_list:
                child_list: list = []
                if isinstance(parent, dict):
                    parent[key] = child_list
                stack.append((indent, parent))  # Keep parent for list lookup
            else:
                child: dict = {}
                if isinstance(parent, dict):
                    parent[key] = child
                stack.append((indent, child))
        elif value.startswith("["):
            items = value.strip("[]").split(",")
            if isinstance(parent, dict):
                parent[key] = [_cast(it.strip().strip('"')) for it in items if it.strip()]
        else:
            if isinstance(parent, dict):
                parent[key] = _cast(value.strip('"'))

        i += 1

    return root


def _cast(v: str):
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    if re.match(r"^\d+$", v):
        return int(v)
    return v.strip('"').strip("'")


def load_config() -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Project config not found: {CONFIG_PATH}")
    text = CONFIG_PATH.read_text(encoding="utf-8")
    _config_cache = _parse_yaml_simple(text)
    return _config_cache


def get(dotpath: str, default=None):
    """Получить значение по точечному пути: get('paths.infobase')"""
    cfg = load_config()
    keys = dotpath.split(".")
    node = cfg
    for k in keys:
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return default
    return node


# Удобные shortcuts
def infobase_path() -> str:
    return get("paths.infobase", "")

def config_root() -> pathlib.Path:
    return PROJ_ROOT / get("paths.config_root", "Конфигурация")

def backups_dir() -> pathlib.Path:
    return PROJ_ROOT / get("paths.backups", "_backups")

def extensions() -> list[dict]:
    return get("extensions", [])
