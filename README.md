# cashback-prompts

Репозиторий с промптами и сгенерированными артефактами для проекта «Ядро начисления кэшбэка».

## Цель

Подготовить цепочку промптов для LLM, по которой последовательно генерируются:

1. BRD — бизнес-требования.
2. Sequence-диаграмма — логика взаимодействия.
3. ER-диаграмма — структура данных.
4. OpenAPI Specification (OAS) — контракты API.

## Структура репозитория

cashback-prompts/
├── README.md
├── prompts.md
├── artifacts/
│ ├── brd.md
│ ├── sequence.md
│ ├── er.md
│ ├── openapi/
│ ├── openapi.yaml
│ │ └── note.md
├── scripts/
│ └── validation_OAS.py


## Ограничения проекта

| Параметр | Значение |
|---|---|
| Максимальный лимит | 500 000 RUB |
| Валюты | RUB, USD, EUR |
| Типы комиссий | fixed, percent, none |
| Статусы транзакций | NEW, PROCESSING, COMPLETED, CANCELLED, REFUNDED, FAILED |

## Валидация OpenAPI

## Установка:

```bash
pip install openapi-spec-validator pyyaml
```

## Запуск:

python scripts/validation_OAS.py artifacts/openapi.yaml

## Ожидаемый результат:

OAS valid
