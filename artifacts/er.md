# ER-диаграмма: «Ядро начисления кэшбэка»

> **Нормализация:** 3НФ.  
> **Сущности:** `Transaction`, `CashbackRule`, `CashbackAccrual`, `Limit`, `Currency`, `Commission`, `Payout`, `StatusHistory`.  
> **Дополнительно:** `PayoutAccrual` — связующая сущность для M:N между `Payout` и `CashbackAccrual` (требуется для 3НФ, иначе сумма выплаты дублировала бы состав начислений).

---

## 1. PlantUML ER

```plantuml
@startuml
hide methods
hide stereotypes
skinparam linetype ortho

entity "Currency" as Currency {
  * currency_code : CHAR(3) <<PK>>
  --
  * name : VARCHAR
  * is_active : BOOLEAN
}

entity "Commission" as Commission {
  * commission_id : UUID <<PK>>
  --
  * commission_type : ENUM(fixed, percent, none)
  fixed_value : NUMERIC
  percent_value : NUMERIC
  * currency_code : CHAR(3) <<FK>>
}

entity "Transaction" as Transaction {
  * transaction_id : UUID <<PK>>
  --
  * amount : NUMERIC
  * status : ENUM(NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED)
  * currency_code : CHAR(3) <<FK>>
  * commission_id : UUID <<FK>>
  * created_at : TIMESTAMP
  * updated_at : TIMESTAMP
}

entity "StatusHistory" as StatusHistory {
  * status_history_id : UUID <<PK>>
  --
  * transaction_id : UUID <<FK>>
  * status_from : ENUM(NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED)
  * status_to : ENUM(NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED)
  * changed_at : TIMESTAMP
  reason : VARCHAR
}

entity "CashbackRule" as CashbackRule {
  * rule_id : UUID <<PK>>
  --
  * name : VARCHAR
  * rate : NUMERIC
  * currency_code : CHAR(3) <<FK>>
  * valid_from : DATE
  valid_to : DATE
  * is_active : BOOLEAN
}

entity "CashbackAccrual" as CashbackAccrual {
  * accrual_id : UUID <<PK>>
  --
  * transaction_id : UUID <<FK>>
  * rule_id : UUID <<FK>>
  * base_amount : NUMERIC
  * cashback_amount : NUMERIC
  * currency_code : CHAR(3) <<FK>>
  * state : ENUM(accrued, reversed)
  * created_at : TIMESTAMP
  reversed_at : TIMESTAMP
}

entity "Limit" as Limit {
  * limit_id : UUID <<PK>>
  --
  * accrual_id : UUID <<FK>>
  * currency_code : CHAR(3) <<FK>>
  * max_amount : NUMERIC
  * applied_amount : NUMERIC
  * is_capped : BOOLEAN
}

entity "Payout" as Payout {
  * payout_id : UUID <<PK>>
  --
  * customer_ref : VARCHAR
  * amount : NUMERIC
  * currency_code : CHAR(3) <<FK>>
  * status : ENUM(created, confirmed, paid, failed)
  * created_at : TIMESTAMP
}

entity "PayoutAccrual" as PayoutAccrual {
  * payout_id : UUID <<PK, FK>>
  * accrual_id : UUID <<PK, FK>>
  --
  * linked_at : TIMESTAMP
}

Currency ||--o{ Commission : "валюта комиссии"
Currency ||--o{ Transaction : "валюта транзакции"
Currency ||--o{ CashbackRule : "валюта правила"
Currency ||--o{ CashbackAccrual : "валюта начисления"
Currency ||--o{ Limit : "валюта лимита"
Currency ||--o{ Payout : "валюта выплаты"

Commission ||--o{ Transaction : "применена к транзакции"

Transaction ||--o{ StatusHistory : "история статусов"
Transaction ||--o| CashbackAccrual : "начисление по транзакции"

CashbackRule ||--o{ CashbackAccrual : "правило начисления"

CashbackAccrual ||--o| Limit : "лимит начисления"
CashbackAccrual ||--o{ PayoutAccrual : "входит в выплату"

Payout ||--o{ PayoutAccrual : "состав выплаты"

@enduml
```

---

## 2. Mermaid `erDiagram`

```mermaid
erDiagram
    CURRENCY {
        char3 currency_code PK
        varchar name
        boolean is_active
    }

    COMMISSION {
        uuid commission_id PK
        enum commission_type
        numeric fixed_value
        numeric percent_value
        char3 currency_code FK
    }

    TRANSACTION {
        uuid transaction_id PK
        numeric amount
        enum status
        char3 currency_code FK
        uuid commission_id FK
        timestamp created_at
        timestamp updated_at
    }

    STATUS_HISTORY {
        uuid status_history_id PK
        uuid transaction_id FK
        enum status_from
        enum status_to
        timestamp changed_at
        varchar reason
    }

    CASHBACK_RULE {
        uuid rule_id PK
        varchar name
        numeric rate
        char3 currency_code FK
        date valid_from
        date valid_to
        boolean is_active
    }

    CASHBACK_ACCRUAL {
        uuid accrual_id PK
        uuid transaction_id FK
        uuid rule_id FK
        numeric base_amount
        numeric cashback_amount
        char3 currency_code FK
        enum state
        timestamp created_at
        timestamp reversed_at
    }

    LIMIT {
        uuid limit_id PK
        uuid accrual_id FK
        char3 currency_code FK
        numeric max_amount
        numeric applied_amount
        boolean is_capped
    }

    PAYOUT {
        uuid payout_id PK
        varchar customer_ref
        numeric amount
        char3 currency_code FK
        enum status
        timestamp created_at
    }

    PAYOUT_ACCRUAL {
        uuid payout_id PK
        uuid accrual_id PK
        timestamp linked_at
    }

    CURRENCY ||--o{ COMMISSION : "валюта комиссии"
    CURRENCY ||--o{ TRANSACTION : "валюта транзакции"
    CURRENCY ||--o{ CASHBACK_RULE : "валюта правила"
    CURRENCY ||--o{ CASHBACK_ACCRUAL : "валюта начисления"
    CURRENCY ||--o{ LIMIT : "валюта лимита"
    CURRENCY ||--o{ PAYOUT : "валюта выплаты"

    COMMISSION ||--o{ TRANSACTION : "применена к транзакции"

    TRANSACTION ||--o{ STATUS_HISTORY : "история статусов"
    TRANSACTION ||--o| CASHBACK_ACCRUAL : "начисление по транзакции"

    CASHBACK_RULE ||--o{ CASHBACK_ACCRUAL : "правило начисления"

    CASHBACK_ACCRUAL ||--o| LIMIT : "лимит начисления"
    CASHBACK_ACCRUAL ||--o{ PAYOUT_ACCRUAL : "входит в выплату"

    PAYOUT ||--o{ PAYOUT_ACCRUAL : "состав выплаты"
```

---

## 3. Пояснения по сущностям

| Сущность | Назначение | Ключ | Связи |
|---|---|---|---|
| `Currency` | Справочник валют: RUB, USD, EUR | `currency_code` | 1:N к Commission, Transaction, CashbackRule, CashbackAccrual, Limit, Payout |
| `Commission` | Тип и параметры комиссии: fixed, percent, none | `commission_id` | N:1 к Currency; 1:N к Transaction |
| `Transaction` | Транзакция клиента | `transaction_id` | N:1 к Currency, Commission; 1:N к StatusHistory; 1:0..1 к CashbackAccrual |
| `StatusHistory` | История смены статусов транзакции | `status_history_id` | N:1 к Transaction |
| `CashbackRule` | Правило начисления кэшбэка | `rule_id` | N:1 к Currency; 1:N к CashbackAccrual |
| `CashbackAccrual` | Начисление или сторно кэшбэка по транзакции | `accrual_id` | N:1 к Transaction, CashbackRule, Currency; 1:0..1 к Limit; 1:N к PayoutAccrual |
| `Limit` | Применённый лимит `500 000 RUB` | `limit_id` | N:1 к CashbackAccrual, Currency |
| `Payout` | Выплата кэшбэка клиенту | `payout_id` | N:1 к Currency; 1:N к PayoutAccrual |
| `PayoutAccrual` | Состав выплаты (M:N) | `(payout_id, accrual_id)` | N:1 к Payout, CashbackAccrual |

---

## 4. Соответствие Sequence → ER

| Участник Sequence | Сущность ER | Комментарий |
|---|---|---|
| Transaction Source | `Transaction` + `StatusHistory` | Источник события транзакции и её статусов |
| Cashback Core | — | Логика; не хранит состояние, работает с сущностями ниже |
| Commission Calculator | `Commission` | Тип комиссии и параметры |
| Currency Converter | `Currency` | Справочник валют; курсы — вне скоупа BRD |
| Limit Service | `Limit` | Применённый лимит `500 000 RUB` |
| Ledger | `CashbackAccrual` | Начисление и сторно |
| Notification | — | Уведомления; состояние не хранит |
| Reporting | `CashbackAccrual`, `Payout`, `StatusHistory` | Источники данных для отчётности |
| Payout Service | `Payout` + `PayoutAccrual` | Выплата и её состав |
| CashbackRule (BRD) | `CashbackRule` | Ставка кэшбэка задаётся продуктом |

---

## 5. Приведение к 3НФ

| НФ | Проверка | Результат |
|---|---|---|
| 1НФ | Все атрибуты атомарны; повторяющихся групп нет | ✅ |
| 2НФ | Все неключевые атрибуты зависят от полного первичного ключа; в `PayoutAccrual` ключ составной, атрибут `linked_at` зависит от полного ключа | ✅ |
| 3НФ | Транзитивных зависимостей нет: `currency_code` вынесен в `Currency`; `commission_type` вынесен в `Commission`; состав выплаты вынесен в `PayoutAccrual`; лимит вынесен в `Limit` | ✅ |

**Устранённые транзитивные зависимости:**

- Валюта транзакции/комиссии/правила/начисления/лимита/выплаты → вынесена в `Currency`.
- Тип и параметры комиссии → вынесены в `Commission`.
- Состав выплаты (какие начисления входят) → вынесен в `PayoutAccrual`.
- Применённый лимит по начислению → вынесен в `Limit`.

---

## 6. Самопроверка

- [x] Все сущности из Sequence отражены: `Transaction`, `CashbackRule`, `CashbackAccrual`, `Limit`, `Currency`, `Commission`, `Payout`, `StatusHistory`.
- [x] Дополнительно добавлена `PayoutAccrual` для устранения M:N и соответствия 3НФ.
- [x] Все валюты ограничены `RUB`, `USD`, `EUR` (в `Currency`).
- [x] Типы комиссий ограничены `fixed`, `percent`, `none` (в `Commission`).
- [x] Статусы ограничены `NEW`, `PROCESSING`, `COMPLETED`, `CANCELLED`, `REFUNDED`, `FAILED` (в `Transaction` и `StatusHistory`).
- [x] Лимит `500 000 RUB` отражён в `Limit.max_amount`.
- [x] Сторно отражено в `CashbackAccrual.state` и `CashbackAccrual.reversed_at`.
- [x] Идемпотентность обеспечена связью `Transaction 1:0..1 CashbackAccrual`.
- [x] Технические детали API/БД не раскрыты — только логическая модель данных.
