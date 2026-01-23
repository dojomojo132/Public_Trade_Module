// =============================================================================
// PTM Scanner Emulator - Renderer Process
// =============================================================================

const { ipcRenderer } = require('electron');

const barcodeInput = document.getElementById('barcode-input');
const historyList = document.getElementById('history-list');
const statusDiv = document.getElementById('status');

// История сканирований
let history = [];

// Обработка Enter в поле ввода
barcodeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        scanBarcode();
    }
});

// Фокус на поле ввода при хоткее
ipcRenderer.on('focus-input', () => {
    barcodeInput.focus();
    barcodeInput.select();
});

// Внутреннее сканирование от быстрых кнопок
ipcRenderer.on('scan-barcode-internal', (event, barcode) => {
    barcodeInput.value = barcode;
    scanBarcode();
});

// Основная функция сканирования
function scanBarcode() {
    const barcode = barcodeInput.value.trim();
    
    if (!barcode) {
        showStatus('Введите штрихкод!', 'error');
        return;
    }
    
    // Отправляем в main process
    ipcRenderer.send('scan-barcode', barcode);
    
    // Очищаем поле
    barcodeInput.value = '';
    
    // Показываем статус
    showStatus('⏳ Отправка...', 'success');
}

// Быстрое сканирование
function quickScan(barcode) {
    ipcRenderer.send('scan-barcode', barcode);
    showStatus(`⏳ Сканирование: ${barcode}`, 'success');
}

// Обработка результата
ipcRenderer.on('scan-result', (event, result) => {
    if (result.success) {
        showStatus(`✅ Отсканировано: ${result.barcode}`, 'success');
        addToHistory(result.barcode);
    } else {
        showStatus(`❌ Ошибка: ${result.error}`, 'error');
    }
    
    // Фокус обратно на поле через 1.5 сек
    setTimeout(() => {
        barcodeInput.focus();
    }, 1500);
});

// Показ статуса
function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    
    setTimeout(() => {
        statusDiv.className = 'status';
    }, 3000);
}

// Добавление в историю
function addToHistory(barcode) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    history.unshift({ barcode, time: timeStr });
    
    // Ограничиваем историю 10 записями
    if (history.length > 10) {
        history = history.slice(0, 10);
    }
    
    renderHistory();
}

// Отрисовка истории
function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML = '<div style="color: #b3d4ff; font-size: 13px;">Пусто</div>';
        return;
    }
    
    historyList.innerHTML = history.map(item => `
        <div class="history-item">
            <span>${item.barcode}</span>
            <span class="history-time">${item.time}</span>
        </div>
    `).join('');
}

// Инициализация
renderHistory();
barcodeInput.focus();
