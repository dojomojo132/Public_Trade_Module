---
name: 'Form Elements Standards'
description: 'Правила нумерации id элементов и обязательные дочерние элементы в Form.xml'
applyTo: '**/Form.xml'
---

# Правила генерации элементов формы 1С

Полный справочник: `Документация/Технические_стандарты/form-elements.md`

## Правила нумерации id

1. `AutoCommandBar` формы **ВСЕГДА** `id="-1"`
2. Остальные элементы — **последовательная нумерация** начиная с `1`
3. Каждый `ContextMenu` и `ExtendedTooltip` — получает свой уникальный id
4. Формат: основной элемент `id=N`, его ContextMenu `id=N+1`, его ExtendedTooltip `id=N+2`
5. Для Table: основная `id=N`, ContextMenu `N+1`, AutoCommandBar `N+2`, ExtendedTooltip `N+3`, SearchStringAddition `N+4`, ViewStatusAddition `N+5`, SearchControlAddition `N+6`

## Пример распределения id

```
ГруппаШапка              id=1
  ExtendedTooltip        id=2
  Склад                  id=3
    ContextMenu          id=4
    ExtendedTooltip      id=5
  Контрагент             id=6
    ContextMenu          id=7
    ExtendedTooltip      id=8
Товары (Table)           id=9
  ContextMenu            id=10
  AutoCommandBar         id=11
  ExtendedTooltip        id=12
  SearchStringAddition   id=13
  ViewStatusAddition     id=14
  SearchControlAddition  id=15
  ТоварыНоменклатура     id=16
    ContextMenu          id=17
    ExtendedTooltip      id=18
```

## Обязательные дочерние элементы

- Каждый элемент ввода (InputField, CheckBox и т.д.) ОБЯЗАН иметь дочерние:
  - `ContextMenu`
  - `ExtendedTooltip`
- Каждая таблица (Table) ОБЯЗАНА иметь дочерние:
  - `ContextMenu`
  - `AutoCommandBar`
  - `ExtendedTooltip`
  - `SearchStringAddition`
  - `ViewStatusAddition`
  - `SearchControlAddition`
- Группа (Group) ОБЯЗАНА иметь `ExtendedTooltip`
- Все id уникальны внутри одного Form.xml
