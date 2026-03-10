# PowerShell обёртки для работы с 1С COM

## Обзор

Модуль предоставляет надёжный и безопасный способ работы с 1С:Предприятие 8.3.24 из Node.js через PowerShell и COM объекты.

### Компоненты

- **`ps-helpers.js`** — базовая обёртка для запуска PowerShell скриптов
- **`1c-com-wrapper.js`** — удобный интерфейс для работы с COM объектами 1С
- **`debug-bridge.js`** — инструменты для отладки (MCP tools)
- **`index.js`** — сервер MCP с экспортом всех инструментов
- **`config.json`** — конфигурация для подключений к базам
- **`examples.js`** — примеры использования

## Установка и настройка

### 1. Проверка требований

```powershell
# PowerShell версия (требуется 5.1+)
$PSVersionTable.PSVersion

# Политика выполнения (нужна RemoteSigned или выше)
Get-ExecutionPolicy

# Если ограничена:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### 2. Установка зависимостей

```bash
cd mcp-config
npm install xml2js
```

### 3. Настройка конфигурации

Отредактируйте `config.json`:

```json
{
  "connections": {
    "development": {
      "path": "D:\\1C_Bases\\PTM_Development",
      "user": "Admin"
    }
  }
}
```

## Использование

### Пример 1: Проверка подключения

```javascript
const PowerShellHelper = require('./ps-helpers');

const ps = new PowerShellHelper();

// Проверка COM
const com = ps.checkCOM();
console.log('COM доступен:', com.available);

// Подключение к базе
const result = ps.connect1C(
  'D:\\1C_Bases\\PTM_Test',
  'TestRunner'
);
console.log('Подключено:', result.success);
```

### Пример 2: Выполнение 1С кода

```javascript
const COM1CWrapper = require('./1c-com-wrapper');

const com = new COM1CWrapper();
com.init({
  infobase: 'D:\\1C_Bases\\PTM_Test',
  user: 'TestRunner'
});

// Выполнить выражение
const result = com.eval('ТекущаяДата()');
console.log('Дата:', result.value);

// Получить константу
const const1 = com.getConstant('ОсновнойСклад');
console.log('Основной склад:', const1.value);

// Установить константу
com.setConstant('ОсновнойСклад', 'Основной');

com.cleanup();
```

### Пример 3: Отладка с брейкпоинтами

```javascript
const { DebugBridge } = require('./debug-bridge');

const bridge = new DebugBridge();

(async () => {
  // Подключиться
  await bridge.attach('D:\\1C_Bases\\PTM_Test', 'TestRunner');

  // Установить точку останова
  bridge.setBreakpoint('ОбщегоНазначения', 156);

  // Вычислить выражение
  const result = await bridge.evaluateExpression('1 + 2');
  console.log('Результат:', result.value);

  // Получить стек
  const stack = await bridge.getCallStack();
  console.log('Стек вызовов:', stack.stack);

  // Отключиться
  await bridge.detach();
})();
```

### Пример 4: MCP сервер

```javascript
const { MCPServer } = require('./index');

const server = new MCPServer('./config.json');

// Вывести доступные инструменты
server.printTools();

// Вызвать инструмент
server.callTool('test_connection', {
  infobase: 'D:\\1C_Bases\\PTM_Test',
  user: 'TestRunner'
}).then(result => {
  console.log('Результат:', result);
});
```

## MCP инструменты

### Отладка

- **`debug_attach`** — подключиться к 1С базе
- **`debug_set_breakpoint`** — установить точку останова
- **`debug_remove_breakpoint`** — удалить точку останова
- **`debug_get_breakpoints`** — получить список точек останова
- **`debug_eval`** — вычислить выражение
- **`debug_get_stack`** — получить стек вызовов
- **`debug_get_variables`** — получить локальные переменные
- **`debug_continue`** — продолжить выполнение
- **`debug_step_into`** — шаг с входом
- **`debug_step_over`** — шаг с пропуском
- **`debug_get_state`** — получить состояние отладки
- **`debug_detach`** — отключиться

### Подключение

- **`get_com_status`** — проверить статус COM
- **`test_connection`** — проверить подключение к базе
- **`eval_1c_code`** — выполнить 1С код

## API Reference

### PowerShellHelper

```javascript
const ps = new PowerShellHelper();

// Синхронное выполнение
ps.executeSync(scriptContent, options);

// Асинхронное выполнение
await ps.executeAsync(scriptContent, options);

// Проверка COM
ps.checkCOM();

// Подключение к 1С
ps.connect1C(infobase, user, password);

// Выполнение кода
ps.evaluateCode(connection, code);

// Очистка
ps.cleanup();
```

### COM1CWrapper

```javascript
const com = new COM1CWrapper();

// Инициализация
com.init(config);

// Выполнение кода
com.eval(code);

// Вызов процедуры
com.callProcedure(moduleName, procedureName, params);

// Работа с константами
com.getConstant(name);
com.setConstant(name, value);

// Системная информация
com.getCurrentDate();
com.getSystemInfo();
com.getUsersList();

// Очистка
com.cleanup();
```

### DebugBridge

```javascript
const bridge = new DebugBridge();

// Управление подключением
await bridge.attach(infobase, user, password);
await bridge.detach();

// Точки останова
bridge.setBreakpoint(module, line);
bridge.removeBreakpoint(module, line);
bridge.getBreakpoints();

// Отладка
await bridge.evaluateExpression(expr);
await bridge.getCallStack();
await bridge.getLocalVariables();

// Управление выполнением
await bridge.continue();
await bridge.pause();
await bridge.stepInto();
await bridge.stepOver();

// Состояние
await bridge.getState();
```

## Обработка ошибок

Все методы возвращают объект с полями `success` и `error`:

```javascript
const result = com.eval('ТекущаяДата()');

if (result.success) {
  console.log('Успешно:', result.value);
} else {
  console.error('Ошибка:', result.error);
}
```

## Логирование и отладка

Для отладки можно использовать опцию `debug`:

```javascript
const result = ps.executeSync(script, { debug: true });
// Выведет: [DEBUG] Выполняется скрипт: ...
```

## Ограничения

- Требуется Windows и установленная платформа 1С 8.3.24
- COM объект должен быть зарегистрирован (обычно делается автоматически при установке 1С)
- PowerShell 5.1+ обязателен
- Требуется политика выполнения скриптов RemoteSigned или выше

## Интеграция с DBG протоколом

Для полной функциональности отладки (настоящие точки останова, просмотр переменных, стека) требуется интеграция с DBG протоколом 1С. Текущая реализация предоставляет базовую функциональность через COM.

## Производительность

- Синхронные операции блокируют основной поток
- Для фоновых операций используйте асинхронные методы
- PowerShell скрипты кешируются во временной папке и удаляются после выполнения
- Рекомендуется переиспользовать объекты `PowerShellHelper` и `COM1CWrapper`

## Примеры

Запустите примеры:

```bash
node examples.js
```

Или запустите MCP сервер:

```bash
node index.js
```

## Лицензия

Часть проекта PTM

## Поддержка

Документация: `docs/testing-and-debug-setup.md`
