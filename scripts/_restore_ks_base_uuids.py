# -*- coding: utf-8 -*-
"""Restore original КассоваяСмена document UUIDs; keep new TCH UUIDs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Конфигурация"
KS = ROOT / "Documents" / "КассоваяСмена.xml"
CDI = ROOT / "ConfigDumpInfo.xml"

# new -> original (document-level only, NOT tabular sections)
RESTORE = {
    "d83ebb1c-dd3a-441c-9634-8f0bbff56a57": "25758dba-a71b-4a22-a206-6f72aa9a04a8",
    "a3cd497d-e518-4e9c-b14f-a7368963ac8f": "1497e3b1-0188-41d6-b088-5ef41ade00aa",
    "de77b481-7d61-49f9-af52-c4df8220e81a": "4ade588b-9df0-47ad-8e25-1d0145c9022d",
    "6116610d-7b34-4d2d-9049-5a010ae4f712": "7c76109a-0b04-4515-b92b-2e2876cc34b2",
    "b713926e-8f42-426e-8097-1dccb1610592": "3389c3c3-96be-41a1-9469-51f1df4fc6a5",
    "58d311f9-dbeb-4cab-9385-4ec90ddaa689": "f0086de6-6334-42f0-ab07-f0e0337853f0",
    "2eac4383-d51c-4d1d-95c6-c856d0f5ff4b": "5e9bd7f7-b721-4f5f-a0eb-fb50ca98751d",
    "00710174-0af7-41c4-a2ea-11c4981219ba": "7f09179f-2d54-4275-9916-ce092a267689",
    "db02820d-f9c5-4390-9a72-c0e858c38a2b": "ab9bc6ac-2e34-44a6-ac57-01877f02d78c",
    "1a76ad58-b17a-4cc8-934d-c6614696a29d": "d69810fe-b33b-4fe9-bb9b-191efbdb91ad",
    "d54d7a13-a5be-494b-b446-0e53e67913c3": "00ddfe67-f984-4777-ae21-d367505b58ff",
    "aea5e4a0-d646-45b4-a910-7d202c5a761a": "0a2e36e0-5969-46f5-b12b-21e509b7d192",
    "df66a160-ab41-4c49-aac1-17ff9885e140": "ce733a7f-7b7c-45f5-a290-a0cf6c2990e0",
    "99d59cf2-931b-4c09-a8c0-773e21002e20": "cbba5721-834d-40c9-91e4-957718a4d424",
    "1f5a7939-2ff2-4c62-b593-5fe566cffdb4": "b1163afd-7f00-4e59-a521-be43c31f821a",
}


def main() -> None:
    for path in (KS, CDI):
        text = path.read_text(encoding="utf-8-sig")
        for new, old in RESTORE.items():
            text = text.replace(new, old)
        path.write_text(text, encoding="utf-8-sig")
    print(f"Restored {len(RESTORE)} base UUIDs")


if __name__ == "__main__":
    main()