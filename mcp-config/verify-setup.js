/**
 * Скрипт проверки всех PowerShell обёрток и интеграции
 * Запуск: node verify-setup.js
 */

const PowerShellHelper = require('./ps-helpers');
const COM1CWrapper = require('./1c-com-wrapper');
const { DebugBridge } = require('./debug-bridge');
const { MCPServer } = require('./index');
const fs = require('fs');
const path = require('path');

class SetupVerifier {
  constructor() {
    this.results = [];
    this.passed = 0;
    this.failed = 0;
  }

  /**
   * Запустить все проверки
   */
  async runAll() {
    console.log('╔════════════════════════════════════════════════╗');
    console.log('║    Проверка PowerShell обёрток для 1С        ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    await this.checkPowerShell();
    await this.checkCOM();
    await this.checkHelpers();
    await this.checkWrappers();
    await this.checkDebugBridge();
    await this.checkMCPServer();
    await this.checkConfig();

    this.printSummary();
  }

  /**
   * Проверка PowerShell
   */
  async checkPowerShell() {
    console.log('1️⃣  Проверка PowerShell...');
    
    try {
      const ps = new PowerShellHelper();
      const version = ps.psVersion;

      if (version >= 5) {
        this.pass('PowerShell версия', `v${version}.1+`);
      } else {
        this.fail('PowerShell версия', `v${version} (требуется 5+)`);
      }

      // Проверка временной директории
      if (fs.existsSync(ps.tempDir)) {
        this.pass('Временная директория', ps.tempDir);
      } else {
        this.fail('Временная директория', 'Не доступна');
      }
    } catch (error) {
      this.fail('PowerShell инициализация', error.message);
    }
  }

  /**
   * Проверка COM
   */
  async checkCOM() {
    console.log('\n2️⃣  Проверка COM объекта V83.COMConnector...');

    try {
      const ps = new PowerShellHelper();
      const comStatus = ps.checkCOM();

      if (comStatus.available) {
        this.pass('COM V83.COMConnector', 'Доступен');
      } else {
        this.fail('COM V83.COMConnector', comStatus.error || 'Не зарегистрирован');
      }
    } catch (error) {
      this.fail('COM проверка', error.message);
    }
  }

  /**
   * Проверка помощников
   */
  async checkHelpers() {
    console.log('\n3️⃣  Проверка PowerShellHelper методов...');

    try {
      const ps = new PowerShellHelper();

      // Проверка синхронного выполнения
      const result = ps.executeSync('Write-Host "test"');
      if (result.success && result.output.includes('test')) {
        this.pass('PowerShellHelper.executeSync()', 'Работает');
      } else {
        this.fail('PowerShellHelper.executeSync()', result.error);
      }

      // Проверка асинхронного выполнения
      const asyncResult = await ps.executeAsync('Write-Host "async-test"');
      if (asyncResult.success && asyncResult.output.includes('async-test')) {
        this.pass('PowerShellHelper.executeAsync()', 'Работает');
      } else {
        this.fail('PowerShellHelper.executeAsync()', asyncResult.error);
      }
    } catch (error) {
      this.fail('PowerShellHelper методы', error.message);
    }
  }

  /**
   * Проверка обёрток
   */
  async checkWrappers() {
    console.log('\n4️⃣  Проверка COM1CWrapper...');

    try {
      const com = new COM1CWrapper();
      
      // Проверка доступности
      const availability = COM1CWrapper.checkAvailability();
      if (availability.available) {
        this.pass('COM1CWrapper инициализация', 'ОК');
      } else {
        this.fail('COM1CWrapper инициализация', availability.error);
      }

      // Проверка методов (без реального подключения)
      if (typeof com.init === 'function' &&
          typeof com.eval === 'function' &&
          typeof com.callProcedure === 'function') {
        this.pass('COM1CWrapper методы', 'Все доступны');
      } else {
        this.fail('COM1CWrapper методы', 'Некоторые отсутствуют');
      }
    } catch (error) {
      this.fail('COM1CWrapper', error.message);
    }
  }

  /**
   * Проверка DebugBridge
   */
  async checkDebugBridge() {
    console.log('\n5️⃣  Проверка DebugBridge...');

    try {
      const bridge = new DebugBridge();

      // Проверка методов
      const methods = [
        'attach', 'detach', 'setBreakpoint', 'removeBreakpoint',
        'getBreakpoints', 'evaluateExpression', 'getCallStack',
        'getLocalVariables', 'continue', 'pause', 'stepInto',
        'stepOver', 'getState'
      ];

      const missingMethods = [];
      for (const method of methods) {
        if (typeof bridge[method] !== 'function') {
          missingMethods.push(method);
        }
      }

      if (missingMethods.length === 0) {
        this.pass('DebugBridge методы', `Все ${methods.length} методов`);
      } else {
        this.fail('DebugBridge методы', `Отсутствуют: ${missingMethods.join(', ')}`);
      }

      // Проверка состояния
      const state = await bridge.getState();
      if (state.connected === false && state.state === 'detached') {
        this.pass('DebugBridge состояние', 'Корректно');
      } else {
        this.fail('DebugBridge состояние', 'Некорректное состояние');
      }
    } catch (error) {
      this.fail('DebugBridge', error.message);
    }
  }

  /**
   * Проверка MCP сервера
   */
  async checkMCPServer() {
    console.log('\n6️⃣  Проверка MCP сервера...');

    try {
      const server = new MCPServer('./config.json');

      // Проверка инструментов
      const tools = server.getTools();
      if (tools.length > 0) {
        this.pass('MCP инструменты', `${tools.length} инструментов`);
      } else {
        this.fail('MCP инструменты', 'Не найдены');
      }

      // Проверка функций
      if (typeof server.callTool === 'function') {
        this.pass('MCPServer.callTool()', 'Доступна');
      } else {
        this.fail('MCPServer.callTool()', 'Не доступна');
      }
    } catch (error) {
      this.fail('MCP сервер', error.message);
    }
  }

  /**
   * Проверка конфигурации
   */
  async checkConfig() {
    console.log('\n7️⃣  Проверка конфигурации...');

    try {
      const configPath = path.resolve('./config.json');
      
      if (fs.existsSync(configPath)) {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        
        if (config.connections && Object.keys(config.connections).length > 0) {
          const connCount = Object.keys(config.connections).length;
          this.pass('config.json', `${connCount} подключений`);
        } else {
          this.fail('config.json', 'Подключения не настроены');
        }

        if (config.powerShell) {
          this.pass('PowerShell конфиг', 'Настроен');
        } else {
          this.fail('PowerShell конфиг', 'Не настроен');
        }
      } else {
        this.fail('config.json', 'Файл не найден');
      }
    } catch (error) {
      this.fail('Конфигурация', error.message);
    }
  }

  /**
   * Записать успешный результат
   */
  pass(name, detail) {
    this.passed++;
    this.results.push({ status: '✅', name, detail });
    console.log(`   ✅ ${name}: ${detail}`);
  }

  /**
   * Записать ошибку
   */
  fail(name, detail) {
    this.failed++;
    this.results.push({ status: '❌', name, detail });
    console.log(`   ❌ ${name}: ${detail}`);
  }

  /**
   * Вывести сводку
   */
  printSummary() {
    console.log('\n╔════════════════════════════════════════════════╗');
    console.log('║              СВОДКА ПРОВЕРКИ                 ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    console.log(`✅ Прошли: ${this.passed}`);
    console.log(`❌ Ошибок: ${this.failed}`);
    console.log(`📊 Всего: ${this.passed + this.failed}`);

    const percentage = ((this.passed / (this.passed + this.failed)) * 100).toFixed(0);
    console.log(`\n🎯 Готовность: ${percentage}%\n`);

    if (this.failed === 0) {
      console.log('✨ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Система готова к использованию.\n');
      return true;
    } else {
      console.log('⚠️  Требуется исправление некоторых проблем.\n');
      return false;
    }
  }
}

// Запуск
if (require.main === module) {
  const verifier = new SetupVerifier();
  verifier.runAll().catch(console.error);
}

module.exports = SetupVerifier;
