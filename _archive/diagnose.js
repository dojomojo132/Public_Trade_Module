/**
 * Диагностика подключения к 1С
 */

const PowerShellHelper = require('./mcp-config/ps-helpers');

console.log('🔍 ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К 1С\n');

const ps = new PowerShellHelper();

// 1. Проверка PowerShell
console.log('1️⃣ PowerShell версия:', ps.psVersion);

// 2. Проверка COM
console.log('2️⃣ Проверка COM объекта...');
const com = ps.checkCOM();
console.log('   COM доступен:', com.available);
if (!com.available) {
  console.error('   Ошибка:', com.error);
  process.exit(1);
}

// 3. Проверка базы
console.log('\n3️⃣ Проверка информационной базы...');
const infobase = 'D:\\Confiq\\Public Trade Module';
console.log('   Путь:', infobase);

const fs = require('fs');
const path = require('path');

const dbFile = path.join(infobase, '1Cv8.1CD');
if (fs.existsSync(dbFile)) {
  console.log('   ✅ Файл базы найден:', dbFile);
} else {
  console.error('   ❌ Файл базы не найден:', dbFile);
  console.log('\n💡 Проверьте путь к базе данных');
  process.exit(1);
}

// 4. Попытка подключения с разными пользователями
console.log('\n4️⃣ Попытки подключения...\n');

const users = ['', 'Admin', 'Администратор'];

for (const user of users) {
  console.log(`   Попытка: пользователь = "${user || '(пустой)'}"`);
  
  const result = ps.connect1C(infobase, user, '');
  
  if (result.success) {
    console.log(`   ✅ УСПЕХ! Используйте: user = "${user}"\n`);
    
    // Проверим что можем выполнить код
    const testCode = ps.evaluateCode(
      { infobase, user, password: '' },
      'ТекущаяДата()'
    );
    
    if (testCode.success) {
      console.log('   ✅ Выполнение кода работает');
      console.log('   Результат:', testCode.result);
    }
    
    process.exit(0);
  } else {
    console.log('   ❌ Ошибка:', result.error);
  }
}

console.log('\n❌ Не удалось подключиться ни с одним пользователем\n');
console.log('💡 Возможные причины:');
console.log('   1. База требует аутентификации');
console.log('   2. База повреждена');
console.log('   3. Версия платформы несовместима');
console.log('   4. COM объект работает некорректно\n');

ps.cleanup();
