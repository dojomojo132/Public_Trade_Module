/**
 * COM Wrapper для 1С через PowerShell
 * Предоставляет удобный интерфейс для работы с 1С COM объектами
 */

const PowerShellHelper = require('./ps-helpers');

class COM1CWrapper {
  constructor() {
    this.ps = new PowerShellHelper();
    this.connection = null;
  }

  /**
   * Инициализация подключения
   * @param {object} config - {infobase, user, password}
   * @returns {boolean}
   */
  init(config) {
    const result = this.ps.connect1C(config.infobase, config.user, config.password || '');
    
    if (result.success) {
      this.connection = config;
      return true;
    } else {
      console.error('Ошибка подключения:', result.error);
      return false;
    }
  }

  /**
   * Проверка доступности COM
   * @returns {object}
   */
  static checkAvailability() {
    const ps = new PowerShellHelper();
    return ps.checkCOM();
  }

  /**
   * Выполнить 1С код
   * @param {string} code - 1С выражение
   * @returns {object} {success, value, error}
   */
  eval(code) {
    if (!this.connection) {
      return {
        success: false,
        value: null,
        error: 'Подключение не инициализировано'
      };
    }

    return this.ps.evaluateCode(this.connection, code);
  }

  /**
   * Вызвать процедуру
   * @param {string} moduleName - Имя модуля (ОбщегоНазначения)
   * @param {string} procedureName - Имя процедуры
   * @param {array} params - Параметры
   * @returns {object}
   */
  callProcedure(moduleName, procedureName, params = []) {
    if (!this.connection) {
      return {
        success: false,
        value: null,
        error: 'Подключение не инициализировано'
      };
    }

    // Строим вызов
    const paramStr = params.map(p => {
      if (typeof p === 'string') {
        return `"${p}"`;
      } else if (typeof p === 'number') {
        return p.toString();
      } else {
        return p.toString();
      }
    }).join(', ');

    const code = `${moduleName}.${procedureName}(${paramStr})`;
    
    return this.ps.evaluateCode(this.connection, code);
  }

  /**
   * Получить значение константы
   * @param {string} constantName - Имя константы
   * @returns {object}
   */
  getConstant(constantName) {
    const code = `Константы.${constantName}.Получить()`;
    return this.eval(code);
  }

  /**
   * Установить значение константы
   * @param {string} constantName - Имя константы
   * @param {*} value - Значение
   * @returns {object}
   */
  setConstant(constantName, value) {
    let valueStr;
    if (typeof value === 'string') {
      valueStr = `"${value}"`;
    } else if (typeof value === 'boolean') {
      valueStr = value ? 'Истина' : 'Ложь';
    } else {
      valueStr = value.toString();
    }

    const code = `Константы.${constantName}.Установить(${valueStr})`;
    return this.eval(code);
  }

  /**
   * Получить текущее значение времени на сервере 1С
   * @returns {object}
   */
  getCurrentDate() {
    return this.eval('ТекущаяДата()');
  }

  /**
   * Получить информацию о системе
   * @returns {object}
   */
  getSystemInfo() {
    const code = `
    НазваниеСистемы = СистемноеИмя();
    ВерсияПлатформы = КонфигурацияПрограммы.ВерсияПлатформы;
    ВерсияКонфигурации = КонфигурацияПрограммы.ВерсияПрограммы;
    "Система: " + НазваниеСистемы + "; Платформа: " + ВерсияПлатформы + "; Конфиг: " + ВерсияКонфигурации
    `;

    return this.eval(code);
  }

  /**
   * Получить список пользователей ИБ
   * @returns {object}
   */
  getUsersList() {
    const code = `
    Результат = Новый Массив;
    Для каждого Пользователь Из ПользователиИнформационнойБазы.ПолучитьПользователей() Цикл
        Результат.Добавить(Пользователь.Имя);
    КонецЦикла;
    СтрСоединить(Результат, ",")
    `;

    const result = this.eval(code);
    if (result.success) {
      return {
        success: true,
        users: result.result.split(',').map(u => u.trim()),
        error: null
      };
    }
    return {
      success: false,
      users: [],
      error: result.error
    };
  }

  /**
   * Экспортировать объект справочника
   * @param {string} catalogName - Имя справочника
   * @param {string} format - xml, json (xml по умолчанию)
   * @returns {object}
   */
  exportCatalog(catalogName, format = 'xml') {
    if (format === 'xml') {
      const code = `
      Справочник = Справочники.${catalogName}.Выбрать();
      // Экспорт в XML
      Результат = Справочник.ВыгрузитьВXml();
      `;
      return this.eval(code);
    }
    
    return {
      success: false,
      value: null,
      error: 'Формат не поддерживается'
    };
  }

  /**
   * Очистить ресурсы
   */
  cleanup() {
    this.ps.cleanup();
  }
}

module.exports = COM1CWrapper;
