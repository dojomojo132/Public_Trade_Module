# -*- coding: utf-8 -*-
import os
dp = r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors"
for f in sorted(os.listdir(dp)):
    if "РабочееМестоКассира" in f or f.endswith(".orphan"):
        print(f"ORPHAN: {f}")
print("--- Check done ---")

# Also check for any .orphan in top-level DataProcessors
for f in sorted(os.listdir(dp)):
    if f.endswith(".orphan") or f.endswith(".bak"):
        print(f"OTHER: {f}")
