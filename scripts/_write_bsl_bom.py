#!/usr/bin/env python3
"""Write BSL files with UTF-8 BOM + CRLF."""
import pathlib
import sys

def write_bsl(path: str, content: str) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = content.replace("\r\n", "\n").replace("\n", "\r\n")
    if not text.endswith("\r\n"):
        text += "\r\n"
    p.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    print(f"OK {path}")

if __name__ == "__main__":
    write_bsl(sys.argv[1], pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))