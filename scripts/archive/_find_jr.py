# -*- coding: utf-8 -*-
import pathlib
f = pathlib.Path(r"c:\Users\vgume\AppData\Roaming\Code\User\workspaceStorage\31191f6a23e0210df38e3e8a316c8170\GitHub.copilot-chat\chat-session-resources\cfd599c4-6841-4f20-9731-912e3eabc39f\toolu_0169UzMVf6rTpf8JYuJHJLxD__vscode-1773445013257\content.txt")
text = f.read_text(encoding="utf-8")
# Find all lines containing ЖР
for line in text.splitlines():
    if "ЖР" in line:
        print(line[:200])
print("---")
# Find block with ЖР source
idx = text.find("Источник:  ЖР")
if idx >= 0:
    print(text[idx:idx+500])
else:
    print("ЖР source not found")
