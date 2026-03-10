/**
 * Пример использования PowerShell обёрток для работы с 1С COM
 */

const PowerShellHelper = require('./ps-helpers');
const COM1CWrapper = require('./1c-com-wrapper');
const { DebugBridge } = require('./debug-bridge');

/**
 * Примеры использования PowerShellHelper
 */
async function demonstratePowerShellHelper() {
  console.log('=== PowerShellHelper Примеры ===\n');

  const ps = new PowerShellHelper();

  // Проверка COM
  console.log('1. Проверка наличия COM объекта:');
  const comCheck = ps.checkCOM();
  console.log('   COM доступен:', comCheck.available);
  console.log('   Ошибка:', comCheck.error || 'Нет');

  // Подключение к 1С
  console.log('\n2. Подключение к 1С базе:');
  const connectResult = ps.connect1C(
    'D:\\1C_Bases\\PTM_Test',
    'TestRunner',
    ''
  );
  console.log('   Успешно:', connectResult.success);
  if (connectResult.error) {
    console.log('   Ошибка:', connectResult.error);
  }

  // Выполнение кода
  if (connectResult.success) {
    console.log('\n3. Выполнение 1С кода (ТекущаяДата):');
    const evalResult = ps.evaluateCode(
      { infobase: 'D:\\1C_Bases\\PTM_Test', user: 'TestRunner' },
      'ТекущаяДата()'
    );
    console.log('   Результат:', evalResult.result || evalResult.error);
  }
}

/**
 * Примеры использования COM1CWrapper
 */
async function demonstrateCOM1CWrapper() {
  console.log('\n=== COM1CWrapper Примеры ===\n');

  const com = new COM1CWrapper();

  // Проверка доступности
  console.log('1. Проверка доступности COM:');
  const availability = COM1CWrapper.checkAvailability();
  console.log('   Доступен:', availability.available);

  // Инициализация
  console.log('\n2. Инициализация подключения:');
  const initialized = com.init({
    infobase: 'D:\\1C_Bases\\PTM_Test',
    user: 'TestRunner'
  });
  console.log('   Инициализировано:', initialized);

  if (initialized) {
    // Получение текущей даты
    console.log('\n3. Получение текущей даты:');
    const date = com.getCurrentDate();
    console.log('   Дата:', date.value || date.error);

    // Получение информации о системе
    console.log('\n4. Информация о системе:');
    const sysInfo = com.getSystemInfo();
    console.log('   Результат:', sysInfo.value || sysInfo.error);

    // Получение списка пользователей
    console.log('\n5. Список пользователей ИБ:');
    const users = com.getUsersList();
    console.log('   Пользователи:', users.users || users.error);

    // Вызов процедуры
    console.log('\n6. Вызов процедуры:');
    const result = com.callProcedure('ОбщегоНазначения', 'ТестПроцедура', ['Параметр1']);
    console.log('   Результат:', result.value || result.error);
  }

  com.cleanup();
}

/**
 * Примеры использования DebugBridge
 */
async function demonstrateDebugBridge() {
  console.log('\n=== DebugBridge Примеры ===\n');

  const bridge = new DebugBridge();

  // Подключение
  console.log('1. Подключение для отладки:');
  const attached = await bridge.attach(
    'D:\\1C_Bases\\PTM_Test',
    'TestRunner',
    ''
  );
  console.log('   Статус:', attached.status);
  console.log('   Сообщение:', attached.message);

  if (attached.status === 'attached') {
    // Установка точки останова
    console.log('\n2. Установка точки останова:');
    const bp1 = bridge.setBreakpoint('ОбщегоНазначения', 156);
    const bp2 = bridge.setBreakpoint('РаботаСДокументами', 42);
    console.log('   Точки останова установлены:', bridge.getBreakpoints().length);

    // Вычисление выражения
    console.log('\n3. Вычисление выражения:');
    const evalRes = await bridge.evaluateExpression('1 + 2');
    console.log('   Результат:', evalRes.value || evalRes.error);
    console.log('   Тип:', evalRes.type);

    // Получение стека вызовов
    console.log('\n4. Стек вызовов:');
    const stack = await bridge.getCallStack();
    console.log('   Фреймы:', stack.stack.length);
    stack.stack.forEach((frame, i) => {
      console.log(`   [${i}] ${frame.module}.${frame.function}:${frame.line}`);
    });

    // Состояние отладки
    console.log('\n5. Состояние отладки:');
    const state = await bridge.getState();
    console.log('   Подключено:', state.connected);
    console.log('   Точек останова:', state.breakpoints);
    console.log('   Статус:', state.state);

    // Отключение
    console.log('\n6. Отключение:');
    const detached = await bridge.detach();
    console.log('   Статус:', detached.status);
  }
}

/**
 * Главная функция для запуска примеров
 */
async function main() {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║  PowerShell обёртки для 1С COM - Примеры      ║');
  console.log('╚════════════════════════════════════════════════╝\n');

  try {
    // Раскомментируйте нужные примеры:
    await demonstratePowerShellHelper();
    // await demonstrateCOM1CWrapper();
    // await demonstrateDebugBridge();

    console.log('\n✅ Примеры завершены');
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// Запуск, если файл запущен напрямую
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  demonstratePowerShellHelper,
  demonstrateCOM1CWrapper,
  demonstrateDebugBridge
};
