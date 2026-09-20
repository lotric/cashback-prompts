# Sequence-диаграммы: «Ядро начисления кэшбэка»

> Выплата показана как выплата доступного остатка по начисленному кэшбэку. Новые статусы транзакций не вводятся.

---

## Описание значимости артефакта

| Раздел | Содержание |
|---|---|
| Процесс и контекст использования | Системное проектирование взаимодействия компонентов ядра кэшбэка. Этап после утверждения BRD, до проектирования данных и API. |
| Цель создания | Описать последовательность вызовов и сообщений между участниками (клиент, API Gateway, сервис транзакций, ядро кэшбэка, сервис правил, сервис лимитов, БД, очередь, внешняя платёжная система) для ключевых сценариев. |
| Что становится определено | Сценарии начисления, отмены/возврата, выплаты и пересчёта; участники, порядок вызовов, предусловия, постусловия, альтернативные потоки и обработка ошибок. |
| Пользователи артефакта | Системный архитектор, системный аналитик, разработчики, QA. Используют для проектирования сервисов, определения контрактов и написания интеграционных тестов. |
| Использование в дальнейшем | Основа для ER-диаграммы и OpenAPI. Используется для трассировки шагов сценария к требованиям BRD и эндпоинтам API. |
| Последствия отсутствия | Разработчики начнут реализовывать взаимодействие по-разному, потеряются альтернативные потоки и ошибки. Возрастёт риск рассинхронизации сервисов и багов на интеграции. |

## 1. Начисление кэшбэка (`COMPLETED`)

### Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant TS as Transaction Source
    participant CC as Cashback Core
    participant Calc as Commission Calculator
    participant Conv as Currency Converter
    participant Lim as Limit Service
    participant L as Ledger
    participant N as Notification
    participant R as Reporting

    TS->>CC: Событие транзакции: tx_id, amount, currency, commission_type, commission_value, status
    CC->>CC: Проверка статуса транзакции

    alt Статус не COMPLETED
        CC-->>TS: Нет начисления для NEW PROCESSING CANCELLED REFUNDED FAILED
    else Статус COMPLETED
        CC->>CC: Проверка валюты RUB USD EUR

        alt Валюта не поддерживается
            CC-->>TS: Отказ - валюта не поддерживается
        else Валюта поддерживается
            CC->>CC: Проверка идемпотентности по tx_id

            alt Уже есть начисление
                CC-->>TS: Повторное начисление запрещено
            else Начисления нет
                CC->>Calc: Рассчитать базу по типу комиссии
                Calc-->>CC: none amount, fixed amount минус fixed, percent amount минус percent

                opt Валюта USD или EUR
                    CC->>Conv: Привести к RUB для проверки лимита
                    Conv-->>CC: RUB-эквивалент
                end

                CC->>Lim: Применить лимит 500 000 RUB
                Lim-->>CC: Кэшбэк равен минимуму из расчёта и 500 000 RUB
                CC->>CC: Округлить до 2 знаков после запятой

                CC->>L: Записать начисление: tx_id, сумма, валюта, статус COMPLETED
                L-->>CC: Начисление зафиксировано

                CC->>N: Уведомить клиента: сумма, валюта, статус COMPLETED
                CC->>R: Передать данные для отчётности
            end
        end
    end
```

### PlantUML

```plantuml
@startuml
autonumber
participant "Transaction Source" as TS
participant "Cashback Core" as CC
participant "Commission Calculator" as Calc
participant "Currency Converter" as Conv
participant "Limit Service" as Lim
participant Ledger as L
participant Notification as N
participant Reporting as R

TS -> CC: Событие транзакции: tx_id, status=COMPLETED, amount, currency, commission_type, commission_value
CC -> CC: Проверка статуса = COMPLETED

alt Статус != COMPLETED
    CC --> TS: Нет начисления (NEW, PROCESSING, CANCELLED, REFUNDED, FAILED)
else Статус = COMPLETED
    CC -> CC: Проверка валюты в {RUB, USD, EUR}

    alt Валюта не поддерживается
        CC --> TS: Отказ: валюта не поддерживается
    else Валюта поддерживается
        CC -> CC: Проверка идемпотентности по tx_id

        alt Уже есть начисление
            CC --> TS: Повторное начисление запрещено
        else Начисления нет
            CC -> Calc: Рассчитать базу
            Calc --> CC: none: amount; fixed: amount-fixed; percent: amount-percent

            opt Валюта USD или EUR
                CC -> Conv: Привести к RUB для лимита
                Conv --> CC: RUB-эквивалент
            end

            CC -> Lim: Применить лимит 500 000 RUB
            Lim --> CC: Кэшбэк = min(расчёт, 500 000 RUB)
            CC -> CC: Округлить до 2 знаков

            CC -> L: Записать начисление (статус COMPLETED)
            L --> CC: Начисление зафиксировано

            CC -> N: Уведомить клиента: сумма, валюта, COMPLETED
            CC -> R: Передать данные для отчётности
        end
    end
end
@enduml
```

---

## 2. Отмена / возврат / ошибка (`CANCELLED`, `REFUNDED`, `FAILED`)

### Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant TS as Transaction Source
    participant CC as Cashback Core
    participant L as Ledger
    participant N as Notification
    participant R as Reporting

    TS->>CC: Событие смены статуса: tx_id, status
    CC->>CC: Проверка статуса

    alt CANCELLED или FAILED
        CC->>L: Проверить начисление по tx_id

        alt Начисления нет
            CC-->>TS: Кэшбэк не начислялся
        else Начисление есть
            CC->>L: Сторнировать начисление
            L-->>CC: Сторно зафиксировано
            CC->>N: Уведомить клиента: сторно, статус CANCELLED или FAILED
            CC->>R: Передать сторно в отчётность
        end

    else REFUNDED
        CC->>L: Проверить начисление по tx_id

        alt Начисления нет
            CC-->>TS: Сторно не требуется
        else Начисление есть
            CC->>L: Сторнировать начисление
            L-->>CC: Сторно зафиксировано
            CC->>N: Уведомить клиента: сторно, статус REFUNDED
            CC->>R: Передать сторно в отчётность
        end

    else NEW или PROCESSING или COMPLETED
        CC-->>TS: Статус не требует сторно
    end
```

### PlantUML

```plantuml
@startuml
autonumber
participant "Transaction Source" as TS
participant "Cashback Core" as CC
participant Ledger as L
participant Notification as N
participant Reporting as R

TS -> CC: Событие смены статуса: tx_id, status=CANCELLED/REFUNDED/FAILED
CC -> CC: Проверка статуса

alt CANCELLED или FAILED
    CC -> L: Проверить начисление по tx_id

    alt Начисления нет
        CC --> TS: Кэшбэк не начислялся
    else Начисление есть
        CC -> L: Сторнировать начисление
        L --> CC: Сторно зафиксировано
        CC -> N: Уведомить клиента: сторно, CANCELLED/FAILED
        CC -> R: Передать сторно в отчётность
    end

else REFUNDED
    CC -> L: Проверить начисление по tx_id

    alt Начисления нет
        CC --> TS: Сторно не требуется
    else Начисление есть
        CC -> L: Сторнировать начисление
        L --> CC: Сторно зафиксировано
        CC -> N: Уведомить клиента: сторно, REFUNDED
        CC -> R: Передать сторно в отчётность
    end

else NEW, PROCESSING, COMPLETED
    CC --> TS: Статус не требует сторно
end
@enduml
```

---

## 3. Выплата кэшбэка

### Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant C as Клиент
    participant CC as Cashback Core
    participant L as Ledger
    participant P as Payout Service
    participant N as Notification
    participant R as Reporting

    C->>CC: Запрос выплаты кэшбэка
    CC->>CC: Проверка валюты RUB USD EUR

    alt Валюта не поддерживается
        CC-->>C: Выплата недоступна
    else Валюта поддерживается
        CC->>L: Запросить доступный остаток начислено минус сторно минус выплачено
        L-->>CC: Доступная сумма

        alt Доступная сумма больше нуля
            CC->>P: Инициировать выплату: сумма, валюта
            P-->>CC: Выплата подтверждена

            CC->>L: Зафиксировать выплату
            L-->>CC: Выплата зафиксирована

            CC->>N: Уведомить клиента: выплата исполнена
            CC->>R: Передать данные о выплате
        else Доступная сумма равна нулю
            CC-->>C: Выплата недоступна
        end
    end
```

### PlantUML

```plantuml
@startuml
autonumber
actor Клиент as C
participant "Cashback Core" as CC
participant Ledger as L
participant "Payout Service" as P
participant Notification as N
participant Reporting as R

C -> CC: Запрос выплаты кэшбэка
CC -> CC: Проверка валюты в {RUB, USD, EUR}

alt Валюта не поддерживается
    CC --> C: Выплата недоступна
else Валюта поддерживается
    CC -> L: Запросить доступный остаток: начислено - сторно - выплачено
    L --> CC: Доступная сумма

    alt Доступная сумма > 0
        CC -> P: Инициировать выплату: сумма, валюта
        P --> CC: Выплата подтверждена

        CC -> L: Зафиксировать выплату
        L --> CC: Выплата зафиксирована

        CC -> N: Уведомить клиента: выплата исполнена
        CC -> R: Передать данные о выплате
    else Доступная сумма = 0
        CC --> C: Выплата недоступна
    end
end
@enduml
```

---

## Самопроверка

| Требование BRD | Где отражено |
|---|---|
| Валюты `RUB`, `USD`, `EUR` | Начисление, выплата: проверка валюты |
| Лимит `500 000 RUB` | Начисление: `Limit Service`, минимум из расчёта и `500 000 RUB` |
| Комиссия `none` | Начисление: база = `amount` |
| Комиссия `fixed` | Начисление: база = `amount минус fixed` |
| Комиссия `percent` | Начисление: база = `amount минус percent` |
| `NEW` | Начисление: нет начисления; отмена/возврат: сторно не требуется |
| `PROCESSING` | Начисление: нет начисления; отмена/возврат: сторно не требуется |
| `COMPLETED` | Начисление: начисляется; отмена/возврат: сторно не требуется |
| `CANCELLED` | Отмена/возврат: нет начисления или сторно |
| `REFUNDED` | Отмена/возврат: сторно ранее начисленного |
| `FAILED` | Отмена/возврат: нет начисления или сторно |
| Округление до 2 знаков | Начисление: `Округлить до 2 знаков` |
| Идемпотентность | Начисление: проверка повторного начисления по `tx_id` |
| Уведомление клиента | Начисление, отмена/возврат, выплата |
| Отчётность | Начисление, отмена/возврат, выплата |
| Статусы транзакций | Используются только `NEW`, `PROCESSING`, `COMPLETED`, `CANCELLED`, `REFUNDED`, `FAILED` |
