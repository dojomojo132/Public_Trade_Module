# -*- coding: utf-8 -*-
import pathlib

log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")

if not log_dir.exists():
    print("Папка логов не найдена")
else:
    print("=== ЛОГИ ДЕПЛОЯ ===\n")
    
    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not log_files:
        print("Лог-файлы не найдены")
    else:
        for log_file in log_files[:5]:  # Последние 5 файлов
            print(f"\n{'='*60}")
            print(f"ФАЙЛ: {log_file.name}")
            print(f"{'='*60}")
            
            try:
                with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    if content.strip():
                        print(content)
                    else:
                        print("(пустой файл)")
            except Exception as e:
                print(f"Ошибка чтения: {e}")
