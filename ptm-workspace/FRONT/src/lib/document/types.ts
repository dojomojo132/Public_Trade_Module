/**
 * Типы для стандартного движка форм документов PTM.
 *
 * См. ТЗ: Документация/Спецификации/Стандарт_Форм_Документов.md
 * Версия: после Q1–Q5 (статусы, движения, picker, MVP-печать, без configVersion).
 */

// ─── Базовые типы ──────────────────────────────────────────────

export type FieldKind =
  | 'string'
  | 'number'
  | 'date'
  | 'datetime'
  | 'bool'
  | 'enum'
  | 'ref'
  | 'multiline';

export type RefType =
  | 'warehouse'
  | 'counterparty'
  | 'product'
  | 'user'
  | 'organization'
  | 'cashRegister'
  | 'currency'
  | (string & {});

export type Align = 'left' | 'right' | 'center';

export type NumberFormat = 'integer' | 'decimal' | 'money' | 'percent';

/** Статус документа — заменяет 1С-проведение. См. ТЗ §7.1. */
export type DocumentStatus = 'active' | 'excluded' | 'deleted';

// ─── Описание поля шапки ───────────────────────────────────────

export interface BaseField {
  name: string;
  label: string;
  hint?: string;
  required?: boolean;
  readonly?: boolean;
  tabOrder?: number;
  visibleWhen?: (doc: AnyDoc) => boolean;
  enabledWhen?: (doc: AnyDoc) => boolean;
  span?: number;
}

export interface StringField extends BaseField {
  kind: 'string';
  default?: string;
  maxLength?: number;
}

export interface MultilineField extends BaseField {
  kind: 'multiline';
  default?: string;
  rows?: number;
}

export interface NumberField extends BaseField {
  kind: 'number';
  default?: number;
  min?: number;
  max?: number;
  step?: number;
  format?: NumberFormat;
}

export interface DateField extends BaseField {
  kind: 'date' | 'datetime';
  default?: 'now' | string;
}

export interface BoolField extends BaseField {
  kind: 'bool';
  default?: boolean;
}

export interface EnumField extends BaseField {
  kind: 'enum';
  options: Array<{ value: string; label: string }>;
  default?: string;
}

export interface RefField extends BaseField {
  kind: 'ref';
  refType: RefType;
  filter?: (doc: AnyDoc) => Record<string, unknown>;
  onChange?: (doc: AnyDoc, newValue: string | null) => void | Promise<void>;
}

export type HeaderField =
  | StringField
  | MultilineField
  | NumberField
  | DateField
  | BoolField
  | EnumField
  | RefField;

// ─── Описание колонки табличной части ──────────────────────────

export interface BaseColumn {
  name: string;
  label: string;
  width?: string;
  align?: Align;
  required?: boolean;
  readonly?: boolean;
  navCol?: number;
  calc?: (line: AnyLine, doc: AnyDoc) => number | string;
  onInput?: (line: AnyLine, newValue: unknown, doc: AnyDoc) => void;
  visibleWhen?: (doc: AnyDoc) => boolean;
}

export interface StringColumn extends BaseColumn {
  kind: 'string';
  default?: string;
}

export interface NumberColumn extends BaseColumn {
  kind: 'number';
  default?: number;
  min?: number;
  max?: number;
  step?: number;
  format?: NumberFormat;
  precision?: number;
}

/** Настройки кнопки «Подбор» (модального диалога множественного выбора). См. ТЗ §7c. */
export interface RefColumnPicker {
  /** Показывать кнопку «Подбор» в тулбаре ТЧ. По умолчанию false. */
  enabled: boolean;
  /** Имя кастомного компонента подбора (импортируется по соглашению). */
  component?: string;
  /** Разрешён выбор нескольких. По умолчанию true. */
  multi?: boolean;
}

export interface RefColumn extends BaseColumn {
  kind: 'ref';
  refType: RefType;
  /** Inline-поиск в ячейке работает всегда. picker — дополнительная кнопка. */
  picker?: RefColumnPicker;
}

export type LineColumn = StringColumn | NumberColumn | RefColumn;

// ─── Итоги (Footer) ────────────────────────────────────────────

export interface TotalDef {
  label: string;
  calc: (doc: AnyDoc) => number;
  format?: NumberFormat;
  className?: string;
}

// ─── Команды (кнопки в командной панели) ───────────────────────

export interface CommandDef {
  id?: string;
  label: string;
  icon?: string;
  hotkey?: string;
  visibleWhen?: (doc: AnyDoc, ctx: DocumentContext) => boolean;
  enabledWhen?: (doc: AnyDoc, ctx: DocumentContext) => boolean;
  handler: (doc: AnyDoc, ctx: DocumentContext) => void | Promise<void>;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
}

// ─── Регистры и снапшоты (ТЗ §7.2–7.3) ─────────────────────────

export type RegisterKind = 'balance' | 'turnover';

export interface RegisterDimension {
  name: string;
  /** Тип значения измерения */
  refType?: RefType;
  kind?: 'string' | 'number' | 'date' | 'enum';
}

export interface RegisterResource {
  name: string;
  format?: NumberFormat;
  precision?: number;
}

export interface SnapshotConfig {
  /** Подмножество измерений регистра, по которым делается срез. */
  grain: string[];
  /** Периодичность фиксации снапшота. */
  period: 'day' | 'week' | 'month';
}

export interface RegisterSchema {
  name: string;
  kind: RegisterKind;
  dimensions: RegisterDimension[];
  resources: RegisterResource[];
  snapshot: SnapshotConfig;
}

// ─── Движения документа (ТЗ §7a) ───────────────────────────────

/** Источник данных для записи регистра: шапка документа или строка ТЧ. */
export type MovementSource = 'header' | 'lines';

/**
 * Путь к значению вида:
 *   'header.warehouseId' | 'line.productId' | литерал JSON-Logic ({ var: '...' }).
 * MVP — простая строка-путь; в будущем — JSON-Logic объект.
 */
export type FieldRef = string;

export interface MovementRule {
  /** Имя регистра, в который пишем. */
  register: string;
  /** Откуда брать данные: одна запись на документ (header) или на каждую строку (lines). */
  source: MovementSource;
  /** Условие применения (JSON-Logic). Опционально. */
  when?: string | Record<string, unknown>;
  /** Сопоставление: имя измерения регистра → путь к значению. */
  dimensions: Record<string, FieldRef>;
  /** Сопоставление: имя ресурса регистра → путь к значению. */
  resources: Record<string, FieldRef>;
  /** Знак записи: '+' приход, '-' расход. */
  sign: '+' | '-';
}

/** Готовая запись движения, отправляемая на backend и сохраняемая в таблицах регистров. */
export interface Movement {
  register: string;
  dimensions: Record<string, unknown>;
  resources: Record<string, number>;
  sign: '+' | '-';
}

export interface DocumentMovementsSpec {
  /** Декларативные правила (сериализуются в JSON, валидируются и в UI, и в Rust). */
  rules: MovementRule[];
  /**
   * Опционально: TS-функция для случаев, где деклараций недостаточно.
   * Выполняется только в UI. Backend валидирует результат структурно.
   * Конфиги с compute требуют доверенного клиента (RBAC).
   */
  compute?: (doc: AnyDoc) => Movement[];
}

// ─── API-эндпоинты ─────────────────────────────────────────────

export interface DocumentApi {
  create?: string;
  update?: string;
  get?: string;
  /** Сменить статус: active/excluded/deleted. */
  setStatus?: string;
  list?: string;
}

// ─── Главный конфиг документа ──────────────────────────────────

export interface DocumentConfig {
  /** Системное имя типа документа (как в backend). */
  type: string;
  title: string;
  pluralTitle?: string;
  icon?: string;
  accent?: string;

  headerFields: HeaderField[];
  lineColumns: LineColumn[];

  totals?: TotalDef[];

  /** Регистры, в которые этот документ умеет писать. */
  registers?: RegisterSchema[];
  /** Описание движений (см. ТЗ §7a). */
  movements?: DocumentMovementsSpec;

  /** Дополнительные команды (помимо стандартных Сохранить/Исключить/Удалить/Копировать/Печать). */
  commands?: CommandDef[];

  /** Стандартные команды, которые нужно скрыть. */
  hideStandardCommands?: Array<
    'save' | 'exclude' | 'restore' | 'delete' | 'copy' | 'print'
  >;

  /** Валидация перед сохранением. null = ок, string = текст ошибки. */
  validate?: (doc: AnyDoc) => string | null;

  /** Хук перед сохранением (можно изменить doc). */
  beforeSave?: (doc: AnyDoc) => AnyDoc | Promise<AnyDoc>;
  /** Хук после успешного сохранения. */
  afterSave?: (doc: AnyDoc, ctx: DocumentContext) => void | Promise<void>;
  /** Хук после смены статуса. */
  afterStatusChange?: (
    doc: AnyDoc,
    newStatus: DocumentStatus,
    ctx: DocumentContext,
  ) => void | Promise<void>;

  api?: DocumentApi;

  /** Автосохранение (секунды). По умолчанию выключено. */
  autosave?: number;

  /** При Enter в последней колонке последней строки — добавить новую строку. По умолчанию true. */
  autoAddRow?: boolean;

  /** MVP-печать: имя Svelte-компонента шаблона для window.print(). Опционально. */
  printComponent?: string;
}

// ─── Контекст работы формы ─────────────────────────────────────

export interface DocumentContext {
  id: string | null;
  mode: 'create' | 'edit' | 'view';
  /** Текущий статус документа. */
  status: DocumentStatus;
  dirty: boolean;
  saving: boolean;
  goto: (path: string) => Promise<void>;
  toast: (msg: string, kind?: 'success' | 'error' | 'info') => void;
}

// ─── Модель данных документа (общая часть) ─────────────────────

export interface BaseDoc {
  id?: string;
  number?: string;
  date?: string;
  /** Статус документа. Default — 'active'. */
  status?: DocumentStatus;
  comment?: string;
  lines: AnyLine[];
}

export interface BaseLine {
  uid?: number;
  lineNumber?: number;
}

export type AnyDoc = BaseDoc & Record<string, unknown>;
export type AnyLine = BaseLine & Record<string, unknown>;

// ─── Хелпер для определения документа с автокомплитом ──────────

export function defineDocument(config: DocumentConfig): DocumentConfig {
  return config;
}
