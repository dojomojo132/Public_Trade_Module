import subprocess, sys

result = subprocess.run(
    ['python', 'scripts/deploy_ext.py', '--ext', 'PTM_Driver_Vchasno', '--action', 'Load'],
    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90,
    cwd=r'D:\Git\Public_Trade_Module'
)
output = result.stdout + result.stderr
for line in output.splitlines():
    line_s = line.strip()
    if any(k in line_s for k in ['Exit code', 'ВЫПОЛНЕН', 'ошибк', 'InternalInfo', 'owner', 'загружен', 'Файл -']):
        print(repr(line_s))
print('returncode:', result.returncode)
