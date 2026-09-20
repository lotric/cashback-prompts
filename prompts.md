# Prompt 1 — BRD
**Роль:** Продуктовый аналитик в финтех-домене.
**Контекст:** Проект «Ядро начисления кэшбэка».
**Вход:** Название проекта, список ограничений.
**Задача:** Сгенерируй BRD-спецификацию.
**Ограничения:**
- Максимальная сумма лимита: 500 000 RUB
- Валюты: RUB, USD, EUR
- Типы комиссий: fixed, percent, none
- Статусы транзакций: NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED
**Формат вывода:** Markdown, таблицы, user stories, acceptance criteria.
**Few-shot:** [вставь 1 короткий пример BRD из смежного финтех-проекта]
**Самопроверка:** Проверь, что все ограничения учтены и нет технических деталей API/БД.

# Prompt 2 — Sequence
**Роль:** Системный архитектор.
**Вход:** {{BRD}} — полный текст BRD из artifacts/brd.md.
**Задача:** Построй Sequence-диаграмму для сценариев начисления, отмены/возврата, выплаты.
**Формат:** Mermaid `sequenceDiagram` + PlantUML.
**Самопроверка:** Каждый шаг из BRD должен быть отражен. Статусы должны совпадать.

# Prompt 3 — ER
**Роль:** DBA / архитектор данных.
**Вход:** {{BRD}} + {{SEQUENCE}}.
**Задача:** Построй ER-диаграмму. Сущности: Transaction, CashbackRule, CashbackAccrual, Limit, Currency, Commission, Payout, StatusHistory.
**Формат:** PlantUML ER + Mermaid `erDiagram`.
**Самопроверка:** Все сущности из Sequence должны быть в ER. Приведи к 3НФ.

# Prompt 4 — OAS
**Роль:** Интегратор / API-аналитик.
**Вход:** {{BRD}} + {{SEQUENCE}} + {{ER}}.
**Задача:** Сгенерируй OpenAPI 3.1 Specification.
**Эндпоинты:** POST /transactions, GET /cashback/accruals, POST /cashback/payout, GET /limits.
**Формат:** YAML.
**Самопроверка:** Все схемы из ER должны быть в components.schemas. Коды ответов: 200, 400, 404, 409, 500.
