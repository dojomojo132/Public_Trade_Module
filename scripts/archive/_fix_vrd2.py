# -*- coding: utf-8 -*-
import pathlib

vrd = pathlib.Path(r"C:\Server\Apache24\htdocs\ptm\default.vrd")
content = vrd.read_text(encoding="utf-8")

# Fix ib connection string to include user
old_ib = 'ib="File=D:\\Confiq\\Public Trade Module;"'
new_ib = 'ib="File=D:\\Confiq\\Public Trade Module;Usr=Админ;"'

if 'Usr=' not in content:
    content = content.replace(old_ib, new_ib)
    vrd.write_text(content, encoding="utf-8")
    print("OK: Added Usr=Админ to connection string")
else:
    print("Already has Usr")

print("\nUpdated VRD:")
print(content)
