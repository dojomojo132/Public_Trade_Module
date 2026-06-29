import subprocess, sys

files = [
    'Документация/Спецификации/Стандарт_Форм_Документов.md',
    'ptm-workspace/FRONT/src/lib/document/types.ts',
    'ptm-workspace/FRONT/src/routes/accountant/invoices/new/+page.svelte',
    'ptm-workspace/FRONT/src/routes/accountant/invoices/[id]/+page.svelte',
    'ptm-workspace/ptm-server/src/main.rs',
]

r = subprocess.run(['git', 'add', '--'] + files)
sys.exit(r.returncode)
