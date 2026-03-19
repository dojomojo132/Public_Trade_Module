#Область ОбработчикиHTTPСервисов

Функция mainGET(Запрос)
	
	Ответ = Новый HTTPСервисОтвет(200);
	Ответ.Заголовки.Вставить("Content-Type", "text/html; charset=utf-8");
	Ответ.Заголовки.Вставить("Access-Control-Allow-Origin", "*");
	Ответ.УстановитьТелоИзСтроки(СформироватьHTMLСтраницу());
	Возврат Ответ;
	
КонецФункции

Функция cartGET(Запрос)
	
	ИдСессии = Запрос.ПараметрыЗапроса.Получить("session");
	Если НЕ ЗначениеЗаполнено(ИдСессии) Тогда
		Возврат СформироватьОтветОшибки(400, "Не указан параметр session");
	КонецЕсли;
	
	ЗапросДанных = Новый Запрос;
	ЗапросДанных.Текст =
		"ВЫБРАТЬ
		|	Корзина.НомерПозиции КАК НомерПозиции,
		|	Корзина.Штрихкод КАК Штрихкод,
		|	Корзина.Наименование КАК Наименование,
		|	Корзина.Количество КАК Количество,
		|	Корзина.Цена КАК Цена,
		|	Корзина.Сумма КАК Сумма
		|ИЗ
		|	РегистрСведений.Анл_МобильнаяКорзина КАК Корзина
		|ГДЕ
		|	Корзина.ИдСессии = &ИдСессии
		|	И (Корзина.НомерПозиции < 10000
		|		ИЛИ Корзина.Отправлено = ЛОЖЬ)
		|УПОРЯДОЧИТЬ ПО
		|	НомерПозиции";
	ЗапросДанных.УстановитьПараметр("ИдСессии", ИдСессии);
	
	Результат = ЗапросДанных.Выполнить();
	Выборка = Результат.Выбрать();
	
	Товары = Новый Массив;
	Пока Выборка.Следующий() Цикл
		Товар = Новый Структура;
		Товар.Вставить("line", Выборка.НомерПозиции);
		Товар.Вставить("barcode", Выборка.Штрихкод);
		Товар.Вставить("name", Выборка.Наименование);
		Товар.Вставить("qty", Выборка.Количество);
		Товар.Вставить("price", Выборка.Цена);
		Товар.Вставить("sum", Выборка.Сумма);
		Если Выборка.НомерПозиции < 10000 Тогда
			Товар.Вставить("source", "rmk");
		Иначе
			Товар.Вставить("source", "mobile");
		КонецЕсли;
		Товары.Добавить(Товар);
	КонецЦикла;
	
	Данные = Новый Структура;
	Данные.Вставить("success", Истина);
	Данные.Вставить("items", Товары);
	
	Возврат СформироватьОтветJSON(200, Данные);
	
КонецФункции

Функция cartPOST(Запрос)
	
	Попытка
		ЧтениеJSON = Новый ЧтениеJSON;
		ЧтениеJSON.УстановитьСтроку(Запрос.ПолучитьТелоКакСтроку());
		ДанныеЗапроса = ПрочитатьJSON(ЧтениеJSON);
	Исключение
		Возврат СформироватьОтветОшибки(400, "Некорректный JSON");
	КонецПопытки;
	
	ИдСессии = ДанныеЗапроса.session;
	Штрихкод = ДанныеЗапроса.barcode;
	
	Если НЕ ЗначениеЗаполнено(ИдСессии) ИЛИ НЕ ЗначениеЗаполнено(Штрихкод) Тогда
		Возврат СформироватьОтветОшибки(400, "Не указаны session или barcode");
	КонецЕсли;
	
	// Поиск товара по штрихкоду
	ЗапросШК = Новый Запрос;
	ЗапросШК.Текст =
		"ВЫБРАТЬ ПЕРВЫЕ 1
		|	Штрихкоды.Номенклатура КАК Номенклатура
		|ИЗ
		|	РегистрСведений.Штрихкоды КАК Штрихкоды
		|ГДЕ
		|	Штрихкоды.Штрихкод = &Штрихкод";
	ЗапросШК.УстановитьПараметр("Штрихкод", Штрихкод);
	
	РезультатШК = ЗапросШК.Выполнить();
	Если РезультатШК.Пустой() Тогда
		Возврат СформироватьОтветОшибки(404, "Товар не найден");
	КонецЕсли;
	
	ВыборкаШК = РезультатШК.Выбрать();
	ВыборкаШК.Следующий();
	Номенклатура = ВыборкаШК.Номенклатура;
	
	// Получить розничную цену
	Цена = ОбщегоНазначения.ПолучитьРозничнуюЦену(ТекущаяДатаСеанса(), Номенклатура);
	
	// Определить следующий номер строки (мобильные товары >= 10000)
	ЗапросМакс = Новый Запрос;
	ЗапросМакс.Текст =
		"ВЫБРАТЬ
		|	ЕСТЬNULL(МАКСИМУМ(Корзина.НомерПозиции), 9999) КАК МаксНомер
		|ИЗ
		|	РегистрСведений.Анл_МобильнаяКорзина КАК Корзина
		|ГДЕ
		|	Корзина.ИдСессии = &ИдСессии
		|	И Корзина.НомерПозиции >= 10000";
	ЗапросМакс.УстановитьПараметр("ИдСессии", ИдСессии);
	
	РезультатМакс = ЗапросМакс.Выполнить();
	ВыборкаМакс = РезультатМакс.Выбрать();
	ВыборкаМакс.Следующий();
	НовыйНомер = Макс(ВыборкаМакс.МаксНомер + 1, 10000);
	
	// Записать в регистр
	НаборЗаписей = РегистрыСведений.Анл_МобильнаяКорзина.СоздатьНаборЗаписей();
	НаборЗаписей.Отбор.ИдСессии.Установить(ИдСессии);
	НаборЗаписей.Отбор.НомерПозиции.Установить(НовыйНомер);
	НоваяЗапись = НаборЗаписей.Добавить();
	НоваяЗапись.ИдСессии = ИдСессии;
	НоваяЗапись.НомерПозиции = НовыйНомер;
	НоваяЗапись.Штрихкод = Штрихкод;
	НоваяЗапись.Наименование = СокрЛП(Номенклатура.Наименование);
	НоваяЗапись.Количество = 1;
	НоваяЗапись.Цена = Цена;
	НоваяЗапись.Сумма = Цена;
	НоваяЗапись.ДатаДобавления = ТекущаяДатаСеанса();
	НоваяЗапись.Отправлено = Ложь;
	НаборЗаписей.Записать();
	
	Данные = Новый Структура;
	Данные.Вставить("success", Истина);
	Данные.Вставить("name", СокрЛП(Номенклатура.Наименование));
	Данные.Вставить("line", НовыйНомер);
	
	Возврат СформироватьОтветJSON(200, Данные);
	
КонецФункции

Функция cartDELETE(Запрос)
	
	ИдСессии = Запрос.ПараметрыЗапроса.Получить("session");
	Если НЕ ЗначениеЗаполнено(ИдСессии) Тогда
		Возврат СформироватьОтветОшибки(400, "Не указан параметр session");
	КонецЕсли;
	
	ЗапросУдаления = Новый Запрос;
	ЗапросУдаления.Текст =
		"ВЫБРАТЬ
		|	Корзина.ИдСессии КАК ИдСессии,
		|	Корзина.НомерПозиции КАК НомерПозиции
		|ИЗ
		|	РегистрСведений.Анл_МобильнаяКорзина КАК Корзина
		|ГДЕ
		|	Корзина.ИдСессии = &ИдСессии
		|	И Корзина.НомерПозиции >= 10000
		|	И Корзина.Отправлено = ЛОЖЬ";
	ЗапросУдаления.УстановитьПараметр("ИдСессии", ИдСессии);
	
	Результат = ЗапросУдаления.Выполнить();
	Выборка = Результат.Выбрать();
	
	Пока Выборка.Следующий() Цикл
		НаборЗаписей = РегистрыСведений.Анл_МобильнаяКорзина.СоздатьНаборЗаписей();
		НаборЗаписей.Отбор.ИдСессии.Установить(Выборка.ИдСессии);
		НаборЗаписей.Отбор.НомерПозиции.Установить(Выборка.НомерПозиции);
		НаборЗаписей.Записать();
	КонецЦикла;
	
	Данные = Новый Структура;
	Данные.Вставить("success", Истина);
	
	Возврат СформироватьОтветJSON(200, Данные);
	
КонецФункции

Функция sendPOST(Запрос)
	
	Попытка
		ЧтениеJSON = Новый ЧтениеJSON;
		ЧтениеJSON.УстановитьСтроку(Запрос.ПолучитьТелоКакСтроку());
		ДанныеЗапроса = ПрочитатьJSON(ЧтениеJSON);
	Исключение
		Возврат СформироватьОтветОшибки(400, "Некорректный JSON");
	КонецПопытки;
	
	ИдСессии = ДанныеЗапроса.session;
	Если НЕ ЗначениеЗаполнено(ИдСессии) Тогда
		Возврат СформироватьОтветОшибки(400, "Не указан параметр session");
	КонецЕсли;
	
	ЗапросОтправки = Новый Запрос;
	ЗапросОтправки.Текст =
		"ВЫБРАТЬ
		|	Корзина.ИдСессии КАК ИдСессии,
		|	Корзина.НомерПозиции КАК НомерПозиции
		|ИЗ
		|	РегистрСведений.Анл_МобильнаяКорзина КАК Корзина
		|ГДЕ
		|	Корзина.ИдСессии = &ИдСессии
		|	И Корзина.НомерПозиции >= 10000
		|	И Корзина.Отправлено = ЛОЖЬ";
	ЗапросОтправки.УстановитьПараметр("ИдСессии", ИдСессии);
	
	Результат = ЗапросОтправки.Выполнить();
	Выборка = Результат.Выбрать();
	
	Счетчик = 0;
	Пока Выборка.Следующий() Цикл
		НаборЗаписей = РегистрыСведений.Анл_МобильнаяКорзина.СоздатьНаборЗаписей();
		НаборЗаписей.Отбор.ИдСессии.Установить(Выборка.ИдСессии);
		НаборЗаписей.Отбор.НомерПозиции.Установить(Выборка.НомерПозиции);
		НаборЗаписей.Прочитать();
		Для Каждого Запись Из НаборЗаписей Цикл
			Запись.Отправлено = Истина;
		КонецЦикла;
		НаборЗаписей.Записать();
		Счетчик = Счетчик + 1;
	КонецЦикла;
	
	Данные = Новый Структура;
	Данные.Вставить("success", Истина);
	Данные.Вставить("count", Счетчик);
	
	Возврат СформироватьОтветJSON(200, Данные);
	
КонецФункции

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

Функция СформироватьОтветJSON(КодСостояния, Данные)
	
	Ответ = Новый HTTPСервисОтвет(КодСостояния);
	Ответ.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");
	Ответ.Заголовки.Вставить("Access-Control-Allow-Origin", "*");
	ЗаписьJSON = Новый ЗаписьJSON;
	ЗаписьJSON.УстановитьСтроку();
	ЗаписатьJSON(ЗаписьJSON, Данные);
	Ответ.УстановитьТелоИзСтроки(ЗаписьJSON.Закрыть());
	Возврат Ответ;
	
КонецФункции

Функция СформироватьОтветОшибки(КодСостояния, Сообщение)
	
	Данные = Новый Структура;
	Данные.Вставить("success", Ложь);
	Данные.Вставить("error", Сообщение);
	Возврат СформироватьОтветJSON(КодСостояния, Данные);
	
КонецФункции

Функция СформироватьHTMLСтраницу()
	
	Возврат СформироватьHTMLЗаголовок() + СформироватьHTMLРазметку() + СформироватьHTMLСкрипт();
	
КонецФункции

Функция СформироватьHTMLЗаголовок()
	
	Стр = "<!DOCTYPE html>" + Символы.ПС;
	Стр = Стр + "<html lang=""ru"">" + Символы.ПС;
	Стр = Стр + "<head>" + Символы.ПС;
	Стр = Стр + "  <meta charset=""UTF-8"">" + Символы.ПС;
	Стр = Стр + "  <meta name=""viewport"" content=""width=device-width, initial-scale=1.0, user-scalable=no"">" + Символы.ПС;
	Стр = Стр + "  <title>Мобильная касса PTM</title>" + Символы.ПС;
	Стр = Стр + "  <script src=""https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js""></script>" + Символы.ПС;
	Стр = Стр + "  <style>" + Символы.ПС;
	Стр = Стр + "    * { box-sizing: border-box; margin: 0; padding: 0; }" + Символы.ПС;
	Стр = Стр + "    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f5; }" + Символы.ПС;
	Стр = Стр + "    .header { background: #1976d2; color: white; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; }" + Символы.ПС;
	Стр = Стр + "    .header h1 { font-size: 18px; }" + Символы.ПС;
	Стр = Стр + "    .status { font-size: 12px; padding: 2px 8px; border-radius: 12px; }" + Символы.ПС;
	Стр = Стр + "    .status.connected { background: #4caf50; }" + Символы.ПС;
	Стр = Стр + "    .status.disconnected { background: #f44336; }" + Символы.ПС;
	Стр = Стр + "    .session-bar { padding: 8px 16px; background: #e3f2fd; display: flex; gap: 8px; align-items: center; }" + Символы.ПС;
	Стр = Стр + "    .session-bar input { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }" + Символы.ПС;
	Стр = Стр + "    .session-bar button { padding: 8px 16px; background: #1976d2; color: white; border: none; border-radius: 4px; font-size: 14px; }" + Символы.ПС;
	Стр = Стр + "    .scan-btn-area { padding: 8px 16px; }" + Символы.ПС;
	Стр = Стр + "    .scan-btn { width: 100%; padding: 14px; background: #1976d2; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }" + Символы.ПС;
	Стр = Стр + "    .scan-btn:active { background: #1565c0; }" + Символы.ПС;
	Стр = Стр + "    .scan-btn.active { background: #f44336; }" + Символы.ПС;
	Стр = Стр + "    .scanner-area { padding: 0 16px 8px; }" + Символы.ПС;
	Стр = Стр + "    #reader { width: 100%; border-radius: 8px; overflow: hidden; }" + Символы.ПС;
	Стр = Стр + "    .manual-input { padding: 0 16px 16px; display: flex; gap: 8px; }" + Символы.ПС;
	Стр = Стр + "    .manual-input input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }" + Символы.ПС;
	Стр = Стр + "    .manual-input button { padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 4px; font-size: 16px; }" + Символы.ПС;
	Стр = Стр + "    .receipt { padding: 0 16px; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item { background: white; padding: 12px; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item .name { font-size: 14px; font-weight: 500; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item .details { font-size: 12px; color: #666; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item .price { font-size: 16px; font-weight: bold; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item .remove-btn { background: #f44336; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; font-size: 14px; cursor: pointer; }" + Символы.ПС;
	Стр = Стр + "    .section-header { padding: 8px 16px; font-size: 13px; font-weight: 600; color: #666; text-transform: uppercase; background: #e8e8e8; margin-top: 8px; border-radius: 4px; }" + Символы.ПС;
	Стр = Стр + "    .receipt-item.rmk { opacity: 0.6; background: #f0f0f0; }" + Символы.ПС;
	Стр = Стр + "    .total-bar { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 12px 16px; box-shadow: 0 -2px 8px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }" + Символы.ПС;
	Стр = Стр + "    .total-bar .total { font-size: 20px; font-weight: bold; }" + Символы.ПС;
	Стр = Стр + "    .total-bar .send-btn { padding: 12px 32px; background: #4caf50; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: bold; }" + Символы.ПС;
	Стр = Стр + "    .total-bar .send-btn:disabled { background: #ccc; }" + Символы.ПС;
	Стр = Стр + "    .empty-message { text-align: center; padding: 40px 16px; color: #999; font-size: 16px; }" + Символы.ПС;
	Стр = Стр + "    .notification { position: fixed; top: 60px; left: 16px; right: 16px; padding: 12px; border-radius: 8px; color: white; font-size: 14px; z-index: 1000; display: none; }" + Символы.ПС;
	Стр = Стр + "    .notification.success { background: #4caf50; }" + Символы.ПС;
	Стр = Стр + "    .notification.error { background: #f44336; }" + Символы.ПС;
	Стр = Стр + "    .qty-controls { display: flex; align-items: center; gap: 8px; }" + Символы.ПС;
	Стр = Стр + "    .qty-btn { width: 28px; height: 28px; border: 1px solid #ccc; border-radius: 4px; background: white; font-size: 18px; cursor: pointer; }" + Символы.ПС;
	Стр = Стр + "    .qty-value { font-size: 16px; min-width: 20px; text-align: center; }" + Символы.ПС;
	Стр = Стр + "    .receipt-footer { height: 80px; }" + Символы.ПС;
	Стр = Стр + "  </style>" + Символы.ПС;
	Стр = Стр + "</head>" + Символы.ПС;
	
	Возврат Стр;
	
КонецФункции

Функция СформироватьHTMLРазметку()
	
	Стр = "<body>" + Символы.ПС;
	Стр = Стр + "  <div class=""header"">" + Символы.ПС;
	Стр = Стр + "    <h1>📱 Мобильная касса</h1>" + Символы.ПС;
	Стр = Стр + "    <span class=""status disconnected"" id=""statusBadge"">Нет связи</span>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""session-bar"" id=""sessionBar"">" + Символы.ПС;
	Стр = Стр + "    <input type=""text"" id=""sessionInput"" placeholder=""ID сессии (UUID)"">" + Символы.ПС;
	Стр = Стр + "    <button onclick=""connectSession()"">Подключить</button>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""scan-btn-area"" id=""scanBtnArea"" style=""display:none"">" + Символы.ПС;
	Стр = Стр + "    <button class=""scan-btn"" id=""scanBtn"" onclick=""toggleScanner()"">📷 Сканировать</button>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""scanner-area"" id=""scannerArea"" style=""display:none"">" + Символы.ПС;
	Стр = Стр + "    <div id=""reader""></div>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""manual-input"" id=""manualArea"" style=""display:none"">" + Символы.ПС;
	Стр = Стр + "    <input type=""text"" id=""barcodeInput"" placeholder=""Введите штрихкод"" inputmode=""numeric"">" + Символы.ПС;
	Стр = Стр + "    <button onclick=""addByBarcode()"">➕</button>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""receipt"" id=""receiptArea"" style=""display:none"">" + Символы.ПС;
	Стр = Стр + "    <div id=""receiptItems""></div>" + Символы.ПС;
	Стр = Стр + "    <div class=""receipt-footer""></div>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""empty-message"" id=""emptyMsg"" style=""display:none"">Отсканируйте товар для начала</div>" + Символы.ПС;
	Стр = Стр + "  <div class=""total-bar"" id=""totalBar"" style=""display:none"">" + Символы.ПС;
	Стр = Стр + "    <div class=""total"" id=""totalSum"">Итого: 0.00 ₴</div>" + Символы.ПС;
	Стр = Стр + "    <button class=""send-btn"" id=""sendBtn"" onclick=""sendToRMK()"">Отправить в кассу</button>" + Символы.ПС;
	Стр = Стр + "  </div>" + Символы.ПС;
	Стр = Стр + "  <div class=""notification"" id=""notification""></div>" + Символы.ПС;
	
	Возврат Стр;
	
КонецФункции

Функция СформироватьHTMLСкрипт()
	
	Стр = "  <script>" + Символы.ПС;
	Стр = Стр + "    const API_BASE = window.location.pathname.replace(/\/$/, '');" + Символы.ПС;
	Стр = Стр + "    let sessionId = '';" + Символы.ПС;
	Стр = Стр + "    let items = [];" + Символы.ПС;
	Стр = Стр + "    let html5Qrcode = null;" + Символы.ПС;
	Стр = Стр + "    let scannerActive = false;" + Символы.ПС;
	Стр = Стр + "    const urlParams = new URLSearchParams(window.location.search);" + Символы.ПС;
	Стр = Стр + "    if (urlParams.get('session')) {" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sessionInput').value = urlParams.get('session');" + Символы.ПС;
	Стр = Стр + "      connectSession();" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function connectSession() {" + Символы.ПС;
	Стр = Стр + "      sessionId = document.getElementById('sessionInput').value.trim();" + Символы.ПС;
	Стр = Стр + "      if (!sessionId) { showNotification('Введите ID сессии', 'error'); return; }" + Символы.ПС;
	Стр = Стр + "      document.getElementById('statusBadge').textContent = 'Подключено';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('statusBadge').className = 'status connected';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sessionBar').style.display = 'none';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('scanBtnArea').style.display = 'block';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('manualArea').style.display = 'flex';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('receiptArea').style.display = 'block';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('emptyMsg').style.display = 'block';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('totalBar').style.display = 'flex';" + Символы.ПС;
	Стр = Стр + "      loadCart();" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function toggleScanner() {" + Символы.ПС;
	Стр = Стр + "      const area = document.getElementById('scannerArea');" + Символы.ПС;
	Стр = Стр + "      const btn = document.getElementById('scanBtn');" + Символы.ПС;
	Стр = Стр + "      if (scannerActive) {" + Символы.ПС;
	Стр = Стр + "        html5Qrcode.stop().then(function() {" + Символы.ПС;
	Стр = Стр + "          area.style.display = 'none';" + Символы.ПС;
	Стр = Стр + "          btn.textContent = '📷 Сканировать';" + Символы.ПС;
	Стр = Стр + "          btn.classList.remove('active');" + Символы.ПС;
	Стр = Стр + "          scannerActive = false;" + Символы.ПС;
	Стр = Стр + "        }).catch(function() { scannerActive = false; });" + Символы.ПС;
	Стр = Стр + "      } else {" + Символы.ПС;
	Стр = Стр + "        area.style.display = 'block';" + Символы.ПС;
	Стр = Стр + "        btn.textContent = '⏹ Остановить камеру';" + Символы.ПС;
	Стр = Стр + "        btn.classList.add('active');" + Символы.ПС;
	Стр = Стр + "        if (!html5Qrcode) { html5Qrcode = new Html5Qrcode('reader'); }" + Символы.ПС;
	Стр = Стр + "        html5Qrcode.start(" + Символы.ПС;
	Стр = Стр + "          { facingMode: 'environment' }," + Символы.ПС;
	Стр = Стр + "          { fps: 10, qrbox: { width: 250, height: 150 }," + Символы.ПС;
	Стр = Стр + "            formatsToSupport: [Html5QrcodeSupportedFormats.EAN_13, Html5QrcodeSupportedFormats.EAN_8," + Символы.ПС;
	Стр = Стр + "              Html5QrcodeSupportedFormats.CODE_128, Html5QrcodeSupportedFormats.CODE_39," + Символы.ПС;
	Стр = Стр + "              Html5QrcodeSupportedFormats.UPC_A, Html5QrcodeSupportedFormats.QR_CODE] }," + Символы.ПС;
	Стр = Стр + "          function(decoded) {" + Символы.ПС;
	Стр = Стр + "            addByBarcodeValue(decoded);" + Символы.ПС;
	Стр = Стр + "            setTimeout(function() {" + Символы.ПС;
	Стр = Стр + "              if (!html5Qrcode) return;" + Символы.ПС;
	Стр = Стр + "              html5Qrcode.stop().then(function() {" + Символы.ПС;
	Стр = Стр + "                document.getElementById('scannerArea').style.display = 'none';" + Символы.ПС;
	Стр = Стр + "                var b = document.getElementById('scanBtn');" + Символы.ПС;
	Стр = Стр + "                b.textContent = '📷 Сканировать';" + Символы.ПС;
	Стр = Стр + "                b.classList.remove('active');" + Символы.ПС;
	Стр = Стр + "                scannerActive = false;" + Символы.ПС;
	Стр = Стр + "              }).catch(function() { scannerActive = false; });" + Символы.ПС;
	Стр = Стр + "            }, 100);" + Символы.ПС;
	Стр = Стр + "          }" + Символы.ПС;
	Стр = Стр + "        ).then(function() { scannerActive = true; }).catch(function(err) {" + Символы.ПС;
	Стр = Стр + "          area.innerHTML = '<p style=""color:#f44336;padding:16px"">Камера недоступна: ' + err + '</p>';" + Символы.ПС;
	Стр = Стр + "          btn.textContent = '📷 Сканировать';" + Символы.ПС;
	Стр = Стр + "          btn.classList.remove('active');" + Символы.ПС;
	Стр = Стр + "        });" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function addByBarcode() {" + Символы.ПС;
	Стр = Стр + "      const input = document.getElementById('barcodeInput');" + Символы.ПС;
	Стр = Стр + "      const barcode = input.value.trim();" + Символы.ПС;
	Стр = Стр + "      if (!barcode) return;" + Символы.ПС;
	Стр = Стр + "      addByBarcodeValue(barcode);" + Символы.ПС;
	Стр = Стр + "      input.value = '';" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    let lastScan = '';" + Символы.ПС;
	Стр = Стр + "    let lastScanTime = 0;" + Символы.ПС;
	Стр = Стр + "    async function addByBarcodeValue(barcode) {" + Символы.ПС;
	Стр = Стр + "      const now = Date.now();" + Символы.ПС;
	Стр = Стр + "      if (barcode === lastScan && now - lastScanTime < 2000) return;" + Символы.ПС;
	Стр = Стр + "      lastScan = barcode;" + Символы.ПС;
	Стр = Стр + "      lastScanTime = now;" + Символы.ПС;
	Стр = Стр + "      try {" + Символы.ПС;
	Стр = Стр + "        const resp = await fetch(API_BASE + '/cart', {" + Символы.ПС;
	Стр = Стр + "          method: 'POST'," + Символы.ПС;
	Стр = Стр + "          headers: { 'Content-Type': 'application/json' }," + Символы.ПС;
	Стр = Стр + "          body: JSON.stringify({ session: sessionId, barcode: barcode })" + Символы.ПС;
	Стр = Стр + "        });" + Символы.ПС;
	Стр = Стр + "        const data = await resp.json();" + Символы.ПС;
	Стр = Стр + "        if (data.success) {" + Символы.ПС;
	Стр = Стр + "          showNotification(data.name + ' добавлен', 'success');" + Символы.ПС;
	Стр = Стр + "          loadCart();" + Символы.ПС;
	Стр = Стр + "        } else {" + Символы.ПС;
	Стр = Стр + "          showNotification(data.error || 'Товар не найден', 'error');" + Символы.ПС;
	Стр = Стр + "        }" + Символы.ПС;
	Стр = Стр + "      } catch(e) {" + Символы.ПС;
	Стр = Стр + "        showNotification('Ошибка связи с сервером', 'error');" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    async function loadCart() {" + Символы.ПС;
	Стр = Стр + "      try {" + Символы.ПС;
	Стр = Стр + "        const resp = await fetch(API_BASE + '/cart?session=' + encodeURIComponent(sessionId));" + Символы.ПС;
	Стр = Стр + "        const data = await resp.json();" + Символы.ПС;
	Стр = Стр + "        if (data.success) {" + Символы.ПС;
	Стр = Стр + "          items = data.items || [];" + Символы.ПС;
	Стр = Стр + "          renderReceipt();" + Символы.ПС;
	Стр = Стр + "        }" + Символы.ПС;
	Стр = Стр + "      } catch(e) { }" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function renderReceipt() {" + Символы.ПС;
	Стр = Стр + "      const container = document.getElementById('receiptItems');" + Символы.ПС;
	Стр = Стр + "      const emptyMsg = document.getElementById('emptyMsg');" + Символы.ПС;
	Стр = Стр + "      const rmkItems = items.filter(function(i){ return i.source === 'rmk'; });" + Символы.ПС;
	Стр = Стр + "      const mobileItems = items.filter(function(i){ return i.source === 'mobile'; });" + Символы.ПС;
	Стр = Стр + "      if (items.length === 0) {" + Символы.ПС;
	Стр = Стр + "        container.innerHTML = '';" + Символы.ПС;
	Стр = Стр + "        emptyMsg.style.display = 'block';" + Символы.ПС;
	Стр = Стр + "        document.getElementById('totalSum').textContent = 'Итого: 0.00 ₴';" + Символы.ПС;
	Стр = Стр + "        document.getElementById('sendBtn').disabled = true;" + Символы.ПС;
	Стр = Стр + "        return;" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "      emptyMsg.style.display = 'none';" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sendBtn').disabled = mobileItems.length === 0;" + Символы.ПС;
	Стр = Стр + "      let html = '';" + Символы.ПС;
	Стр = Стр + "      if (rmkItems.length > 0) {" + Символы.ПС;
	Стр = Стр + "        html += '<div class=""section-header"">В чеке на кассе (' + rmkItems.length + ')</div>';" + Символы.ПС;
	Стр = Стр + "        rmkItems.forEach(function(item) {" + Символы.ПС;
	Стр = Стр + "          html += '<div class=""receipt-item rmk"">' " + Символы.ПС;
	Стр = Стр + "            + '<div><div class=""name"">' + escapeHtml(item.name) + '</div>'" + Символы.ПС;
	Стр = Стр + "            + '<div class=""details"">' + item.qty + ' × ' + item.price.toFixed(2) + '</div></div>'" + Символы.ПС;
	Стр = Стр + "            + '<div class=""price"">' + item.sum.toFixed(2) + '</div></div>';" + Символы.ПС;
	Стр = Стр + "        });" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "      if (mobileItems.length > 0) {" + Символы.ПС;
	Стр = Стр + "        html += '<div class=""section-header"">Добавлено 📱 (' + mobileItems.length + ')</div>';" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "      mobileItems.forEach(function(item) {" + Символы.ПС;
	Стр = Стр + "        html += '<div class=""receipt-item"">' " + Символы.ПС;
	Стр = Стр + "          + '<div><div class=""name"">' + escapeHtml(item.name) + '</div>'" + Символы.ПС;
	Стр = Стр + "          + '<div class=""details"">' + item.barcode + ' | ' + item.qty + ' × ' + item.price.toFixed(2) + '</div></div>'" + Символы.ПС;
	Стр = Стр + "          + '<div style=""display:flex;align-items:center;gap:12px"">'" + Символы.ПС;
	Стр = Стр + "          + '<div class=""price"">' + item.sum.toFixed(2) + '</div>'" + Символы.ПС;
	Стр = Стр + "          + '</div></div>';" + Символы.ПС;
	Стр = Стр + "      });" + Символы.ПС;
	Стр = Стр + "      container.innerHTML = html;" + Символы.ПС;
	Стр = Стр + "      let total = 0;" + Символы.ПС;
	Стр = Стр + "      mobileItems.forEach(function(item) { total += item.sum; });" + Символы.ПС;
	Стр = Стр + "      document.getElementById('totalSum').textContent = 'Итого: ' + total.toFixed(2) + ' ₴';" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    async function sendToRMK() {" + Символы.ПС;
	Стр = Стр + "      if (items.length === 0) return;" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sendBtn').disabled = true;" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sendBtn').textContent = 'Отправка...';" + Символы.ПС;
	Стр = Стр + "      try {" + Символы.ПС;
	Стр = Стр + "        const resp = await fetch(API_BASE + '/send', {" + Символы.ПС;
	Стр = Стр + "          method: 'POST'," + Символы.ПС;
	Стр = Стр + "          headers: { 'Content-Type': 'application/json' }," + Символы.ПС;
	Стр = Стр + "          body: JSON.stringify({ session: sessionId })" + Символы.ПС;
	Стр = Стр + "        });" + Символы.ПС;
	Стр = Стр + "        const data = await resp.json();" + Символы.ПС;
	Стр = Стр + "        if (data.success) {" + Символы.ПС;
	Стр = Стр + "          showNotification('✅ Отправлено на кассу (' + data.count + ' позиций)', 'success');" + Символы.ПС;
	Стр = Стр + "          loadCart();" + Символы.ПС;
	Стр = Стр + "        } else {" + Символы.ПС;
	Стр = Стр + "          showNotification(data.error || 'Ошибка отправки', 'error');" + Символы.ПС;
	Стр = Стр + "        }" + Символы.ПС;
	Стр = Стр + "      } catch(e) {" + Символы.ПС;
	Стр = Стр + "        showNotification('Ошибка связи с сервером', 'error');" + Символы.ПС;
	Стр = Стр + "      }" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sendBtn').disabled = false;" + Символы.ПС;
	Стр = Стр + "      document.getElementById('sendBtn').textContent = 'Отправить в кассу';" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function showNotification(text, type) {" + Символы.ПС;
	Стр = Стр + "      const el = document.getElementById('notification');" + Символы.ПС;
	Стр = Стр + "      el.textContent = text;" + Символы.ПС;
	Стр = Стр + "      el.className = 'notification ' + type;" + Символы.ПС;
	Стр = Стр + "      el.style.display = 'block';" + Символы.ПС;
	Стр = Стр + "      setTimeout(function() { el.style.display = 'none'; }, 3000);" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    function escapeHtml(text) {" + Символы.ПС;
	Стр = Стр + "      const div = document.createElement('div');" + Символы.ПС;
	Стр = Стр + "      div.textContent = text;" + Символы.ПС;
	Стр = Стр + "      return div.innerHTML;" + Символы.ПС;
	Стр = Стр + "    }" + Символы.ПС;
	Стр = Стр + "    document.getElementById('barcodeInput').addEventListener('keydown', function(e) {" + Символы.ПС;
	Стр = Стр + "      if (e.key === 'Enter') addByBarcode();" + Символы.ПС;
	Стр = Стр + "    });" + Символы.ПС;
	Стр = Стр + "    document.getElementById('sessionInput').addEventListener('keydown', function(e) {" + Символы.ПС;
	Стр = Стр + "      if (e.key === 'Enter') connectSession();" + Символы.ПС;
	Стр = Стр + "    });" + Символы.ПС;
	Стр = Стр + "  </script>" + Символы.ПС;
	Стр = Стр + "</body>" + Символы.ПС;
	Стр = Стр + "</html>";
	
	Возврат Стр;
	
КонецФункции

#КонецОбласти