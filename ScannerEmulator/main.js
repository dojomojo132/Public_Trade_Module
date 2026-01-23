// =============================================================================
// PTM Scanner Emulator - Electron Main Process
// Имитирует USB сканер с клавиатурным вводом
// =============================================================================

const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const robot = require('robotjs');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 500,
        height: 700,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        autoHideMenuBar: true,
        title: 'PTM Scanner Emulator'
    });

    mainWindow.loadFile('index.html');
    
    // Окно всегда поверх
    mainWindow.setAlwaysOnTop(true, 'floating');
}

app.whenReady().then(() => {
    createWindow();
    
    // Глобальный хоткей Ctrl+Shift+S для быстрого сканирования
    globalShortcut.register('CommandOrControl+Shift+S', () => {
        mainWindow.webContents.send('focus-input');
    });
});

app.on('window-all-closed', () => {
    globalShortcut.unregisterAll();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Обработчик сканирования
ipcMain.on('scan-barcode', async (event, barcode) => {
    if (!barcode || barcode.trim() === '') {
        event.reply('scan-result', { success: false, error: 'Пустой штрихкод' });
        return;
    }
    
    try {
        // Минимизируем окно эмулятора
        mainWindow.minimize();
        
        // Даём время на переключение в 1С
        await sleep(300);
        
        // Имитируем клавиатурный ввод
        robot.typeString(barcode);
        
        // Задержка перед Enter
        await sleep(50);
        
        // Enter (как настоящий сканер)
        robot.keyTap('enter');
        
        event.reply('scan-result', { success: true, barcode });
        
        // Возвращаем окно через 1 секунду
        setTimeout(() => {
            mainWindow.restore();
            mainWindow.focus();
        }, 1000);
        
    } catch (error) {
        event.reply('scan-result', { success: false, error: error.message });
    }
});

// Обработчик быстрых кнопок
ipcMain.on('quick-scan', async (event, barcode) => {
    event.sender.send('scan-barcode-internal', barcode);
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
