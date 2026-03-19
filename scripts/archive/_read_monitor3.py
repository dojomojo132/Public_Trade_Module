import pathlib
txt = pathlib.Path(r'c:\Users\vgume\AppData\Roaming\Code\User\workspaceStorage\31191f6a23e0210df38e3e8a316c8170\GitHub.copilot-chat\chat-session-resources\b69abf77-3d34-4420-bd16-3c5d2c743e00\toolu_vrtx_012BZqEofbgk1Ab6KE3G8Ch6__vscode-1773906926771\content.txt').read_text(encoding='utf-8', errors='replace')
lines = txt.splitlines()
# Показываем первые 30 строк и последние 10 строк - чтобы увидеть заголовок мониторинга
print('=== ПЕРВЫЕ 15 СТРОК ===')
for ln in lines[:15]: print(ln)
print()
print('=== ОШИБКИ (строки 10-20) ===')
for ln in lines[10:25]: print(ln)
