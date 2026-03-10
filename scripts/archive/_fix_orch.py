path = r'd:\Git\Public_Trade_Module\.github\agents\orchestrator.agent.md'
content = open(path, encoding='utf-8').read()

replacements = [
    (
        'запустить `python scripts/_dialog.py 1` (интерактивный диалог):\n   - SELECTED:post_monitoring:1 («Всё работает») → запустить `python scripts/_dialog.py 2` (commit / новый запрос)',
        'запустить `vscode_askQuestions` (header: `post_monitoring`, ДИАЛОГ 1):\n   - SELECTED:1 («Всё работает») → запустить `vscode_askQuestions` (header: `next_action`, ДИАЛОГ 2)'
    ),
    (
        'Git commit — **ТОЛЬКО** после выбора SELECTED:1 в `python scripts/_dialog.py 2`',
        'Git commit — **ТОЛЬКО** после выбора SELECTED:1 (Закоммитить) в `vscode_askQuestions` (ДИАЛОГ 2)'
    ),
    (
        '(только через SELECTED:1 в `_dialog.py 2`)',
        '(только через SELECTED:1 в vscode_askQuestions ДИАЛОГ 2)'
    ),
    (
        'ФАЗА 6: Спецификация → _dialog.py 2 (интерактивный) → Commit (по SELECTED:1)',
        'ФАЗА 6: Спецификация → vscode_askQuestions ДИАЛОГ 2 → Commit (по SELECTED:1)'
    ),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'Replaced: {old[:60]}...')
    else:
        print(f'NOT FOUND: {old[:60]}...')

open(path, 'w', encoding='utf-8').write(content)
print('Done')
