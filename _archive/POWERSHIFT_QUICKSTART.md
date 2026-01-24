# Быстрый старт с PowerShell обёртками

## 📋 Что было создано

```
mcp-config/
├── ps-helpers.js          # Базовая обёртка PowerShell
├── 1c-com-wrapper.js      # Удобный интерфейс для COM
├── debug-bridge.js        # Инструменты отладки (MCP tools)
├── index.js               # MCP сервер
├── config.json            # Конфигурация подключений
├── examples.js            # Примеры использования
├── verify-setup.js        # Проверка окружения
├── README.md              # Подробная документация
└── ps-scripts/            # Папка для PowerShell скриптов
```

## 🚀 Быстрый старт

### 1. Проверка окружения

```bash
cd mcp-config
node verify-setup.js
```

Должно выдать зелёные галочки. Если есть ошибки - смотри README.md

### 2. Запуск примеров

```javascript
// example-basic.js
const PowerShellHelper = require('./mcp-config/ps-helpers');
const COM1CWrapper = require('./mcp-config/1c-com-wrapper');

// Создать экземпляры
const ps = new PowerShellHelper();
const com = new COM1CWrapper();

// Проверить COM
const status = ps.checkCOM();
console.log('COM доступен:', status.available);

// Инициализировать подключение
const success = com.init({
  infobase: 'D:\\1C_Bases\\PTM_Test',
  user: 'TestRunner'
});

if (success) {
  // Выполнить код
  const result = com.eval('ТекущаяДата()');
  console.log('Дата:', result.value);
  
  com.cleanup();
}
```

### 3. Использование в GitHub Copilot

Добавить в `copilot-instructions.md`:

```markdown
## MCP инструменты для отладки

Доступны следующие инструменты через MCP:

### Отладка
- `@mcp debug_attach` — подключиться к 1С
- `@mcp debug_eval` — вычислить выражение
- `@mcp debug_set_breakpoint` — установить точку останова
- `@mcp debug_get_stack` — получить стек вызовов

### Примеры запросов Copilot

"Подключись к тестовой базе и выполни ТекущаяДата()"
↓
Copilot вызовет:
@mcp debug_attach(infobase="D:\\1C_Bases\\PTM_Test", user="TestRunner")
@mcp debug_eval(expression="ТекущаяДата()")

"Установи брейкпоинт в модуле ОбщегоНазначения на строке 156"
↓
Copilot вызовет:
@mcp debug_set_breakpoint(module="ОбщегоНазначения", line=156)
```

## 📊 Архитектура

```
GitHub Copilot (IDE)
        ↓
   MCP Server (index.js)
        ↓
  DebugBridge (debug-bridge.js)
        ↓
 COM1CWrapper (1c-com-wrapper.js)
        ↓
 PowerShellHelper (ps-helpers.js)
        ↓
   PowerShell (Windows native)
        ↓
  V83.COMConnector (1С COM)
        ↓
 1С:Предприятие (База данных)
```

## 🔧 Основные методы

### PowerShellHelper
```javascript
ps.executeSync(script)           // Выполнить скрипт синхронно
ps.executeAsync(script)          // Выполнить асинхронно
ps.checkCOM()                    // Проверить COM
ps.connect1C(path, user, pwd)    // Подключиться к 1С
ps.evaluateCode(conn, code)      // Выполнить 1С код
```

### COM1CWrapper
```javascript
com.init(config)                 // Инициализировать
com.eval(code)                   // Выполнить код
com.callProcedure(module, proc)  // Вызвать процедуру
com.getCurrentDate()             // Текущая дата
com.getConstant(name)            // Получить константу
com.setConstant(name, value)     // Установить константу
com.getUsersList()               // Список пользователей
```

### DebugBridge
```javascript
await bridge.attach(path, user)  // Подключиться
await bridge.evaluateExpression(expr)
await bridge.setBreakpoint(mod, line)
await bridge.getCallStack()
await bridge.stepInto()          // Шаг в функцию
await bridge.stepOver()          // Шаг через функцию
await bridge.continue()          // Продолжить
await bridge.detach()            // Отключиться
```

## 📝 Примеры кода

### Пример 1: Простое выполнение кода

```javascript
const COM1CWrapper = require('./mcp-config/1c-com-wrapper');

const com = new COM1CWrapper();
com.init({
  infobase: 'D:\\1C_Bases\\PTM_Test',
  user: 'TestRunner'
});

// Получить текущую дату
const date = com.getCurrentDate();
console.log('Дата на сервере:', date.value);

// Выполнить сложное выражение
const result = com.eval(`
  Результат = 0;
  Для Каждого Товар Из Справочники.Номенклатура.ВыбратьСтроки() Цикл
    Результат = Результат + 1;
  КонецЦикла;
  Результат
`);
console.log('Количество товаров:', result.value);

com.cleanup();
```

### Пример 2: Отладка с брейкпоинтами

```javascript
const { DebugBridge } = require('./mcp-config/debug-bridge');

const bridge = new DebugBridge();

(async () => {
  // Подключиться к базе
  const attached = await bridge.attach(
    'D:\\1C_Bases\\PTM_Test',
    'TestRunner'
  );
  console.log('Подключено:', attached.status);

  // Установить брейкпоинт
  bridge.setBreakpoint('ОбщегоНазначения', 156);
  console.log('Брейкпоинт установлен');

  // Выполнить выражение
  const result = await bridge.evaluateExpression('СортировкаЗапроса()');
  console.log('Результат:', result);

  // Получить стек вызовов
  const stack = await bridge.getCallStack();
  stack.stack.forEach((frame, i) => {
    console.log(`[${i}] ${frame.module}.${frame.function}:${frame.line}`);
  });

  // Выполнить шаг
  await bridge.stepOver();

  // Отключиться
  await bridge.detach();
})();
```

### Пример 3: MCP сервер

```javascript
const { MCPServer } = require('./mcp-config/index');

const server = new MCPServer('./mcp-config/config.json');

// Вывести все доступные инструменты
server.printTools();

// Вызвать инструмент
server.callTool('debug_attach', {
  infobase: 'D:\\1C_Bases\\PTM_Test',
  user: 'TestRunner'
}).then(result => {
  console.log('Результат подключения:', result);
});
```

## 🐛 Отладка проблем

### Проблема: COM не доступен

```powershell
# Проверить регистрацию COM
Get-ItemProperty "HKLM:\SOFTWARE\Classes\V83.COMConnector" -ErrorAction SilentlyContinue

# Переregister COM
cd "C:\Program Files\1cv8\8.3.24\bin"
regsvr32.exe comcntr.dll
```

### Проблема: PowerShell не выполняет скрипты

```powershell
# Проверить политику
Get-ExecutionPolicy

# Установить правильную политику
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### Проблема: Не может подключиться к базе

```javascript
// Проверить строку подключения
const ps = new PowerShellHelper();
const result = ps.checkCOM();
console.log('COM статус:', result);

// Проверить наличие базы
const connection = ps.connect1C('D:\\1C_Bases\\PTM_Test', 'TestRunner');
console.log('Результат подключения:', connection);
```

## 📚 Дополнительно

- Полная документация: `mcp-config/README.md`
- Примеры использования: `mcp-config/examples.js`
- Проверка системы: `mcp-config/verify-setup.js`

## ✅ Готовый чеклист

- [ ] PowerShell установлен (версия 5.1+)
- [ ] Политика выполнения скриптов установлена
- [ ] 1С платформа 8.3.24 установлена
- [ ] COM объект V83.COMConnector зарегистрирован
- [ ] Информационные базы созданы
- [ ] `mcp-config` папка создана со всеми файлами
- [ ] `npm install` выполнен
- [ ] `node verify-setup.js` прошел успешно
- [ ] Примеры работают

---

**Готово! Система PowerShell обёрток для 1С настроена и готова к использованию.**
