# Настройка плагинов для дебага и тестирования 1С 8.3.24

**Дата создания:** 20 января 2026 г.  
**Версия:** 1.0  
**Цель:** Интеграция инструментов отладки и автотестирования в VS Code + GitHub Copilot + MCP

---

## 0. Подготовительные работы

### 0.1 Проверка системных требований

#### Минимальные требования
```
ОС:           Windows 10/11 (64-bit) или Windows Server 2016+
Процессор:    Intel Core i5 / AMD Ryzen 5 или выше
ОЗУ:          16 GB (рекомендуется 32 GB)
Диск:         SSD с 50 GB свободного места
.NET:         .NET Framework 4.7.2 или выше
```

#### Проверка PowerShell
```powershell
# Проверка версии PowerShell (требуется 5.1+)
$PSVersionTable.PSVersion

# Проверка прав администратора
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Проверка политики выполнения скриптов
Get-ExecutionPolicy
# Если Restricted, установить:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 0.2 Установка базового ПО

#### 1. Git
```powershell
# Установка через Chocolatey
choco install git -y

# Или скачать: https://git-scm.com/download/win

# Проверка установки
git --version

# Настройка
git config --global user.name "Ваше Имя"
git config --global user.email "email@example.com"
git config --global core.autocrlf true
```

#### 2. Node.js (LTS версия)
```powershell
# Установка через Chocolatey
choco install nodejs-lts -y

# Или скачать: https://nodejs.org/

# Проверка установки
node --version  # Требуется v18.0.0 или выше
npm --version
```

#### 3. Python (для некоторых инструментов)
```powershell
# Установка через Chocolatey
choco install python -y

# Проверка
python --version  # Требуется 3.9+
```

#### 4. Visual Studio Code
```powershell
# Установка через Chocolatey
choco install vscode -y

# Или скачать: https://code.visualstudio.com/

# Проверка
code --version
```

### 0.3 Установка платформы 1С 8.3.24

#### Установка платформы
```powershell
# 1. Скачать дистрибутив 1С:Предприятие 8.3.24
# с сайта releases.1c.ru (требуется подписка ИТС)

# 2. Запустить установщик
# setup.exe /S /InstallDir="C:\Program Files\1cv8\8.3.24"

# 3. Проверка установки
& "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" /version

# 4. Установка лицензий (если требуется)
# Панель управления → Администрирование → 1С:Предприятие 8 Лицензирование
```

#### Регистрация COM-объектов
```powershell
# COM-объект V83.COMConnector регистрируется автоматически при установке платформы 1С
# Файл находится в: C:\Program Files\1cv8\8.3.24\bin\comcntr.dll

# Если объект не зарегистрирован, выполнить вручную:
cd "C:\Program Files\1cv8\8.3.24\bin"
regsvr32.exe comcntr.dll

# Для 64-разрядной версии (если установлена):
cd "C:\Program Files\1cv8\8.3.24\bin"
regsvr32.exe comcntr.dll

# Проверка регистрации через реестр
Get-ItemProperty "HKLM:\SOFTWARE\Classes\V83.COMConnector" -ErrorAction SilentlyContinue

# Альтернатива: проверка через COM
$regasm = Get-ItemProperty "HKLM:\SOFTWARE\Classes\CLSID\{181E893D-73A4-4722-B61D-D604B3D67D47}" -ErrorAction SilentlyContinue
if ($regasm) {
    Write-Host "✓ COM-компоненты 1С зарегистрированы"
} else {
    Write-Host "✗ Требуется регистрация COM-компонентов"
}
```

#### Проверка компонентов COM
```powershell
# Проверка регистрации COM-объектов
try {
    $comObject = New-Object -ComObject "V83.COMConnector"
    if ($comObject) {
        Write-Host "✓ COM-объект V83.COMConnector доступен"
        
        # Проверка версии компоненты
        $version = $comObject.GetType().Assembly.GetName().Version
        Write-Host "  Версия: $version"
    }
} catch {
    Write-Host "✗ COM-объект не зарегистрирован" -ForegroundColor Red
    Write-Host "  Ошибка: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "  Выполните регистрацию: regsvr32.exe comcntr.dll" -ForegroundColor Yellow
}
```

**Важно:** 
- COM-компоненты регистрируются автоматически при установке платформы
- Файл `comcntr.dll` - это и есть COM Connector для подключения к 1С
- Для работы с COM из Node.js используется встроенный PowerShell (не требует npm пакетов)
- Если используется 64-битный Node.js, нужна 64-битная версия платформы 1С

### 0.4 Подготовка информационных баз

#### Создание файловой тестовой базы
```powershell
# 1. Создать директорию для баз
$testDbPath = "D:\1C_Bases\PTM_Test"
New-Item -ItemType Directory -Path $testDbPath -Force

# 2. Создать информационную базу
& "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" CREATEINFOBASE File="$testDbPath" /Out "$testDbPath\create.log"

# 3. Проверить создание
if (Test-Path "$testDbPath\1Cv8.1CD") {
    Write-Host "✓ Тестовая база создана: $testDbPath"
} else {
    Write-Host "✗ Ошибка создания базы"
}
```

#### Создание базы разработки
```powershell
# База для отладки
$devDbPath = "D:\1C_Bases\PTM_Development"
New-Item -ItemType Directory -Path $devDbPath -Force
& "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" CREATEINFOBASE File="$devDbPath"
```

#### Загрузка конфигурации в базы
```powershell
# Путь к XML конфигурации
$configXml = "D:\Git\Public_Trade_Module\Configuration.xml"

# Загрузка в тестовую базу
& "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" DESIGNER `
    /F"$testDbPath" `
    /LoadCfg "$configXml" `
    /Out "$testDbPath\load-config.log"

# Загрузка в базу разработки
& "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" DESIGNER `
    /F"$devDbPath" `
    /LoadCfg "$configXml" `
    /Out "$devDbPath\load-config.log"

Write-Host "✓ Конфигурация загружена в обе базы"
```

#### Создание пользователей
```powershell
# Скрипт для создания пользователей (выполнить в 1С)
$createUsersScript = @"
Пользователь = Справочники.Пользователи.СоздатьЭлемент();
Пользователь.Наименование = "TestRunner";
Пользователь.Записать();

// Установить полные права
ПользовательИБ = ПользователиИнформационнойБазы.СоздатьПользователя();
ПользовательИБ.Имя = "TestRunner";
ПользовательИБ.ПолноеИмя = "Автоматический запуск тестов";
ПользовательИБ.Роли.Добавить(Метаданные.Роли.ПолныеПрава);
ПользовательИБ.Записать();
"@

# Сохранить скрипт
$createUsersScript | Out-File -FilePath "$testDbPath\create-users.bsl" -Encoding UTF8

Write-Host "✓ Скрипт создания пользователей сохранен"
Write-Host "  Выполните его вручную в конфигураторе или через /Execute"
```

### 0.5 Установка инструментов разработки

#### Установка OneScript (для отладки)
```powershell
# Установка через Chocolatey
choco install onescript -y

# Или через установщик с GitHub
# https://github.com/EvilBeaver/OneScript/releases

# Проверка
oscript -version

# Установка пакетов
opm install 1commands
opm install vanessa-behavior
```

#### Установка EDT (опционально, для advanced отладки)
```powershell
# Скачать 1C:Enterprise Development Tools
# https://releases.1c.ru/project/DevelopmentTools10

# Установка аналогична обычному Eclipse
```

### 0.6 Настройка Node.js окружения

#### Рекомендуемый подход: PowerShell + Node.js (без native модулей)

**Важно:** Пакеты `win32ole` и `node-comconnector` несовместимы с современными версиями Node.js. Используйте PowerShell для работы с COM объектами 1С - это наиболее стабильное решение.

#### Создание package.json
```powershell
# Перейти в корень проекта
cd D:\Git\Public_Trade_Module

# Инициализация npm проекта
npm init -y

# Установка необходимых пакетов (только кроссплатформенные)
npm install --save-dev `
    xml2js `
    express `
    chalk `
    commander `
    jest
```

#### package.json (итоговый)
```json
{
  "name": "ptm-test-framework",
  "version": "1.0.0",
  "description": "Testing and debugging tools for PTM configuration",
  "main": "index.js",
  "scripts": {
    "test": "node .vscode/plugins/test-runner.js --all",
    "test:unit": "node .vscode/plugins/test-runner.js --unit",
    "test:integration": "node .vscode/plugins/test-runner.js --integration",
    "coverage": "node .vscode/plugins/coverage-checker.js",
    "debug": "node .vscode/plugins/debug-launcher.js"
  },
  "keywords": ["1c", "testing", "debugging"],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "xml2js": "^0.6.0",
    "express": "^4.18.0",
    "chalk": "^4.1.2",
    "commander": "^11.0.0",
    "jest": "^29.0.0"
  }
}
```

### 0.7 Настройка GitHub Copilot

#### Активация подписки
```
1. Открыть VS Code
2. Перейти в Extensions (Ctrl+Shift+X)
3. Найти "GitHub Copilot"
4. Нажать Install
5. Войти через GitHub аккаунт (требуется активная подписка)
6. Проверить статус: Ctrl+Shift+P → "GitHub Copilot: Check Status"
```

#### Проверка работы Copilot
```javascript
// Создать тестовый файл test.bsl
// Начать писать: "Функция Получить"
// Copilot должен предложить автодополнение
```

### 0.8 Настройка MCP сервера для 1С

#### Установка MCP SDK
```powershell
# Установка через npm
npm install -g @modelcontextprotocol/sdk

# Проверка
mcp --version
```

#### Создание структуры MCP сервера
```powershell
# Создать директорию для MCP
mkdir mcp-config
cd mcp-config

# Инициализация MCP проекта
npm init -y
npm install @modelcontextprotocol/sdk xml2js
```

#### Базовый конфигурационный файл
Файл: `mcp-config/1c-server-config.json`

```json
{
  "server": {
    "name": "1c-metadata-server",
    "version": "1.0.0",
    "port": 3001
  },
  "connections": {
    "development": {
      "type": "file",
      "path": "D:\\1C_Bases\\PTM_Development",
      "user": "Admin",
      "password": ""
    },
    "testing": {
      "type": "file",
      "path": "D:\\1C_Bases\\PTM_Test",
      "user": "TestRunner",
      "password": ""
    }
  },
  "cache": {
    "enabled": true,
    "ttl": 300
  }
}
```

#### Проверка подключения к 1С через PowerShell (рекомендуемый способ)
```javascript
// Файл: mcp-config/test-connection.js
const { exec } = require('child_process');
const path = require('path');

function testConnection() {
  // PowerShell скрипт для подключения к 1С
  const psScript = `
    try {
        [System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.InteropServices") > $null
        $v83 = New-Object -ComObject "V83.COMConnector"
        $conn = $v83.Connect('File="D:\\\\1C_Bases\\\\PTM_Test";Usr="TestRunner";')
        
        Write-Host "✓ Подключение успешно"
        
        # Тест выполнения запроса
        $result = $conn.Eval('ТекущаяДата()')
        Write-Host "✓ Выполнение кода работает"
        Write-Host "Текущая дата из 1С: $result"
    } catch {
        Write-Host "✗ Ошибка подключения: $($_.Exception.Message)"
        exit 1
    }
  `;

  // Сохраняем скрипт во временный файл
  const tempFile = path.join(__dirname, 'temp-script.ps1');
  const fs = require('fs');
  fs.writeFileSync(tempFile, psScript);

  // Выполняем PowerShell скрипт
  exec(`powershell -ExecutionPolicy Bypass -File "${tempFile}"`, (error, stdout, stderr) => {
    // Удаляем временный файл
    fs.unlinkSync(tempFile);
    
    if (error) {
      console.error('Ошибка выполнения:', error.message);
      return;
    }
    console.log(stdout);
  });
}

testConnection();
```

```powershell
# Запуск проверки
node mcp-config/test-connection.js
```

**Преимущества PowerShell подхода:**
- ✅ Встроен в Windows, не требует дополнительных модулей
- ✅ Прямой доступ к COM объектам
- ✅ Совместим со всеми версиями Node.js
- ✅ Нет проблем с native модулями
- ✅ Простой и надежный способ

### 0.9 Создание структуры проекта

#### Автоматическое создание структуры
```powershell
# Скрипт создания всех необходимых директорий
$projectRoot = "D:\Git\Public_Trade_Module"
$directories = @(
    ".vscode",
    ".vscode\plugins",
    ".github",
    ".github\workflows",
    "mcp-tools",
    "mcp-config",
    "Тесты",
    "Тесты\Модульные",
    "Тесты\Интеграционные",
    "Тесты\UI",
    "Тесты\Производительности",
    "test-results",
    "test-results\coverage",
    "test-results\reports",
    "docs\templates"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $projectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force
        Write-Host "✓ Создана: $dir"
    } else {
        Write-Host "○ Существует: $dir"
    }
}

Write-Host "`n✓ Структура проекта создана"
```

### 0.10 Настройка .gitignore

Файл: `.gitignore`

```gitignore
# 1С специфичные
*.1CD
*.dt
*.log
*.txt
1Cv8.1CD
1Cv8.CDN
1Cv8.lgf
1Cv8Diag.txt

# Тестовые базы
**/1C_Bases/

# Результаты тестов
test-results/**/*.xml
test-results/**/*.html
test-results/temp-*
coverage/

# Node
node_modules/
npm-debug.log
package-lock.json

# VS Code
.vscode/*.log
.vscode/settings.local.json

# Временные файлы
*.tmp
*.temp
*.cache
```

### 0.11 Проверочный чеклист готовности

```powershell
# Скрипт полной проверки готовности
# Файл: check-readiness.ps1

Write-Host "=== ПРОВЕРКА ГОТОВНОСТИ ОКРУЖЕНИЯ ===" -ForegroundColor Cyan

$checks = @()

# 1. PowerShell
$psVersion = $PSVersionTable.PSVersion.Major
$checks += @{
    Name = "PowerShell версия"
    Status = $psVersion -ge 5
    Message = "v$($PSVersionTable.PSVersion)"
}

# 2. Git
try {
    $gitVersion = (git --version) -replace 'git version ', ''
    $checks += @{ Name = "Git"; Status = $true; Message = $gitVersion }
} catch {
    $checks += @{ Name = "Git"; Status = $false; Message = "Не установлен" }
}

# 3. Node.js
try {
    $nodeVersion = (node --version)
    $checks += @{ Name = "Node.js"; Status = $true; Message = $nodeVersion }
} catch {
    $checks += @{ Name = "Node.js"; Status = $false; Message = "Не установлен" }
}

# 4. VS Code
try {
    $codeVersion = (code --version)[0]
    $checks += @{ Name = "VS Code"; Status = $true; Message = $codeVersion }
} catch {
    $checks += @{ Name = "VS Code"; Status = $false; Message = "Не установлен" }
}

# 5. 1С Платформа
$platform1c = "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe"
if (Test-Path $platform1c) {
    $checks += @{ Name = "1С 8.3.24"; Status = $true; Message = "Установлена" }
} else {
    $checks += @{ Name = "1С 8.3.24"; Status = $false; Message = "Не найдена" }
}

# 6. COM-объект
try {
    $com = New-Object -ComObject "V83.COMConnector"
    $checks += @{ Name = "COM V83"; Status = $true; Message = "Доступен" }
} catch {
    $checks += @{ Name = "COM V83"; Status = $false; Message = "Недоступен" }
}

# 7. Тестовая база
$testDb = "D:\1C_Bases\PTM_Test\1Cv8.1CD"
if (Test-Path $testDb) {
    $checks += @{ Name = "Тестовая БД"; Status = $true; Message = "Создана" }
} else {
    $checks += @{ Name = "Тестовая БД"; Status = $false; Message = "Отсутствует" }
}

# 8. Структура проекта
$projectDirs = @(".vscode", "mcp-tools", "Тесты")
$allExist = $true
foreach ($dir in $projectDirs) {
    if (-not (Test-Path $dir)) { $allExist = $false }
}
$checks += @{ 
    Name = "Структура проекта"
    Status = $allExist
    Message = if ($allExist) { "Создана" } else { "Неполная" }
}

# Вывод результатов
Write-Host "`n"
foreach ($check in $checks) {
    $icon = if ($check.Status) { "✓" } else { "✗" }
    $color = if ($check.Status) { "Green" } else { "Red" }
    Write-Host "$icon $($check.Name): " -NoNewline
    Write-Host $check.Message -ForegroundColor $color
}

$failedCount = ($checks | Where-Object { -not $_.Status }).Count
Write-Host "`n"
if ($failedCount -eq 0) {
    Write-Host "=== ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ ===" -ForegroundColor Green
    Write-Host "Можно приступать к настройке" -ForegroundColor Green
} else {
    Write-Host "=== ОБНАРУЖЕНО ПРОБЛЕМ: $failedCount ===" -ForegroundColor Red
    Write-Host "Устраните проблемы перед продолжением" -ForegroundColor Yellow
}
```

```powershell
# Запуск проверки
.\check-readiness.ps1
```

### 0.12 Итоговый чеклист подготовки

- [ ] **Системные требования** проверены (ОЗУ, диск, ОС)
- [ ] **PowerShell 5.1+** установлен, политика выполнения настроена
- [ ] **Git** установлен и настроен
- [ ] **Node.js LTS** установлен (v18+)
- [ ] **VS Code** установлен
- [ ] **1С:Предприятие 8.3.24** установлено
- [ ] **COM-объекты** зарегистрированы и доступны
- [ ] **Тестовая база** создана (PTM_Test)
- [ ] **База разработки** создана (PTM_Development)
- [ ] **Конфигурация** загружена в обе базы
- [ ] **Пользователи** созданы (TestRunner с полными правами)
- [ ] **OneScript** установлен (опционально)
- [ ] **npm пакеты** установлены (xml2js, win32ole, express)
- [ ] **GitHub Copilot** активирован и работает
- [ ] **MCP SDK** установлен
- [ ] **Структура проекта** создана (все папки)
- [ ] **.gitignore** настроен
- [ ] **Проверочный скрипт** выполнен успешно

---

## 1. Отладка (Debug)

### 1.1 Конфигурация launch.json

Файл: `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "oscript",
      "request": "launch",
      "name": "Отладка 1С через OneScript",
      "program": "${file}",
      "args": [],
      "cwd": "${workspaceFolder}",
      "runtimeExecutable": "oscript.exe",
      "internalConsoleOptions": "openOnSessionStart"
    },
    {
      "type": "node",
      "request": "attach",
      "name": "Attach к 1С через DBG",
      "port": 1550,
      "address": "localhost",
      "restart": true
    }
  ]
}
```

### 1.2 Расширения VS Code для отладки

```powershell
# Установка необходимых расширений
code --install-extension 1c-syntax.language-1c-bsl
code --install-extension 1c-syntax.language-1c-bsl-debug
code --install-extension hbenl.vscode-test-explorer
code --install-extension ryanluker.vscode-coverage-gutters
```

### 1.3 MCP Инструменты для дебага

Файл: `mcp-tools/1c-debug-bridge.js`

```javascript
{
  "tools": [
    {
      "name": "start_1c_debug_session",
      "description": "Запускает сеанс отладки 1С",
      "inputSchema": {
        "type": "object",
        "properties": {
          "infobase": {
            "type": "string",
            "description": "Строка подключения к базе"
          },
          "user": {
            "type": "string",
            "description": "Имя пользователя"
          },
          "breakpoints": {
            "type": "array",
            "description": "Список точек останова",
            "items": {
              "type": "string",
              "example": "Module.bsl:45"
            }
          }
        },
        "required": ["infobase", "user"]
      }
    },
    {
      "name": "evaluate_expression",
      "description": "Вычисляет выражение в контексте отладки",
      "inputSchema": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            "description": "1С выражение для вычисления"
          }
        },
        "required": ["expression"]
      }
    },
    {
      "name": "get_call_stack",
      "description": "Получает текущий стек вызовов"
    },
    {
      "name": "get_local_variables",
      "description": "Получает значения локальных переменных"
    }
  ]
}
```

### 1.4 Реализация Debug Bridge

Файл: `mcp-tools/debug-bridge.js`

```javascript
const com = require('win32ole');

class DebugBridge {
  constructor() {
    this.connection = null;
  }

  async attachTo1C(infobase, user, password = "") {
    try {
      const v83 = new com.Dispatch('V83.COMConnector');
      this.connection = v83.Connect(`File="${infobase}";Usr="${user}";Pwd="${password}";`);
      return { status: "attached", infobase };
    } catch (error) {
      return { status: "error", message: error.message };
    }
  }

  async setBreakpoint(module, line) {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugSetBreakpoint(module, line);
  }

  async evaluateExpression(expr) {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    try {
      const result = this.connection.DebugEvaluate(expr);
      return { success: true, value: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getCallStack() {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugGetCallStack();
  }

  async getVariables() {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugGetLocalVars();
  }

  disconnect() {
    if (this.connection) {
      this.connection = null;
    }
  }
}

// Глобальный экземпляр
const bridge = new DebugBridge();

// Экспорт MCP инструментов
module.exports = {
  tools: [
    {
      name: "debug_attach",
      handler: async (params) => {
        return await bridge.attachTo1C(
          params.infobase,
          params.user,
          params.password
        );
      }
    },
    {
      name: "debug_eval",
      handler: async (params) => {
        return await bridge.evaluateExpression(params.expression);
      }
    },
    {
      name: "debug_stack",
      handler: async () => {
        return await bridge.getCallStack();
      }
    },
    {
      name: "debug_vars",
      handler: async () => {
        return await bridge.getVariables();
      }
    }
  ]
};
```

---

## 2. Автотестирование

### 2.1 Структура тестов

```
/project-root/
├── Тесты/
│   ├── Модульные/              # Юнит-тесты отдельных функций
│   │   ├── ТестОбщийМодуль.epf
│   │   ├── ТестРаботаСНоменклатурой.epf
│   │   └── ТестРасчетыСКонтрагентами.epf
│   ├── Интеграционные/         # Тесты бизнес-процессов
│   │   ├── ТестПроведенияДокумента.epf
│   │   ├── ТестФискальногоЧека.epf
│   │   └── ТестОбменаДанными.epf
│   ├── UI/                     # Тесты пользовательских форм
│   │   ├── ТестФормыКассира.epf
│   │   └── ТестФормыТовара.epf
│   └── Производительности/     # Нагрузочные тесты
│       └── ТестБольшихВыборок.epf
└── test-results/               # Результаты тестов
    ├── coverage/
    └── reports/
```

### 2.2 Конфигурация тестирования

Файл: `.vscode/test-config.json`

```json
{
  "testFramework": "1C:Unit",
  "testInfobase": {
    "connection": "tcp://localhost/PTM_Test",
    "user": "TestRunner",
    "password": ""
  },
  "coverage": {
    "enabled": true,
    "threshold": 70,
    "excludePatterns": [
      "**/Ext/**",
      "**/CommonTemplates/**",
      "**/Forms/**"
    ]
  },
  "parallel": false,
  "timeout": 30000,
  "retryOnFailure": 2,
  "screenshotOnFailure": true,
  "outputFormat": ["console", "xml", "html"]
}
```

### 2.3 MCP Инструменты для тестирования

Файл: `mcp-tools/1c-unit-runner.js`

```javascript
{
  "tools": [
    {
      "name": "run_unit_tests",
      "description": "Запускает юнит-тесты из внешней обработки",
      "inputSchema": {
        "type": "object",
        "properties": {
          "testFile": {
            "type": "string",
            "description": "Путь к файлу теста (.epf)"
          },
          "testCase": {
            "type": "string",
            "description": "Имя конкретного теста (опционально)"
          },
          "infobase": {
            "type": "string",
            "description": "Строка подключения к тестовой базе"
          }
        },
        "required": ["testFile", "infobase"]
      }
    },
    {
      "name": "generate_test_template",
      "description": "Генерирует шаблон теста для объекта метаданных",
      "inputSchema": {
        "type": "object",
        "properties": {
          "objectType": {
            "type": "string",
            "enum": ["CommonModule", "Document", "Catalog", "DataProcessor"]
          },
          "objectName": {
            "type": "string",
            "description": "Имя объекта метаданных"
          },
          "methodName": {
            "type": "string",
            "description": "Имя метода для тестирования"
          }
        },
        "required": ["objectType", "objectName", "methodName"]
      }
    },
    {
      "name": "run_all_tests",
      "description": "Запускает все тесты в проекте",
      "inputSchema": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "enum": ["unit", "integration", "ui", "all"],
            "default": "all"
          }
        }
      }
    },
    {
      "name": "get_test_coverage",
      "description": "Получает отчет о покрытии кода тестами"
    }
  ]
}
```

### 2.4 Реализация Test Runner

Файл: `.vscode/plugins/test-runner.js`

```javascript
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

class TestRunner {
  constructor() {
    this.config = this.loadConfig();
    this.results = [];
  }

  loadConfig() {
    const configPath = path.join(__dirname, '../test-config.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }

  async runTests(options = {}) {
    const testPattern = options.pattern || '**/*.epf';
    const category = options.category || 'all';
    
    // Получаем список тестовых файлов
    const testFiles = this.findTestFiles(testPattern, category);
    
    console.log(`Найдено тестов: ${testFiles.length}`);
    
    for (const testFile of testFiles) {
      await this.runSingleTest(testFile);
    }
    
    this.printSummary();
    return this.results;
  }

  findTestFiles(pattern, category) {
    const testDir = path.join(__dirname, '../../Тесты');
    const categoryMap = {
      'unit': 'Модульные',
      'integration': 'Интеграционные',
      'ui': 'UI',
      'all': ''
    };
    
    const searchDir = category === 'all' 
      ? testDir 
      : path.join(testDir, categoryMap[category]);
    
    // Рекурсивный поиск .epf файлов
    return this.findEpfFiles(searchDir);
  }

  findEpfFiles(dir) {
    let results = [];
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        results = results.concat(this.findEpfFiles(fullPath));
      } else if (item.endsWith('.epf')) {
        results.push(fullPath);
      }
    }
    
    return results;
  }

  async runSingleTest(testFile) {
    const { connection, user, password } = this.config.testInfobase;
    const logFile = path.join(__dirname, '../../test-results/temp-log.txt');
    
    const command = `
      "C:\\Program Files\\1cv8\\8.3.24\\bin\\1cv8.exe"
      ENTERPRISE
      /F"${connection}"
      /N"${user}"
      ${password ? `/P"${password}"` : ''}
      /Execute"${testFile}"
      /TestClient
      /Out"${logFile}"
      /DumpResult"${logFile}.xml"
    `.replace(/\n/g, ' ').trim();
    
    console.log(`Запуск: ${path.basename(testFile)}`);
    
    return new Promise((resolve, reject) => {
      exec(command, { timeout: this.config.timeout }, (error, stdout, stderr) => {
        const result = this.parseTestResult(logFile, testFile);
        this.results.push(result);
        
        if (error && !this.config.retryOnFailure) {
          reject(error);
        } else if (error && result.retry < this.config.retryOnFailure) {
          result.retry++;
          this.runSingleTest(testFile).then(resolve).catch(reject);
        } else {
          resolve(result);
        }
      });
    });
  }

  parseTestResult(logFile, testFile) {
    if (!fs.existsSync(logFile)) {
      return {
        file: testFile,
        status: 'error',
        error: 'Лог-файл не создан',
        retry: 0
      };
    }
    
    const log = fs.readFileSync(logFile, 'utf-8');
    const passed = (log.match(/\[PASSED\]/g) || []).length;
    const failed = (log.match(/\[FAILED\]/g) || []).length;
    const skipped = (log.match(/\[SKIPPED\]/g) || []).length;
    
    return {
      file: path.basename(testFile),
      status: failed === 0 ? 'success' : 'failed',
      passed,
      failed,
      skipped,
      total: passed + failed + skipped,
      retry: 0
    };
  }

  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ');
    console.log('='.repeat(60));
    
    let totalPassed = 0;
    let totalFailed = 0;
    let totalSkipped = 0;
    
    for (const result of this.results) {
      const icon = result.status === 'success' ? '✓' : '✗';
      console.log(`${icon} ${result.file}: ${result.passed}/${result.total}`);
      
      totalPassed += result.passed;
      totalFailed += result.failed;
      totalSkipped += result.skipped;
    }
    
    console.log('='.repeat(60));
    console.log(`Всего: ${totalPassed + totalFailed + totalSkipped}`);
    console.log(`✓ Успешно: ${totalPassed}`);
    console.log(`✗ Провалено: ${totalFailed}`);
    console.log(`⊘ Пропущено: ${totalSkipped}`);
    console.log('='.repeat(60) + '\n');
  }
}

// Экспорт
module.exports = TestRunner;

// CLI запуск
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};
  
  for (const arg of args) {
    if (arg === '--all') options.category = 'all';
    else if (arg === '--unit') options.category = 'unit';
    else if (arg === '--integration') options.category = 'integration';
    else if (arg.startsWith('--file=')) options.pattern = arg.split('=')[1];
  }
  
  const runner = new TestRunner();
  runner.runTests(options).catch(console.error);
}
```

---

## 3. VS Code Tasks

Файл: `.vscode/tasks.json` (дополнение)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Запустить все тесты",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/test-runner.js",
        "--all"
      ],
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Запустить юнит-тесты",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/test-runner.js",
        "--unit"
      ],
      "group": "test"
    },
    {
      "label": "Запустить интеграционные тесты",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/test-runner.js",
        "--integration"
      ],
      "group": "test"
    },
    {
      "label": "Запустить тесты текущего файла",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/test-runner.js",
        "--file=${file}"
      ],
      "group": "test"
    },
    {
      "label": "Проверить покрытие кода",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/coverage-checker.js"
      ],
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "Запустить дебаг с брейкпоинтами",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/plugins/debug-launcher.js",
        "--file=${file}",
        "--line=${lineNumber}"
      ],
      "group": "build"
    }
  ]
}
```

---

## 4. Генерация тестов через Copilot

### 4.1 Дополнение к copilot-instructions.md

```markdown
## Автоматическая генерация тестов

### Правила создания тестов

1. **Каждая экспортная функция/процедура** → отдельный юнит-тест
2. **Имя теста:** `Тест<ИмяФункции>`
3. **Структура теста (AAA pattern):**

```bsl
Процедура ТестПолучитьОстаток() Экспорт
    // Arrange (Подготовка) - настройка тестовых данных
    Номенклатура = Справочники.Номенклатура.НайтиПоНаименованию("Тестовый товар");
    Склад = Константы.ОсновнойСклад.Получить();
    ОжидаемыйОстаток = 100;
    
    // Act (Действие) - выполнение тестируемой функции
    ФактическийОстаток = РаботаСНоменклатурой.ПолучитьОстаток(Номенклатура, Склад);
    
    // Assert (Проверка) - утверждения
    Ожидаем.Что(ФактическийОстаток, "Остаток должен быть числом").Число();
    Ожидаем.Что(ФактическийОстаток >= 0, "Остаток не может быть отрицательным").Истина();
    Ожидаем.Что(ФактическийОстаток, "Остаток не совпадает").Равно(ОжидаемыйОстаток);
КонецПроцедуры
```

### Workflow генерации тестов

**При создании новой функции:**
1. Copilot автоматически вызывает `@mcp generate_test_template`
2. Создает файл в `/Тесты/Модульные/Тест<ИмяМодуля>.epf`
3. Генерирует тест по шаблону AAA
4. Добавляет комментарий `// @test:generated`

**При изменении существующей функции:**
1. Copilot проверяет наличие теста
2. Предупреждает: "Функция изменена, требуется обновление теста"
3. Предлагает регенерировать тест

### Специальные комментарии (аннотации)

```bsl
// @test:generate - создать тест для этой функции
// @test:skip - не генерировать тест (для служебных функций)
// @test:mock ИмяСервиса - создать мок для внешнего сервиса
// @test:integration - создать интеграционный тест, а не юнит
```

### Примеры генерации

**Запрос:** "Создай функцию ПолучитьЦенуТовара + тесты"

**Copilot выполняет:**
1. `@mcp 1c-metadata get InformationRegister.ЦеныНоменклатуры`
2. Генерирует функцию с правильными полями
3. `@mcp generate_test_template`
4. Создает тест с проверками граничных условий
5. Обновляет спецификацию

### Типы утверждений (Assertions)

```bsl
// Проверка типов
Ожидаем.Что(Значение, "Описание").Число();
Ожидаем.Что(Значение, "Описание").Строка();
Ожидаем.Что(Значение, "Описание").Булево();
Ожидаем.Что(Значение, "Описание").Массив();

// Проверка равенства
Ожидаем.Что(Значение, "Описание").Равно(ОжидаемоеЗначение);
Ожидаем.Что(Значение, "Описание").НеРавно(НежелательноеЗначение);

// Проверка условий
Ожидаем.Что(Условие, "Описание").Истина();
Ожидаем.Что(Условие, "Описание").Ложь();

// Проверка исключений
Ожидаем.Что(ВыполнитьМетод).ВызоветИсключение();
```
```

---

## 5. CI/CD Integration

### 5.1 GitHub Actions Workflow

Файл: `.github/workflows/test-and-debug.yml`

```yaml
name: Tests & Coverage

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: windows-latest
    timeout-minutes: 30
    
    steps:
      - name: Checkout код
        uses: actions/checkout@v3
      
      - name: Установить Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Установить зависимости
        run: npm install
      
      - name: Установить 1С платформу
        run: choco install 1c-enterprise-platform --version=8.3.24
      
      - name: Создать тестовую базу
        run: |
          $dbPath = "${{runner.temp}}\test_db"
          & "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" CREATEINFOBASE File="$dbPath"
          & "C:\Program Files\1cv8\8.3.24\bin\1cv8.exe" DESIGNER /F"$dbPath" /LoadCfg Configuration.xml /Out test-load.log
      
      - name: Запустить юнит-тесты
        run: node .vscode/plugins/test-runner.js --unit
      
      - name: Запустить интеграционные тесты
        run: node .vscode/plugins/test-runner.js --integration
        continue-on-error: true
      
      - name: Проверить покрытие кода
        run: node .vscode/plugins/coverage-checker.js
      
      - name: Загрузить отчет о тестах
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
      
      - name: Опубликовать результаты
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: 1C Test Results
          path: test-results/*.xml
          reporter: java-junit

  coverage-report:
    needs: unit-tests
    runs-on: windows-latest
    
    steps:
      - name: Скачать результаты тестов
        uses: actions/download-artifact@v3
        with:
          name: test-results
      
      - name: Генерация отчета покрытия
        run: node .vscode/plugins/coverage-report-generator.js
      
      - name: Комментарий в PR с покрытием
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const coverage = JSON.parse(fs.readFileSync('test-results/coverage.json'));
            
            const comment = `## 📊 Покрытие кода
            
            | Метрика | Значение |
            |---------|----------|
            | Покрытие строк | ${coverage.lines}% |
            | Покрытие функций | ${coverage.functions}% |
            | Покрытие модулей | ${coverage.modules}% |
            
            ${coverage.lines < 70 ? '⚠️ Покрытие ниже порога 70%' : '✅ Покрытие соответствует требованиям'}
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

---

## 6. Coverage Checker

Файл: `.vscode/plugins/coverage-checker.js`

```javascript
const fs = require('fs');
const path = require('path');

class CoverageChecker {
  constructor() {
    this.config = this.loadConfig();
    this.coverage = {
      lines: { total: 0, covered: 0 },
      functions: { total: 0, covered: 0 },
      modules: { total: 0, covered: 0 }
    };
  }

  loadConfig() {
    const configPath = path.join(__dirname, '../test-config.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }

  async check() {
    console.log('Анализ покрытия кода тестами...\n');
    
    // Парсинг результатов тестов
    this.parseTestResults();
    
    // Расчет покрытия
    const coverage = this.calculateCoverage();
    
    // Сохранение отчета
    this.saveReport(coverage);
    
    // Вывод результатов
    this.printReport(coverage);
    
    // Проверка порога
    if (coverage.lines < this.config.coverage.threshold) {
      console.error(`\n❌ ОШИБКА: Покрытие ${coverage.lines}% ниже порога ${this.config.coverage.threshold}%`);
      process.exit(1);
    } else {
      console.log(`\n✅ Покрытие ${coverage.lines}% соответствует требованиям`);
    }
  }

  parseTestResults() {
    const resultsDir = path.join(__dirname, '../../test-results');
    
    if (!fs.existsSync(resultsDir)) {
      console.error('Нет результатов тестов');
      return;
    }
    
    // Чтение XML отчетов
    const xmlFiles = fs.readdirSync(resultsDir).filter(f => f.endsWith('.xml'));
    
    for (const xmlFile of xmlFiles) {
      const content = fs.readFileSync(path.join(resultsDir, xmlFile), 'utf-8');
      this.parseXmlReport(content);
    }
  }

  parseXmlReport(xml) {
    // Простой парсинг (в реальности использовать xml2js)
    const linesMatch = xml.match(/<coverage lines-covered="(\d+)" lines-valid="(\d+)"/);
    if (linesMatch) {
      this.coverage.lines.covered += parseInt(linesMatch[1]);
      this.coverage.lines.total += parseInt(linesMatch[2]);
    }
  }

  calculateCoverage() {
    return {
      lines: this.calculatePercent(this.coverage.lines),
      functions: this.calculatePercent(this.coverage.functions),
      modules: this.calculatePercent(this.coverage.modules)
    };
  }

  calculatePercent(data) {
    return data.total === 0 ? 0 : Math.round((data.covered / data.total) * 100);
  }

  saveReport(coverage) {
    const reportPath = path.join(__dirname, '../../test-results/coverage.json');
    fs.writeFileSync(reportPath, JSON.stringify(coverage, null, 2));
  }

  printReport(coverage) {
    console.log('┌─────────────────────────────────────┐');
    console.log('│      ОТЧЕТ О ПОКРЫТИИ КОДА         │');
    console.log('├─────────────────────────────────────┤');
    console.log(`│ Покрытие строк:    ${coverage.lines}%`.padEnd(37) + '│');
    console.log(`│ Покрытие функций:  ${coverage.functions}%`.padEnd(37) + '│');
    console.log(`│ Покрытие модулей:  ${coverage.modules}%`.padEnd(37) + '│');
    console.log('└─────────────────────────────────────┘');
  }
}

// Запуск
if (require.main === module) {
  const checker = new CoverageChecker();
  checker.check().catch(console.error);
}

module.exports = CoverageChecker;
```

---

## 7. Интеграция с Copilot - Полный Workflow

### 7.1 Сценарий: Разработка функции с тестами

```
Разработчик: "Создай функцию ПолучитьОстатокТовара в модуле РаботаСНоменклатурой с тестами"

Copilot:
├─ Шаг 1: Проверка метаданных
│  └─ @mcp 1c-metadata get AccumulationRegister.ОстаткиТоваров
│
├─ Шаг 2: Генерация функции
│  └─ Создает: CommonModules/РаботаСНоменклатурой/Module.bsl
│     Асинх Функция ПолучитьОстатокТовара(Номенклатура, Склад) Экспорт
│         // @test:generate
│         Запрос = Новый Запрос;
│         Запрос.Текст = "ВЫБРАТЬ ...";
│         // ...
│     КонецФункции
│
├─ Шаг 3: Генерация теста
│  └─ @mcp generate_test_template
│     Создает: Тесты/Модульные/ТестРаботаСНоменклатурой.epf
│
├─ Шаг 4: Запуск теста
│  └─ @mcp run_unit_tests
│     Результат: ✓ PASSED (0.8s)
│
├─ Шаг 5: Проверка покрытия
│  └─ @mcp get_test_coverage
│     Результат: 85% (выше порога 70%)
│
└─ Шаг 6: Обновление документации
   └─ @mcp spec-updater add-history
      "Добавлена функция ПолучитьОстатокТовара с тестами"
```

### 7.2 Сценарий: Отладка проблемы

```
Разработчик: "Проблема в функции РассчитатьСуммуСоСкидкой, запусти дебаг"

Copilot:
├─ Шаг 1: Установка точки останова
│  └─ @mcp debug_attach → подключение к базе
│     @mcp debug_breakpoint Module.bsl:156
│
├─ Шаг 2: Выполнение до точки останова
│  └─ Триггер: запуск кода до брейкпоинта
│
├─ Шаг 3: Инспекция переменных
│  └─ @mcp debug_vars
│     Переменные:
│     - СуммаДокумента = 1000
│     - ПроцентСкидки = 15
│     - РассчитаннаяСумма = ??? (ошибка здесь)
│
├─ Шаг 4: Вычисление выражения
│  └─ @mcp debug_eval "СуммаДокумента * (1 - ПроцентСкидки / 100)"
│     Результат: 850 (ожидаемо)
│
├─ Шаг 5: Анализ
│  └─ Copilot: "Ошибка: используется ПроцентСкидки напрямую вместо деления на 100"
│
└─ Шаг 6: Исправление + тест
   └─ Исправляет код
      Генерирует регрессионный тест
      Запускает все тесты → ✓ PASSED
```

---

## 8. Установка и настройка

### 8.1 Пошаговая установка

```powershell
# 1. Установка расширений VS Code
code --install-extension 1c-syntax.language-1c-bsl
code --install-extension 1c-syntax.language-1c-bsl-debug
code --install-extension hbenl.vscode-test-explorer
code --install-extension ryanluker.vscode-coverage-gutters

# 2. Установка Node.js зависимостей
npm install --save-dev win32ole node-comconnector xml2js

# 3. Создание структуры
mkdir Тесты\Модульные
mkdir Тесты\Интеграционные
mkdir Тесты\UI
mkdir test-results\coverage
mkdir mcp-tools

# 4. Копирование конфигурационных файлов
# (скопировать все .json и .js файлы из документации)

# 5. Настройка прав для тестовой базы
# Создать пользователя TestRunner с полными правами

# 6. Проверка установки
node .vscode/plugins/test-runner.js --help
```

### 8.2 Проверка работоспособности

```powershell
# Тест MCP подключения
node mcp-tools/debug-bridge.js test-connection

# Запуск тестового теста
node .vscode/plugins/test-runner.js --file=Тесты\Модульные\ПримерТеста.epf

# Проверка отладчика
# (Установить брейкпоинт в VS Code и запустить F5)
```

---

## 9. Контрольный список

- [ ] Установлены все расширения VS Code
- [ ] Создана структура папок для тестов
- [ ] Настроен `.vscode/launch.json`
- [ ] Настроен `.vscode/test-config.json`
- [ ] Настроены tasks.json для запуска тестов
- [ ] Реализован test-runner.js
- [ ] Реализован debug-bridge.js (MCP)
- [ ] Реализован coverage-checker.js
- [ ] Создана тестовая информационная база
- [ ] Настроен CI/CD workflow
- [ ] Обновлен copilot-instructions.md с правилами тестирования
- [ ] Проведен тестовый запуск всех компонентов

---

## 10. Результат

После полной настройки разработчик получает:

✅ **Автоматическую генерацию тестов** через Copilot  
✅ **Отладку прямо из VS Code** с брейкпоинтами  
✅ **Запуск тестов через Tasks** (Ctrl+Shift+B)  
✅ **Отчеты о покрытии кода** в реальном времени  
✅ **CI/CD проверку** на каждый commit  
✅ **Интеграцию с MCP** для работы с 1С метаданными  
✅ **Автообновление документации** после тестов  

---

**Версия документа:** 1.0  
**Последнее обновление:** 20 января 2026 г.  
**Автор:** Система разработки PTM
