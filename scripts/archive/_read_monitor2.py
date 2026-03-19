import pathlib
txt = pathlib.Path(r'c:\Users\vgume\AppData\Roaming\Code\User\workspaceStorage\31191f6a23e0210df38e3e8a316c8170\GitHub.copilot-chat\chat-session-resources\b69abf77-3d34-4420-bd16-3c5d2c743e00\toolu_vrtx_012BZqEofbgk1Ab6KE3G8Ch6__vscode-1773906926771\content.txt').read_text(encoding='utf-8', errors='replace')
# Ищем ключевые строки
for i, ln in enumerate(txt.splitlines()):
    if any(key in ln for key in ['ОШИБОК', 'ИТОГ', 'ERROR', 'ClientFile', 'EXCP', 'src\\backend', 'Ошибок найдено']):
        print(f'{i}: {ln}')
