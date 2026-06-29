# -*- coding: utf-8 -*-
"""Fix duplicate UUIDs in КассоваяСмена TCH metadata."""
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Конфигурация"
KS = ROOT / "Documents" / "КассоваяСмена.xml"
CDI = ROOT / "ConfigDumpInfo.xml"


def collect_existing() -> set[str]:
    existing: set[str] = set()
    for path in ROOT.rglob("*.xml"):
        if path == KS:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for match in re.findall(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            text,
            re.I,
        ):
            existing.add(match.lower())
    return existing


def main() -> None:
    ks_text = KS.read_text(encoding="utf-8-sig")
    cdi_text = CDI.read_text(encoding="utf-8-sig")

    block = re.search(
        r'<Metadata name="Document\.КассоваяСмена".*?</Metadata>',
        cdi_text,
        re.S,
    )
    if not block:
        raise SystemExit("КассоваяСмена block not found in ConfigDumpInfo.xml")

    patch_ids = re.findall(r'id="([0-9a-f-]{36})"', block.group(0), re.I)
    internal = re.findall(
        r"<xr:TypeId>([0-9a-f-]{36})</xr:TypeId>|<xr:ValueId>([0-9a-f-]{36})</xr:ValueId>",
        ks_text,
        re.I,
    )
    internal_ids = [a or b for a, b in internal]
    all_old = sorted(set(patch_ids + internal_ids))

    existing = collect_existing()
    mapping: dict[str, str] = {}
    for old in all_old:
        key = old.lower()
        if key in mapping:
            continue
        while True:
            new = str(uuid.uuid4())
            if new.lower() not in existing and new.lower() not in mapping.values():
                mapping[key] = new
                existing.add(new.lower())
                break

    print(f"Replacing {len(mapping)} UUIDs")
    for old, new in mapping.items():
        print(f"  {old} -> {new}")

    for path in (KS, CDI):
        text = path.read_text(encoding="utf-8-sig")
        for old, new in mapping.items():
            text = re.sub(old, new, text, flags=re.I)
        path.write_text(text, encoding="utf-8-sig")

    print("Done")


if __name__ == "__main__":
    main()