#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Валидатор целостности конфигурации 1С:Предприятие 8.3.27 (XML-файлы)
.DESCRIPTION
    Проверяет соответствие между Configuration.xml, ConfigDumpInfo.xml и файловой структурой.
    Запускать ОБЯЗАТЕЛЬНО перед загрузкой конфигурации из файлов в конфигуратор.
.PARAMETER ConfigPath
    Путь к папке с конфигурацией (где лежит Configuration.xml)
.EXAMPLE
    .\validate-config.ps1
    .\validate-config.ps1 -ConfigPath "D:\Git\Public_Trade_Module\Конфигурация\Проверка"
#>

param(
    [string]$ConfigPath = ""
)

# ═══════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$OutputEncoding = [System.Text.Encoding]::UTF8

# Автоопределение пути
if (-not $ConfigPath) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
    $ConfigPath = Join-Path $projectRoot "Конфигурация\Проверка"
    if (-not (Test-Path $ConfigPath)) {
        $ConfigPath = Join-Path $projectRoot "Конфигурация"
    }
}

$configurationXml = Join-Path $ConfigPath "Configuration.xml"
$configDumpInfo = Join-Path $ConfigPath "ConfigDumpInfo.xml"

if (-not (Test-Path $configurationXml)) {
    Write-Host "FATAL: Configuration.xml не найден: $configurationXml" -ForegroundColor Red
    exit 1
}

# Счётчики
$script:errors = 0
$script:warnings = 0
$script:passed = 0

function Write-Check([string]$status, [string]$message) {
    switch ($status) {
        "OK"   { Write-Host "  [OK] $message" -ForegroundColor Green; $script:passed++ }
        "FAIL" { Write-Host "  [ОШИБКА] $message" -ForegroundColor Red; $script:errors++ }
        "WARN" { Write-Host "  [ПРЕДУП] $message" -ForegroundColor Yellow; $script:warnings++ }
        "INFO" { Write-Host "  [ИНФО] $message" -ForegroundColor Cyan }
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ВАЛИДАТОР КОНФИГУРАЦИИ 1С:Предприятие 8.3.27" -ForegroundColor Cyan
Write-Host "  Путь: $ConfigPath" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# МАППИНГ: тип XML-элемента → папка на диске
# ═══════════════════════════════════════════════════════════════════

$typeToFolder = @{
    "Catalog"              = "Catalogs"
    "Document"             = "Documents"
    "Enum"                 = "Enums"
    "Report"               = "Reports"
    "DataProcessor"        = "DataProcessors"
    "CommonModule"         = "CommonModules"
    "CommonPicture"        = "CommonPictures"
    "CommonTemplate"       = "CommonTemplates"
    "Constant"             = "Constants"
    "InformationRegister"  = "InformationRegisters"
    "AccumulationRegister" = "AccumulationRegisters"
    "Role"                 = "Roles"
    "Subsystem"            = "Subsystems"
    "StyleItem"            = "StyleItems"
    "Style"                = "Styles"
    "Language"             = "Languages"
}

# Типы, требующие InternalInfo/GeneratedType
$typesRequiringInternalInfo = @("Catalog", "Document", "AccumulationRegister", "InformationRegister", "DataProcessor", "Report")

# Типы, которые имеют подпапку (а не только XML-файл)
$typesWithSubfolder = @("Catalog", "Document", "DataProcessor", "Report", "Enum", "InformationRegister", "AccumulationRegister")

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 1: ЧТЕНИЕ Configuration.xml
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 1: Проверка Configuration.xml" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

[xml]$configXml = Get-Content $configurationXml -Encoding UTF8
$ns = New-Object System.Xml.XmlNamespaceManager($configXml.NameTable)
$ns.AddNamespace("md", "http://v8.1c.ru/8.3/MDClasses")

$childObjects = $configXml.MetaDataObject.Configuration.ChildObjects

# Собираем все объекты из Configuration.xml в словарь тип→массив имён
$configObjects = @{}
foreach ($node in $childObjects.ChildNodes) {
    if ($node.NodeType -eq "Element") {
        $typeName = $node.LocalName
        $objectName = $node.InnerText.Trim()
        if (-not $configObjects.ContainsKey($typeName)) {
            $configObjects[$typeName] = @()
        }
        $configObjects[$typeName] += $objectName
    }
}

$totalObjects = ($configObjects.Values | ForEach-Object { $_.Count } | Measure-Object -Sum).Sum
Write-Check "OK" "Configuration.xml прочитан: $totalObjects объектов"

# Проверка version
$version = $configXml.MetaDataObject.version
if ($version -eq "2.20") {
    Write-Check "OK" "version='2.20' корректна"
} else {
    Write-Check "FAIL" "version='$version' — должно быть '2.20'"
}

# Проверка CompatibilityMode
$props = $configXml.MetaDataObject.Configuration.Properties
$compatMode = $props.CompatibilityMode
if ($compatMode) {
    Write-Check "INFO" "CompatibilityMode: $compatMode"
}

$modalityMode = $props.ModalityUseMode
if ($modalityMode -eq "DontUse") {
    Write-Check "OK" "ModalityUseMode=DontUse (модальные окна запрещены)"
} else {
    Write-Check "WARN" "ModalityUseMode='$modalityMode' — рекомендуется DontUse"
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 2: ФАЙЛЫ НА ДИСКЕ ↔ Configuration.xml
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 2: Проверка файлов на диске" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

foreach ($typeName in $typeToFolder.Keys | Sort-Object) {
    $folderName = $typeToFolder[$typeName]
    $folderPath = Join-Path $ConfigPath $folderName
    $registeredNames = @()
    if ($configObjects.ContainsKey($typeName)) {
        $registeredNames = $configObjects[$typeName]
    }

    if (-not (Test-Path $folderPath)) {
        if ($registeredNames.Count -gt 0) {
            Write-Check "FAIL" "Папка $folderName отсутствует, но в Configuration.xml есть $($registeredNames.Count) объектов типа $typeName"
        }
        continue
    }

    # Проверяем: для каждого объекта в Configuration.xml — есть ли XML-файл?
    foreach ($objName in $registeredNames) {
        $xmlFile = Join-Path $folderPath "$objName.xml"
        if (-not (Test-Path $xmlFile)) {
            Write-Check "FAIL" "${typeName}.${objName}: XML-файл отсутствует ($folderName\$objName.xml)"
        } else {
            # Проверяем well-formed XML
            try {
                [xml]$testXml = Get-Content $xmlFile -Encoding UTF8
                # Noop — парсинг успешен
            } catch {
                Write-Check "FAIL" "${typeName}.${objName}: XML невалидный — $($_.Exception.Message)"
            }
        }
    }

    # Обратная проверка: есть ли XML-файлы на диске, не зарегистрированные в Configuration.xml?
    $xmlFiles = Get-ChildItem -Path $folderPath -Filter "*.xml" -File -ErrorAction SilentlyContinue
    foreach ($f in $xmlFiles) {
        $nameFromFile = $f.BaseName
        if ($nameFromFile -notin $registeredNames) {
            Write-Check "FAIL" "${typeName}.${nameFromFile}: XML-файл есть на диске, но НЕ зарегистрирован в Configuration.xml/<ChildObjects>"
        }
    }

    $okCount = ($registeredNames | Where-Object { Test-Path (Join-Path $folderPath "$_.xml") }).Count
    if ($okCount -eq $registeredNames.Count -and $registeredNames.Count -gt 0) {
        Write-Check "OK" "${typeName}: все $okCount объектов имеют XML-файлы"
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 3: ConfigDumpInfo.xml
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 3: Проверка ConfigDumpInfo.xml" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

if (-not (Test-Path $configDumpInfo)) {
    Write-Check "FAIL" "ConfigDumpInfo.xml отсутствует! Загрузка в конфигуратор невозможна."
} else {
    [xml]$dumpXml = Get-Content $configDumpInfo -Encoding UTF8
    $dumpNs = New-Object System.Xml.XmlNamespaceManager($dumpXml.NameTable)
    $dumpNs.AddNamespace("di", "http://v8.1c.ru/8.3/xcf/dumpinfo")

    # Собираем все top-level Metadata записи из ConfigDumpInfo
    $dumpEntries = @{}
    $allDumpNodes = $dumpXml.ConfigDumpInfo.ConfigVersions.Metadata
    foreach ($node in $allDumpNodes) {
        $name = $node.name
        if ($name) {
            $dumpEntries[$name] = $node.id
        }
    }

    Write-Check "OK" "ConfigDumpInfo.xml прочитан: $($dumpEntries.Count) записей"

    # Проверяем: все объекты из Configuration.xml имеют запись в ConfigDumpInfo
    foreach ($typeName in $configObjects.Keys | Sort-Object) {
        # Формируем полное имя для ConfigDumpInfo
        foreach ($objName in $configObjects[$typeName]) {
            $fullName = "$typeName.$objName"
            if (-not $dumpEntries.ContainsKey($fullName)) {
                Write-Check "FAIL" "${fullName}: НЕТ записи в ConfigDumpInfo.xml — загрузка конфигурации обвалится!"
            }
        }
    }

    # Проверяем уникальность UUID
    $uuidMap = @{}
    $duplicateUuids = @()
    foreach ($entry in $dumpEntries.GetEnumerator()) {
        $uuid = $entry.Value
        if ($uuid) {
            if ($uuidMap.ContainsKey($uuid)) {
                $duplicateUuids += "${uuid} - $($uuidMap[$uuid]) ↔ $($entry.Key)"
            } else {
                $uuidMap[$uuid] = $entry.Key
            }
        }
    }

    if ($duplicateUuids.Count -eq 0) {
        Write-Check "OK" "Все UUID в ConfigDumpInfo уникальны"
    } else {
        foreach ($dup in $duplicateUuids) {
            Write-Check "FAIL" "Дублирующийся UUID: $dup"
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 4: Проверка XML объектов метаданных (InternalInfo, UUID)
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 4: Проверка структуры XML объектов" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

$uuidPattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

foreach ($typeName in $typesRequiringInternalInfo) {
    $folderName = $typeToFolder[$typeName]
    if (-not $folderName) { continue }
    $folderPath = Join-Path $ConfigPath $folderName
    if (-not (Test-Path $folderPath)) { continue }

    $registeredNames = @()
    if ($configObjects.ContainsKey($typeName)) {
        $registeredNames = $configObjects[$typeName]
    }

    foreach ($objName in $registeredNames) {
        $xmlFile = Join-Path $folderPath "$objName.xml"
        if (-not (Test-Path $xmlFile)) { continue }

        try {
            [xml]$objXml = Get-Content $xmlFile -Encoding UTF8
            $rootNode = $objXml.MetaDataObject
            if (-not $rootNode) { continue }
            
            # Находим узел объекта (Catalog, Document и т.д.)
            $objNode = $rootNode.SelectSingleNode("md:$typeName", $ns)
            if (-not $objNode) {
                # Попробуем без namespace
                $objNode = $rootNode.$typeName
            }
            if (-not $objNode) { continue }

            # Проверяем UUID корневого элемента
            $objUuid = $objNode.uuid
            if ($objUuid) {
                if ($objUuid -notmatch $uuidPattern) {
                    Write-Check "FAIL" "${typeName}.${objName}: UUID '$objUuid' не соответствует формату"
                }
            } else {
                Write-Check "FAIL" "${typeName}.${objName}: отсутствует uuid атрибут"
            }

            # Проверяем version
            $objVersion = $rootNode.version
            if ($objVersion -and $objVersion -ne "2.20") {
                Write-Check "FAIL" "${typeName}.${objName}: version='$objVersion' — должно быть '2.20'"
            }

            # Проверяем InternalInfo
            $internalInfo = $objNode.InternalInfo
            if (-not $internalInfo) {
                Write-Check "WARN" "${typeName}.${objName}: отсутствует InternalInfo/GeneratedType"
            }

        } catch {
            Write-Check "FAIL" "${typeName}.${objName}: ошибка чтения XML — $($_.Exception.Message)"
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 5: Проверка форм (element id, обязательные вложенные элементы)
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 5: Проверка форм" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

$formFiles = Get-ChildItem -Path $ConfigPath -Recurse -Filter "Form.xml" -File -ErrorAction SilentlyContinue

if ($formFiles.Count -eq 0) {
    Write-Check "WARN" "Файлы форм (Form.xml) не найдены"
} else {
    Write-Check "INFO" "Найдено файлов форм: $($formFiles.Count)"

    foreach ($formFile in $formFiles) {
        $relativePath = $formFile.FullName.Replace($ConfigPath, "").TrimStart("\")
        
        try {
            $content = Get-Content $formFile.FullName -Encoding UTF8 -Raw
            [xml]$formXml = $content
        } catch {
            Write-Check "FAIL" "$relativePath : XML невалидный — $($_.Exception.Message)"
            continue
        }

        # Собираем все id элементов формы
        $allIds = @()
        $allElements = $formXml.SelectNodes("//*[@id]")
        foreach ($elem in $allElements) {
            $id = $elem.GetAttribute("id")
            if ($id) {
                $allIds += $id
            }
        }

        # Проверяем уникальность id
        $duplicateIds = $allIds | Group-Object | Where-Object { $_.Count -gt 1 }
        if ($duplicateIds) {
            foreach ($dup in $duplicateIds) {
                Write-Check "FAIL" "$relativePath : дублирующийся id='$($dup.Name)' (встречается $($dup.Count) раз)"
            }
        } else {
            if ($allIds.Count -gt 0) {
                Write-Check "OK" "$relativePath : $($allIds.Count) элементов, id уникальны"
            }
        }

        # Проверяем что формы версии 2.20
        $formVersion = $formXml.Form.version
        if ($formVersion -and $formVersion -ne "2.20") {
            Write-Check "FAIL" "$relativePath : version='$formVersion' — должно быть '2.20'"
        }

        # Проверяем наличие placeholder'ов {{...}} (забытые шаблоны)
        if ($content -match '\{\{[^}]+\}\}') {
            $placeholders = [regex]::Matches($content, '\{\{[^}]+\}\}') | ForEach-Object { $_.Value } | Select-Object -Unique
            foreach ($ph in $placeholders) {
                Write-Check "FAIL" "$relativePath : незамённый placeholder $ph"
            }
        }

        # Проверяем наличие ContextMenu и ExtendedTooltip для InputField, Table, LabelField, CheckBoxField, Button
        $elementsNeedingChildren = @("InputField", "Table", "LabelField", "CheckBoxField", "Button", "LabelDecoration")
        foreach ($elemType in $elementsNeedingChildren) {
            $elements = $formXml.GetElementsByTagName($elemType)
            foreach ($elem in $elements) {
                $elemName = $elem.GetAttribute("name")
                if (-not $elemName) { continue }

                # Для InputField, LabelField, CheckBoxField — нужны ContextMenu + ExtendedTooltip
                if ($elemType -in @("InputField", "LabelField", "CheckBoxField")) {
                    $hasCtx = $false
                    $hasTooltip = $false
                    foreach ($child in $elem.ChildNodes) {
                        if ($child.LocalName -eq "ContextMenu") { $hasCtx = $true }
                        if ($child.LocalName -eq "ExtendedTooltip") { $hasTooltip = $true }
                    }
                    if (-not $hasCtx) {
                        Write-Check "FAIL" "$relativePath : $elemType '$elemName' — отсутствует ContextMenu"
                    }
                    if (-not $hasTooltip) {
                        Write-Check "FAIL" "$relativePath : $elemType '$elemName' — отсутствует ExtendedTooltip"
                    }
                }

                # Для Table — дополнительно нужны AutoCommandBar, SearchStringAddition, ViewStatusAddition, SearchControlAddition
                if ($elemType -eq "Table") {
                    $requiredChildren = @("ContextMenu", "AutoCommandBar", "ExtendedTooltip", "SearchStringAddition", "ViewStatusAddition", "SearchControlAddition")
                    foreach ($reqChild in $requiredChildren) {
                        $found = $false
                        foreach ($child in $elem.ChildNodes) {
                            if ($child.LocalName -eq $reqChild) { $found = $true; break }
                        }
                        if (-not $found) {
                            Write-Check "FAIL" "$relativePath : Table '$elemName' — отсутствует обязательный $reqChild"
                        }
                    }
                }
            }
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 6: Проверка модулей (Forms/*/Ext/Form/Module.bsl)
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 6: Проверка файловой структуры объектов" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

foreach ($typeName in @("Document", "Catalog", "DataProcessor", "Report")) {
    $folderName = $typeToFolder[$typeName]
    $folderPath = Join-Path $ConfigPath $folderName
    if (-not (Test-Path $folderPath)) { continue }

    $registeredNames = @()
    if ($configObjects.ContainsKey($typeName)) {
        $registeredNames = $configObjects[$typeName]
    }

    foreach ($objName in $registeredNames) {
        $objFolder = Join-Path $folderPath $objName
        
        # Объект имеет XML — должна быть и папка (если есть модули/формы)
        if ((Test-Path $objFolder) -and (Test-Path "$objFolder\Forms")) {
            # Проверяем формы
            $formFolders = Get-ChildItem -Path "$objFolder\Forms" -Directory -ErrorAction SilentlyContinue
            foreach ($formFolder in $formFolders) {
                $formXmlFile = Join-Path "$objFolder\Forms" "$($formFolder.Name).xml"
                $formExtXml = Join-Path $formFolder.FullName "Ext\Form.xml"
                $formModule = Join-Path $formFolder.FullName "Ext\Form\Module.bsl"

                # Должен быть Form.xml описатель
                if (-not (Test-Path $formXmlFile)) {
                    Write-Check "FAIL" "$typeName.$objName.Form.$($formFolder.Name): отсутствует $($formFolder.Name).xml описатель формы"
                }
                # Должен быть Ext/Form.xml
                if (-not (Test-Path $formExtXml)) {
                    Write-Check "FAIL" "$typeName.$objName.Form.$($formFolder.Name): отсутствует Ext\Form.xml"
                }
                # Должен быть Ext/Form/Module.bsl
                if (-not (Test-Path $formModule)) {
                    Write-Check "WARN" "$typeName.$objName.Form.$($formFolder.Name): отсутствует Ext\Form\Module.bsl (модуль формы)"
                }
            }
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ЭТАП 7: Проверка перекрёстных ссылок (RegisterRecords, DefaultObjectForm)
# ═══════════════════════════════════════════════════════════════════

Write-Host "ЭТАП 7: Проверка перекрёстных ссылок" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray

$registeredRegisters = @()
if ($configObjects.ContainsKey("AccumulationRegister")) {
    $registeredRegisters += $configObjects["AccumulationRegister"]
}
if ($configObjects.ContainsKey("InformationRegister")) {
    $registeredRegisters += $configObjects["InformationRegister"]
}

# Проверяем RegisterRecords документов
if ($configObjects.ContainsKey("Document")) {
    $docFolder = Join-Path $ConfigPath "Documents"
    foreach ($docName in $configObjects["Document"]) {
        $docXmlFile = Join-Path $docFolder "$docName.xml"
        if (-not (Test-Path $docXmlFile)) { continue }

        try {
            [xml]$docXml = Get-Content $docXmlFile -Encoding UTF8
            $docNode = $docXml.MetaDataObject.Document
            if (-not $docNode) { continue }
            $props = $docNode.Properties

            # DefaultObjectForm
            $defaultForm = $props.DefaultObjectForm
            if ($defaultForm -and $defaultForm.Trim()) {
                # Формат: Document.ЧекККМ.Form.ФормаДокумента
                $parts = $defaultForm.Trim() -split "\."
                if ($parts.Count -ge 4) {
                    $formName = $parts[-1]
                    $formFolder = Join-Path $docFolder "$docName\Forms\$formName"
                    if (-not (Test-Path $formFolder)) {
                        Write-Check "FAIL" "Document.${docName}: DefaultObjectForm='$defaultForm' — папка формы не найдена"
                    }
                }
            }

            # RegisterRecords
            $regRecords = $props.RegisterRecords
            if ($regRecords) {
                foreach ($item in $regRecords.ChildNodes) {
                    if ($item.NodeType -eq "Element") {
                        $regRef = $item.InnerText.Trim()
                        # Формат: AccumulationRegister.ОстаткиТоваров
                        $regParts = $regRef -split "\."
                        if ($regParts.Count -ge 2) {
                            $regName = $regParts[1]
                            $allRegisters = @()
                            if ($configObjects.ContainsKey("AccumulationRegister")) { $allRegisters += $configObjects["AccumulationRegister"] }
                            if ($configObjects.ContainsKey("InformationRegister")) { $allRegisters += $configObjects["InformationRegister"] }
                            if ($regName -notin $allRegisters) {
                                Write-Check "FAIL" "Document.${docName}: RegisterRecords ссылается на '$regRef', который не зарегистрирован в Configuration.xml"
                            }
                        }
                    }
                }
            }
        } catch {
            # Уже обработано на этапе 2
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# ИТОГ
# ═══════════════════════════════════════════════════════════════════

Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ИТОГ:" -ForegroundColor Cyan
Write-Host "    Проверок пройдено : $script:passed" -ForegroundColor Green
Write-Host "    Предупреждений    : $script:warnings" -ForegroundColor Yellow
Write-Host "    ОШИБОК            : $script:errors" -ForegroundColor $(if ($script:errors -gt 0) { "Red" } else { "Green" })
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($script:errors -gt 0) {
    Write-Host "  ЗАГРУЗКА В КОНФИГУРАТОР ЗАБЛОКИРОВАНА — исправьте ошибки!" -ForegroundColor Red
    Write-Host ""
    exit 1
} else {
    Write-Host "  Конфигурация готова к загрузке." -ForegroundColor Green
    Write-Host ""
    exit 0
}
