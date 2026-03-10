# -*- coding: utf-8 -*-
import pathlib

vrd = pathlib.Path(r"C:\Server\Apache24\htdocs\ptm\default.vrd")
content = vrd.read_text(encoding="utf-8")

# Add httpServices after ws line
old = '\t<ws pointEnableCommon="true"/>'
new = '\t<ws pointEnableCommon="true"/>\r\n\t<httpServices publishByDefault="true"/>'

if '<httpServices' not in content:
    content = content.replace(old, new)
    vrd.write_text(content, encoding="utf-8")
    print("OK: httpServices added")
else:
    print("Already has httpServices")

print("\nUpdated content:")
print(content)
