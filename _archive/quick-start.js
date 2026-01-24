#!/usr/bin/env node
/**
 * Быстрый инициализатор MCP системы
 * 
 * Использование:
 *   node quick-start.js verify   - Проверить систему
 *   node quick-start.js examples - Запустить примеры
 *   node quick-start.js server   - Запустить MCP сервер
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class QuickStart {
  constructor() {
    this.rootDir = __dirname;
    this.mcpDir = path.join(this.rootDir, 'mcp-config');
  }

  /**
   * Проверить установку
   */
  verify() {
    console.log('\n╔════════════════════════════════════════════════╗');
    console.log('║        Проверка PowerShell обёрток           ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    try {
      const verifyPath = path.join(this.mcpDir, 'verify-setup.js');
      if (!fs.existsSync(verifyPath)) {
        console.error('❌ Файл verify-setup.js не найден');
        return false;
      }

      console.log('📋 Запуск проверки системы...\n');
      execSync(`node "${verifyPath}"`, { stdio: 'inherit' });
      return true;
    } catch (error) {
      console.error('\n❌ Ошибка при проверке:', error.message);
      return false;
    }
  }

  /**
   * Запустить примеры
   */
  examples() {
    console.log('\n╔════════════════════════════════════════════════╗');
    console.log('║       Примеры использования PowerShell       ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    try {
      const examplesPath = path.join(this.mcpDir, 'examples.js');
      if (!fs.existsSync(examplesPath)) {
        console.error('❌ Файл examples.js не найден');
        return false;
      }

      console.log('▶️  Запуск примеров...\n');
      execSync(`node "${examplesPath}"`, { stdio: 'inherit' });
      return true;
    } catch (error) {
      console.error('\n❌ Ошибка при запуске примеров:', error.message);
      return false;
    }
  }

  /**
   * Запустить MCP сервер
   */
  server() {
    console.log('\n╔════════════════════════════════════════════════╗');
    console.log('║        MCP Debug Server для 1С               ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    try {
      const serverPath = path.join(this.mcpDir, 'index.js');
      if (!fs.existsSync(serverPath)) {
        console.error('❌ Файл index.js не найден');
        return false;
      }

      console.log('🚀 Запуск MCP сервера...');
      console.log('📡 Доступные инструменты:\n');
      execSync(`node "${serverPath}"`, { stdio: 'inherit' });
      return true;
    } catch (error) {
      console.error('\n❌ Ошибка при запуске сервера:', error.message);
      return false;
    }
  }

  /**
   * Показать справку
   */
  help() {
    console.log(`
╔════════════════════════════════════════════════╗
║   PowerShell обёртки для 1С - Быстрый старт   ║
╚════════════════════════════════════════════════╝

ИСПОЛЬЗОВАНИЕ:
  node quick-start.js [команда]

КОМАНДЫ:

  verify     ✅ Проверить окружение и готовность системы
             └─ Запустит 7 проверок и покажет статус

  examples   ▶️  Запустить примеры использования
             └─ Покажет как работают все компоненты

  server     🚀 Запустить MCP сервер
             └─ Выведет доступные инструменты

  help       ℹ️  Показать эту справку

ПРИМЕРЫ:

  # Проверить, что система готова
  node quick-start.js verify

  # Увидеть примеры кода
  node quick-start.js examples

  # Запустить сервер для Copilot
  node quick-start.js server

ДОКУМЕНТАЦИЯ:

  • mcp-config/README.md              - Полная документация API
  • POWERSHIFT_QUICKSTART.md          - Быстрый старт
  • СТАТУС_РЕАЛИЗАЦИИ.md             - Что реализовано
  • mcp-config/РЕАЛИЗАЦИЯ.md         - Архитектура

БЫСТРЫЕ КОМАНДЫ:

  # Все сразу
  npm install && node quick-start.js verify && node quick-start.js examples

  # Интеграция с Copilot
  # Обновить .github/copilot-instructions.md с примерами MCP

  # Запустить в Node
  node -e "require('./mcp-config/1c-com-wrapper')"

ПОДДЕРЖКА:

  Если возникают проблемы:
  1. Проверь что установлены: PowerShell 5.1+, Node.js 18+, 1С 8.3.24
  2. Запусти: node quick-start.js verify
  3. Смотри ошибки и используй README.md
`);
  }

  /**
   * Главная функция
   */
  run(command = 'help') {
    const cmd = (command || 'help').toLowerCase().trim();

    switch (cmd) {
      case 'verify':
        return this.verify() ? 0 : 1;
      case 'examples':
        return this.examples() ? 0 : 1;
      case 'server':
        return this.server() ? 0 : 1;
      case 'help':
      case '--help':
      case '-h':
        this.help();
        return 0;
      default:
        console.error(`\n❌ Неизвестная команда: ${cmd}`);
        console.log('   Используй: node quick-start.js help\n');
        return 1;
    }
  }
}

// Запуск
if (require.main === module) {
  const quickStart = new QuickStart();
  const command = process.argv[2];
  const exitCode = quickStart.run(command);
  process.exit(exitCode);
}

module.exports = QuickStart;
