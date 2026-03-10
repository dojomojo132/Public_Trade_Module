/**
 * PowerShell Helper для работы с COM объектами 1С
 * Запускает PowerShell скрипты и возвращает результаты
 */

const { exec, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

class PowerShellHelper {
  constructor() {
    this.psVersion = this.checkPowerShellVersion();
    this.tempDir = path.join(os.tmpdir(), 'ptm-ps-scripts');
    this.ensureTempDir();
  }

  /**
   * Проверка версии PowerShell
   */
  checkPowerShellVersion() {
    try {
      const version = execSync('powershell -NoProfile -Command "$PSVersionTable.PSVersion.Major"', 
        { encoding: 'utf-8' }).trim();
      return parseInt(version);
    } catch (e) {
      throw new Error('PowerShell не найден или не работает');
    }
  }

  /**
   * Проверка наличия tmp директории
   */
  ensureTempDir() {
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  /**
   * Выполнить PowerShell скрипт синхронно
   * @param {string} scriptContent - Содержимое скрипта
   * @param {object} options - Опции (timeout, encoding)
   * @returns {object} { success, output, error }
   */
  executeSync(scriptContent, options = {}) {
    const {
      timeout = 30000,
      encoding = 'utf-8',
      debug = false
    } = options;

    const scriptFile = path.join(this.tempDir, `script-${Date.now()}.ps1`);
    
    try {
      // Сохраняем скрипт
      fs.writeFileSync(scriptFile, scriptContent, 'utf-8');

      if (debug) {
        console.log(`[DEBUG] Выполняется скрипт: ${scriptFile}`);
      }

      // Выполняем скрипт
      const cmd = `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptFile}"`;
      const output = execSync(cmd, {
        timeout,
        encoding,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      return {
        success: true,
        output: output.trim(),
        error: null
      };
    } catch (error) {
      return {
        success: false,
        output: error.stdout ? error.stdout.toString().trim() : '',
        error: error.stderr ? error.stderr.toString().trim() : error.message
      };
    } finally {
      // Удаляем временный файл
      if (fs.existsSync(scriptFile)) {
        fs.unlinkSync(scriptFile);
      }
    }
  }

  /**
   * Выполнить PowerShell скрипт асинхронно
   * @param {string} scriptContent - Содержимое скрипта
   * @param {object} options - Опции
   * @returns {Promise<object>}
   */
  executeAsync(scriptContent, options = {}) {
    return new Promise((resolve) => {
      const {
        timeout = 30000,
        encoding = 'utf-8',
        debug = false
      } = options;

      const scriptFile = path.join(this.tempDir, `script-${Date.now()}.ps1`);
      
      try {
        // Сохраняем скрипт
        fs.writeFileSync(scriptFile, scriptContent, 'utf-8');

        if (debug) {
          console.log(`[DEBUG] Выполняется скрипт: ${scriptFile}`);
        }

        // Выполняем скрипт асинхронно
        const cmd = `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptFile}"`;
        const child = exec(cmd, { timeout, encoding }, (error, stdout, stderr) => {
          // Удаляем временный файл
          if (fs.existsSync(scriptFile)) {
            fs.unlinkSync(scriptFile);
          }

          if (error) {
            resolve({
              success: false,
              output: stdout || '',
              error: stderr || error.message
            });
          } else {
            resolve({
              success: true,
              output: stdout.trim(),
              error: null
            });
          }
        });
      } catch (error) {
        if (fs.existsSync(scriptFile)) {
          fs.unlinkSync(scriptFile);
        }
        
        resolve({
          success: false,
          output: '',
          error: error.message
        });
      }
    });
  }

  /**
   * Подключение к 1С базе
   * @param {string} infobase - Путь или строка подключения
   * @param {string} user - Пользователь
   * @param {string} password - Пароль (опционально)
   * @returns {object} { success, connection, error }
   */
  connect1C(infobase, user, password = '') {
    const psScript = `
$ErrorActionPreference = "Stop"
try {
    [System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.InteropServices") > $null
    $v83 = New-Object -ComObject "V83.COMConnector"
    
    if ($null -eq $v83) {
        throw "COM объект V83.COMConnector не доступен"
    }
    
    $connStr = 'File="${infobase}";Usr="${user}";'
    if ("${password}" -ne "") {
        $connStr += 'Pwd="${password}";'
    }
    
    $conn = $v83.Connect($connStr)
    
    if ($null -eq $conn) {
        throw "Не удалось подключиться к базе"
    }
    
    Write-Host "SUCCESS"
} catch {
    Write-Host "ERROR: \$(\$_.Exception.Message)"
}
    `;

    const result = this.executeSync(psScript.trim());
    
    if (result.success && result.output.includes('SUCCESS')) {
      return {
        success: true,
        connection: {
          infobase,
          user,
          connected: true
        },
        error: null
      };
    } else {
      return {
        success: false,
        connection: null,
        error: result.error || result.output
      };
    }
  }

  /**
   * Проверка наличия COM объекта
   * @returns {object} { available, version, error }
   */
  checkCOM() {
    const psScript = `
$ErrorActionPreference = "SilentlyContinue"
try {
    $v83 = New-Object -ComObject "V83.COMConnector"
    if ($null -ne $v83) {
        Write-Host "AVAILABLE"
    } else {
        Write-Host "UNAVAILABLE"
    }
} catch {
    Write-Host "UNAVAILABLE"
}
    `;

    const result = this.executeSync(psScript.trim());
    const available = result.success && result.output.includes('AVAILABLE');

    return {
      available,
      version: available ? '8.3.24' : null,
      error: available ? null : 'COM объект V83.COMConnector не зарегистрирован'
    };
  }

  /**
   * Выполнить код в контексте 1С базы
   * @param {object} connection - Параметры подключения {infobase, user, password}
   * @param {string} code - 1С код для выполнения
   * @returns {object} { success, result, error }
   */
  evaluateCode(connection, code) {
    const { infobase, user, password = '' } = connection;
    
    const psScript = `
$ErrorActionPreference = "Stop"
try {
    $v83 = New-Object -ComObject "V83.COMConnector"
    $connStr = 'File="${infobase}";Usr="${user}";'
    if ("${password}" -ne "") {
        $connStr += 'Pwd="${password}";'
    }
    $conn = $v83.Connect($connStr)
    
    $result = $conn.Eval("${code}")
    Write-Host "SUCCESS"
    Write-Host $result
} catch {
    Write-Host "ERROR"
    Write-Host \$_.Exception.Message
}
    `;

    const result = this.executeSync(psScript.trim());
    
    if (result.success) {
      const lines = result.output.split('\n');
      if (lines[0] === 'SUCCESS') {
        return {
          success: true,
          result: lines.slice(1).join('\n'),
          error: null
        };
      }
    }
    
    return {
      success: false,
      result: null,
      error: result.error || result.output
    };
  }

  /**
   * Получить список объектов метаданных
   * @param {object} connection - Параметры подключения
   * @param {string} objectType - Тип объекта (Catalogs, Documents и т.д.)
   * @returns {object} { success, objects, error }
   */
  getMetadataObjects(connection, objectType = 'All') {
    const { infobase, user, password = '' } = connection;
    
    const psScript = `
$ErrorActionPreference = "Stop"
try {
    $v83 = New-Object -ComObject "V83.COMConnector"
    $connStr = 'File="${infobase}";Usr="${user}";'
    if ("${password}" -ne "") {
        $connStr += 'Pwd="${password}";'
    }
    $conn = $v83.Connect($connStr)
    
    # Получаем метаданные
    $metadata = $conn.Metadata()
    
    # Формируем список
    $objects = @()
    
    if ("${objectType}" -eq "All" -or "${objectType}" -eq "Catalogs") {
        foreach ($cat in $metadata.Catalogs) {
            $objects += @{Type="Catalog"; Name=$cat.Name; FullName=$cat.FullName}
        }
    }
    
    # Конвертируем в JSON
    $json = ConvertTo-Json $objects
    Write-Host $json
} catch {
    Write-Host "ERROR"
    Write-Host \$_.Exception.Message
}
    `;

    const result = this.executeSync(psScript.trim());
    
    if (result.success && !result.output.includes('ERROR')) {
      try {
        const objects = JSON.parse(result.output);
        return {
          success: true,
          objects,
          error: null
        };
      } catch (e) {
        return {
          success: false,
          objects: [],
          error: 'Ошибка парсинга результата'
        };
      }
    }
    
    return {
      success: false,
      objects: [],
      error: result.error || result.output
    };
  }

  /**
   * Получить структуру объекта метаданных
   * @param {object} connection - Параметры подключения
   * @param {string} objectName - Имя объекта
   * @returns {object} { success, structure, error }
   */
  getObjectStructure(connection, objectName) {
    const { infobase, user, password = '' } = connection;
    
    const psScript = `
$ErrorActionPreference = "Stop"
try {
    $v83 = New-Object -ComObject "V83.COMConnector"
    $connStr = 'File="${infobase}";Usr="${user}";'
    if ("${password}" -ne "") {
        $connStr += 'Pwd="${password}";'
    }
    $conn = $v83.Connect($connStr)
    
    # Получаем объект метаданных
    $metadata = $conn.Metadata()
    $obj = $metadata.FindByName("${objectName}")
    
    if ($null -eq $obj) {
        Write-Host "ERROR: Объект не найден"
        return
    }
    
    # Формируем структуру
    $structure = @{
        Name = $obj.Name
        FullName = $obj.FullName
        Attributes = @()
    }
    
    # Атрибуты
    if ($null -ne $obj.Attributes) {
        foreach ($attr in $obj.Attributes) {
            $structure.Attributes += @{
                Name = $attr.Name
                Type = $attr.Type
                Required = $attr.Required
            }
        }
    }
    
    $json = ConvertTo-Json $structure
    Write-Host $json
} catch {
    Write-Host "ERROR"
    Write-Host \$_.Exception.Message
}
    `;

    const result = this.executeSync(psScript.trim());
    
    if (result.success && !result.output.includes('ERROR')) {
      try {
        const structure = JSON.parse(result.output);
        return {
          success: true,
          structure,
          error: null
        };
      } catch (e) {
        return {
          success: false,
          structure: null,
          error: 'Ошибка парсинга результата'
        };
      }
    }
    
    return {
      success: false,
      structure: null,
      error: result.error || result.output
    };
  }

  /**
   * Очистить временные файлы
   */
  cleanup() {
    try {
      if (fs.existsSync(this.tempDir)) {
        const files = fs.readdirSync(this.tempDir);
        for (const file of files) {
          fs.unlinkSync(path.join(this.tempDir, file));
        }
      }
    } catch (e) {
      console.error('Ошибка при очистке временных файлов:', e.message);
    }
  }
}

module.exports = PowerShellHelper;
