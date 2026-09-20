# OpenAPI 3.1 Specification: «Ядро начисления кэшбэка»

```yaml
openapi: 3.1.0
info:
  title: Cashback Core API
  version: 1.0.0
  description: |
    API ядра начисления кэшбэка.
    Поддерживаемые валюты: RUB, USD, EUR.
    Типы комиссий: fixed, percent, none.
    Статусы транзакций: NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED.
    Максимальный лимит кэшбэка: 500 000 RUB.
  contact:
    name: Cashback Core Team
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://sandbox.example.com/v1
    description: Sandbox

tags:
  - name: Transactions
    description: Операции с транзакциями
  - name: Cashback
    description: Начисления и выплаты кэшбэка
  - name: Limits
    description: Лимиты кэшбэка

paths:
  /transactions:
    post:
      tags: [Transactions]
      summary: Создать или обновить транзакцию
      description: |
        Принимает событие транзакции. Если статус COMPLETED — инициирует начисление кэшбэка.
        Если статус CANCELLED, REFUNDED, FAILED — инициирует сторно ранее начисленного кэшбэка.
        Статусы NEW и PROCESSING не приводят к начислению.
      operationId: createTransaction
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TransactionCreateRequest'
      responses:
        '200':
          description: Транзакция обработана, начисление или сторно выполнено
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TransactionResponse'
        '400':
          description: Некорректный запрос (валюта не поддерживается, неверный тип комиссии, отрицательная сумма)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Связанная сущность не найдена (комиссия, правило, валюта)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '409':
          description: Конфликт идемпотентности — начисление по транзакции уже существует
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервиса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /cashback/accruals:
    get:
      tags: [Cashback]
      summary: Получить список начислений кэшбэка
      description: Возвращает начисления и сторно по фильтрам.
      operationId: listCashbackAccruals
      parameters:
        - name: transactionId
          in: query
          required: false
          schema:
            type: string
            format: uuid
        - name: state
          in: query
          required: false
          schema:
            $ref: '#/components/schemas/AccrualState'
        - name: currency
          in: query
          required: false
          schema:
            $ref: '#/components/schemas/CurrencyCode'
        - name: from
          in: query
          required: false
          schema:
            type: string
            format: date-time
        - name: to
          in: query
          required: false
          schema:
            type: string
            format: date-time
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 200
            default: 50
        - name: offset
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
            default: 0
      responses:
        '200':
          description: Список начислений
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CashbackAccrualListResponse'
        '400':
          description: Некорректные параметры фильтра
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Транзакция не найдена
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервиса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /cashback/payout:
    post:
      tags: [Cashback]
      summary: Инициировать выплату кэшбэка
      description: |
        Выплата выполняется только по доступному остатку:
        начислено минус сторно минус ранее выплачено.
        Валюта должна входить в RUB, USD, EUR.
      operationId: createPayout
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PayoutCreateRequest'
      responses:
        '200':
          description: Выплата инициирована
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PayoutResponse'
        '400':
          description: Некорректный запрос (валюта не поддерживается, сумма меньше или равна нулю)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Начисления для выплаты не найдены
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '409':
          description: Конфликт — недостаточно доступного остатка или выплата уже в обработке
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервиса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /limits:
    get:
      tags: [Limits]
      summary: Получить лимиты кэшбэка
      description: Возвращает применённые лимиты, включая максимальный лимит 500 000 RUB.
      operationId: listLimits
      parameters:
        - name: accrualId
          in: query
          required: false
          schema:
            type: string
            format: uuid
        - name: currency
          in: query
          required: false
          schema:
            $ref: '#/components/schemas/CurrencyCode'
        - name: isCapped
          in: query
          required: false
          schema:
            type: boolean
      responses:
        '200':
          description: Список лимитов
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LimitListResponse'
        '400':
          description: Некорректные параметры фильтра
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Начисление не найдено
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервиса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:

    # ---------- Справочники ----------

    CurrencyCode:
      type: string
      description: Код валюты
      enum: [RUB, USD, EUR]

    Currency:
      type: object
      description: Справочник валют
      required: [currencyCode, name, isActive]
      properties:
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        name:
          type: string
          example: Российский рубль
        isActive:
          type: boolean
          example: true

    CommissionType:
      type: string
      description: Тип комиссии
      enum: [fixed, percent, none]

    Commission:
      type: object
      description: Комиссия по транзакции
      required: [commissionId, commissionType, currencyCode]
      properties:
        commissionId:
          type: string
          format: uuid
        commissionType:
          $ref: '#/components/schemas/CommissionType'
        fixedValue:
          type: number
          nullable: true
          description: Значение фиксированной комиссии
          example: 50
        percentValue:
          type: number
          nullable: true
          description: Значение процентной комиссии
          example: 1.5
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'

    # ---------- Транзакция ----------

    TransactionStatus:
      type: string
      description: Статус транзакции
      enum: [NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED]

    Transaction:
      type: object
      description: Транзакция клиента
      required:
        - transactionId
        - amount
        - status
        - currencyCode
        - commissionId
        - createdAt
        - updatedAt
      properties:
        transactionId:
          type: string
          format: uuid
        amount:
          type: number
          minimum: 0
          example: 10000
        status:
          $ref: '#/components/schemas/TransactionStatus'
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        commissionId:
          type: string
          format: uuid
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    TransactionCreateRequest:
      type: object
      required:
        - transactionId
        - amount
        - currencyCode
        - commissionType
        - status
      properties:
        transactionId:
          type: string
          format: uuid
          description: Идентификатор транзакции
        amount:
          type: number
          minimum: 0
          example: 10000
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        commissionType:
          $ref: '#/components/schemas/CommissionType'
        commissionValue:
          type: number
          nullable: true
          description: Значение комиссии. Для none игнорируется
          example: 1.5
        status:
          $ref: '#/components/schemas/TransactionStatus'
        ruleId:
          type: string
          format: uuid
          nullable: true
          description: Идентификатор правила начисления кэшбэка

    TransactionResponse:
      type: object
      required: [transaction]
      properties:
        transaction:
          $ref: '#/components/schemas/Transaction'
        accrual:
          $ref: '#/components/schemas/CashbackAccrual'
        limit:
          $ref: '#/components/schemas/Limit'

    # ---------- История статусов ----------

    StatusHistory:
      type: object
      description: Запись истории смены статуса
      required:
        - statusHistoryId
        - transactionId
        - statusFrom
        - statusTo
        - changedAt
      properties:
        statusHistoryId:
          type: string
          format: uuid
        transactionId:
          type: string
          format: uuid
        statusFrom:
          $ref: '#/components/schemas/TransactionStatus'
        statusTo:
          $ref: '#/components/schemas/TransactionStatus'
        changedAt:
          type: string
          format: date-time
        reason:
          type: string
          nullable: true

    # ---------- Правило начисления ----------

    CashbackRule:
      type: object
      description: Правило начисления кэшбэка
      required: [ruleId, name, rate, currencyCode, validFrom, isActive]
      properties:
        ruleId:
          type: string
          format: uuid
        name:
          type: string
          example: Базовая ставка 1%
        rate:
          type: number
          description: Ставка кэшбэка
          example: 1.0
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        validFrom:
          type: string
          format: date
        validTo:
          type: string
          format: date
          nullable: true
        isActive:
          type: boolean

    # ---------- Начисление ----------

    AccrualState:
      type: string
      description: Состояние начисления
      enum: [accrued, reversed]

    CashbackAccrual:
      type: object
      description: Начисление или сторно кэшбэка
      required:
        - accrualId
        - transactionId
        - ruleId
        - baseAmount
        - cashbackAmount
        - currencyCode
        - state
        - createdAt
      properties:
        accrualId:
          type: string
          format: uuid
        transactionId:
          type: string
          format: uuid
        ruleId:
          type: string
          format: uuid
        baseAmount:
          type: number
          description: База расчёта после учёта комиссии
          example: 9850
        cashbackAmount:
          type: number
          description: Сумма кэшбэка после лимита и округления
          example: 98.5
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        state:
          $ref: '#/components/schemas/AccrualState'
        createdAt:
          type: string
          format: date-time
        reversedAt:
          type: string
          format: date-time
          nullable: true

    CashbackAccrualListResponse:
      type: object
      required: [items, total]
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/CashbackAccrual'
        total:
          type: integer
          example: 1
        limit:
          type: integer
          example: 50
        offset:
          type: integer
          example: 0

    # ---------- Лимит ----------

    Limit:
      type: object
      description: Применённый лимит кэшбэка
      required:
        - limitId
        - accrualId
        - currencyCode
        - maxAmount
        - appliedAmount
        - isCapped
      properties:
        limitId:
          type: string
          format: uuid
        accrualId:
          type: string
          format: uuid
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        maxAmount:
          type: number
          description: Максимальная сумма лимита, 500 000 RUB
          example: 500000
        appliedAmount:
          type: number
          description: Фактически применённая сумма кэшбэка
          example: 98.5
        isCapped:
          type: boolean
          description: Признак срабатывания лимита
          example: false

    LimitListResponse:
      type: object
      required: [items, total]
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/Limit'
        total:
          type: integer
          example: 1

    # ---------- Выплата ----------

    PayoutStatus:
      type: string
      description: Статус выплаты
      enum: [created, confirmed, paid, failed]

    Payout:
      type: object
      description: Выплата кэшбэка
      required:
        - payoutId
        - customerRef
        - amount
        - currencyCode
        - status
        - createdAt
      properties:
        payoutId:
          type: string
          format: uuid
        customerRef:
          type: string
          example: customer-123
        amount:
          type: number
          example: 98.5
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        status:
          $ref: '#/components/schemas/PayoutStatus'
        createdAt:
          type: string
          format: date-time

    PayoutAccrual:
      type: object
      description: Связь выплаты с начислениями
      required: [payoutId, accrualId, linkedAt]
      properties:
        payoutId:
          type: string
          format: uuid
        accrualId:
          type: string
          format: uuid
        linkedAt:
          type: string
          format: date-time

    PayoutCreateRequest:
      type: object
      required: [customerRef, currencyCode]
      properties:
        customerRef:
          type: string
          example: customer-123
        currencyCode:
          $ref: '#/components/schemas/CurrencyCode'
        amount:
          type: number
          nullable: true
          description: Если не указано — выплачивается весь доступный остаток
          example: 98.5

    PayoutResponse:
      type: object
      required: [payout]
      properties:
        payout:
          $ref: '#/components/schemas/Payout'
        accruals:
          type: array
          items:
            $ref: '#/components/schemas/PayoutAccrual'

    # ---------- Ошибки ----------

    ErrorResponse:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          example: VALIDATION_ERROR
        message:
          type: string
          example: Валюта не поддерживается
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
                example: currencyCode
              issue:
                type: string
                example: Допустимые значения RUB, USD, EUR
```

---

## Самопроверка

### Покрытие сущностей ER в `components.schemas`

| Сущность ER | Схема OAS | Статус |
|---|---|---|
| `Currency` | `Currency`, `CurrencyCode` | ✅ |
| `Commission` | `Commission`, `CommissionType` | ✅ |
| `Transaction` | `Transaction`, `TransactionCreateRequest`, `TransactionResponse`, `TransactionStatus` | ✅ |
| `StatusHistory` | `StatusHistory` | ✅ |
| `CashbackRule` | `CashbackRule` | ✅ |
| `CashbackAccrual` | `CashbackAccrual`, `AccrualState`, `CashbackAccrualListResponse` | ✅ |
| `Limit` | `Limit`, `LimitListResponse` | ✅ |
| `Payout` | `Payout`, `PayoutStatus`, `PayoutCreateRequest`, `PayoutResponse` | ✅ |
| `PayoutAccrual` | `PayoutAccrual` | ✅ |

### Покрытие кодов ответов

| Эндпоинт | 200 | 400 | 404 | 409 | 500 |
|---|---|---|---|---|---|
| `POST /transactions` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /cashback/accruals` | ✅ | ✅ | ✅ | — | ✅ |
| `POST /cashback/payout` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /limits` | ✅ | ✅ | ✅ | — | ✅ |

### Соответствие BRD

| Ограничение BRD | Где отражено |
|---|---|
| Валюты RUB, USD, EUR | `CurrencyCode.enum` |
| Типы комиссий fixed, percent, none | `CommissionType.enum` |
| Статусы NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED | `TransactionStatus.enum` |
| Лимит 500 000 RUB | `Limit.maxAmount` (пример 500000) |
| Идемпотентность | `409` на `POST /transactions` |
| Сторно | `CashbackAccrual.state = reversed`, `reversedAt` |
| Округление до 2 знаков | Отражено в описании `cashbackAmount` |
| Выплата по доступному остатку | `PayoutCreateRequest`, `409` при нехватке остатка |
