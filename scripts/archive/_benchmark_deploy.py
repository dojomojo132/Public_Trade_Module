# -*- coding: utf-8 -*-
"""Точный замер времени каждого этапа деплоя"""
import time, subprocess, sys, pathlib

ROOT = pathlib.Path(r'd:\Git\Public_Trade_Module')
WRAPPER = ROOT / 'scripts' / '_ps_wrapper.py'
PYTHON = sys.executable

results = []

def measure(label, action, extra_args=None):
    """Замерить время выполнения действия деплоя"""
    args = [PYTHON, str(WRAPPER), 'deploy', '-Action', action, '-SkipDtBackup']
    if extra_args:
        args.extend(extra_args)
    
    print(f"\n{'='*60}")
    print(f"[СТАРТ] {label}")
    print(f"{'='*60}")
    
    t0 = time.perf_counter()
    result = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8', errors='replace')
    t1 = time.perf_counter()
    
    elapsed = t1 - t0
    success = 'OK' in result.stdout or result.returncode == 0
    
    # Extract key status line
    status_line = ""
    for line in result.stdout.splitlines():
        if '[OK]' in line or '[FAIL]' in line:
            status_line = line.strip()
    
    print(f"  Время: {elapsed:.2f} сек")
    print(f"  Exit code: {result.returncode}")
    print(f"  Статус: {status_line}")
    
    results.append({
        'label': label,
        'time': elapsed,
        'exit_code': result.returncode,
        'status': status_line
    })
    return result

def measure_validate():
    """Замерить валидацию"""
    args = [PYTHON, str(WRAPPER), 'validate']
    
    print(f"\n{'='*60}")
    print(f"[СТАРТ] Валидация XML")
    print(f"{'='*60}")
    
    t0 = time.perf_counter()
    result = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8', errors='replace')
    t1 = time.perf_counter()
    
    elapsed = t1 - t0
    
    status_line = ""
    for line in result.stdout.splitlines():
        if 'ИТОГ' in line or 'ОШИБОК' in line or 'готова' in line:
            status_line = line.strip()
    
    print(f"  Время: {elapsed:.2f} сек")
    print(f"  Статус: {status_line}")
    
    results.append({
        'label': 'Валидация XML',
        'time': elapsed,
        'exit_code': result.returncode,
        'status': status_line
    })
    return result

def measure_monitor():
    """Замерить мониторинг"""
    args = [PYTHON, str(WRAPPER), 'monitor', '-Action', 'Check', '-LastMinutes', '3']
    
    print(f"\n{'='*60}")
    print(f"[СТАРТ] Мониторинг")
    print(f"{'='*60}")
    
    t0 = time.perf_counter()
    result = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8', errors='replace')
    t1 = time.perf_counter()
    
    elapsed = t1 - t0
    
    status_line = ""
    for line in result.stdout.splitlines():
        if 'ЖР:' in line and ('OK' in line or 'ERROR' in line):
            status_line = line.strip()
    
    print(f"  Время: {elapsed:.2f} сек")
    print(f"  Статус: {status_line}")
    
    results.append({
        'label': 'Мониторинг',
        'time': elapsed,
        'exit_code': result.returncode,
        'status': status_line
    })

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ ДЕПЛОЯ PTM             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    total_start = time.perf_counter()
    
    # Этап 1: Валидация
    measure_validate()
    
    # Этап 2: Загрузка
    measure('Загрузка (LoadConfigFromFiles)', 'Load')
    
    # Этап 3: Проверка
    measure('Проверка (CheckConfig)', 'Check')
    
    # Этап 4: Обновление БД
    measure('Обновление БД (UpdateDBCfg)', 'Update')
    
    # Этап 5: Мониторинг
    measure_monitor()
    
    total_end = time.perf_counter()
    total = total_end - total_start
    
    # Итог
    print(f"\n{'='*60}")
    print(f"         ИТОГОВЫЙ ОТЧЁТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print(f"{'='*60}")
    print(f"\n{'Этап':<45} {'Время':>8} {'Доля':>6}")
    print(f"{'-'*60}")
    
    for r in results:
        pct = (r['time'] / total * 100) if total > 0 else 0
        print(f"  {r['label']:<43} {r['time']:>6.1f}с {pct:>5.1f}%")
    
    print(f"{'-'*60}")
    print(f"  {'ИТОГО':<43} {total:>6.1f}с  100%")
    print()
    
    # Detect bottleneck
    slowest = max(results, key=lambda x: x['time'])
    print(f"  Узкое место: {slowest['label']} ({slowest['time']:.1f}с)")

if __name__ == '__main__':
    main()
