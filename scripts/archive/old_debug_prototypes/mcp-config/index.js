/**
 * Инициализация MCP сервера с поддержкой отладки
 * Экспортирует инструменты для работы с 1С
 */

const { createMCPTools } = require('./debug-bridge');
const COM1CWrapper = require('./1c-com-wrapper');
const PowerShellHelper = require('./ps-helpers');
const fs = require('fs');
const path = require('path');

class MCPServer {
  constructor(configPath = './config.json') {
    this.config = this.loadConfig(configPath);
    this.tools = [];
    this.initializeTools();
  }

  loadConfig(configPath) {
    try {
      const fullPath = path.resolve(configPath);
      if (fs.existsSync(fullPath)) {
        return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
      }
    } catch (e) {
      console.warn('Ошибка загрузки конфигурации:', e.message);
    }
    return {};
  }

  /**
   * Инициализация всех MCP инструментов
   */
  initializeTools() {
    // Debug tools
    const debugTools = createMCPTools();
    this.tools.push(...debugTools);

    // Metadata tools
    this.tools.push(
      {
        name: 'get_com_status',
        description: 'Получить статус COM объекта V83.COMConnector',
        handler: () => {
          const ps = new PowerShellHelper();
          return ps.checkCOM();
        }
      },
      {
        name: 'test_connection',
        description: 'Проверить подключение к 1С базе',
        inputSchema: {
          type: 'object',
          properties: {
            infobase: { type: 'string' },
            user: { type: 'string' },
            password: { type: 'string' }
          },
          required: ['infobase', 'user']
        },
        handler: (params) => {
          const ps = new PowerShellHelper();
          return ps.connect1C(params.infobase, params.user, params.password);
        }
      },
      {
        name: 'eval_1c_code',
        description: 'Выполнить 1С код в базе',
        inputSchema: {
          type: 'object',
          properties: {
            infobase: { type: 'string' },
            user: { type: 'string' },
            password: { type: 'string' },
            code: { type: 'string' }
          },
          required: ['infobase', 'user', 'code']
        },
        handler: (params) => {
          const ps = new PowerShellHelper();
          return ps.evaluateCode(
            { infobase: params.infobase, user: params.user, password: params.password },
            params.code
          );
        }
      }
    );
  }

  /**
   * Получить все доступные инструменты
   */
  getTools() {
    return this.tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema || { type: 'object', properties: {} }
    }));
  }

  /**
   * Вызвать инструмент по имени
   */
  async callTool(toolName, params) {
    const tool = this.tools.find(t => t.name === toolName);
    
    if (!tool) {
      throw new Error(`Инструмент ${toolName} не найден`);
    }

    if (typeof tool.handler === 'function') {
      return await Promise.resolve(tool.handler(params));
    }

    throw new Error(`Инструмент ${toolName} не имеет обработчика`);
  }

  /**
   * Список доступных инструментов для вывода в консоль
   */
  printTools() {
    console.log('\n╔════════════════════════════════════════════════╗');
    console.log('║         Доступные MCP инструменты             ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    this.tools.forEach((tool, index) => {
      console.log(`${index + 1}. ${tool.name}`);
      console.log(`   Описание: ${tool.description}`);
      if (tool.inputSchema && tool.inputSchema.properties) {
        const props = Object.keys(tool.inputSchema.properties);
        if (props.length > 0) {
          console.log(`   Параметры: ${props.join(', ')}`);
        }
      }
      console.log();
    });

    console.log(`Всего инструментов: ${this.tools.length}`);
  }
}

// Экспорт
module.exports = { MCPServer };

// Запуск как самостоятельное приложение
if (require.main === module) {
  const server = new MCPServer('./config.json');
  server.printTools();

  // Пример вызова инструмента
  console.log('\n═══════════════════════════════════════════════');
  console.log('Пример вызова инструмента:');
  console.log('═══════════════════════════════════════════════\n');

  server.callTool('get_com_status', {})
    .then(result => {
      console.log('Результат get_com_status:');
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(error => {
      console.error('Ошибка:', error.message);
    });
}
