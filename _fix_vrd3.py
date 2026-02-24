# -*- coding: utf-8 -*-
import pathlib

vrd = pathlib.Path(r"C:\Server\Apache24\htdocs\ptm\default.vrd")
content = vrd.read_text(encoding="utf-8")

# Fix: Usr needs to be in quotes (XML entity encoded)
old = 'ib="File=D:\\Confiq\\Public Trade Module;Usr=Админ;"'
new = 'ib="File=&quot;D:\\Confiq\\Public Trade Module&quot;;Usr=&quot;Админ&quot;;"'

content = content.replace(old, new)
vrd.write_text(content, encoding="utf-8")
print("Fixed VRD:")
print(content)
