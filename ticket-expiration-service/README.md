# Ticket Expiration Service

Независимый сервис для автоматической проверки и пометки просроченных билетов.

## Описание

Сервис периодически проверяет билеты в базе данных и помечает их как просроченные, если они не были использованы или возвращены до 12:00 дня после мероприятия.

## Логика просрочки

- Если мероприятие в 00:00-11:59, билет истекает в 12:00 того же дня
- Если мероприятие в 12:00-23:59, билет истекает в 12:00 следующего дня

## Конфигурация

Переменные окружения (`.env`):

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=club_pass

# Service
CHECK_INTERVAL_MINUTES=30
LOG_LEVEL=INFO
```

## Запуск

### Локально

```bash
cd ticket-expiration-service
pip install -r requirements.txt
python -m src.main
```

### Docker

```bash
docker compose up ticket-expiration-service
```

## Архитектура

- **Независимый сервис**: Не зависит от API, имеет собственное подключение к БД
- **Периодическая проверка**: Использует APScheduler для автоматических проверок
- **Собственные модели**: SQLAlchemy модели для работы с БД
- **Логирование**: Подробное логирование всех операций

## Структура

```
ticket-expiration-service/
├── src/
│   ├── main.py              # Точка входа и scheduler
│   ├── config.py            # Конфигурация
│   ├── db.py                # Подключение к БД
│   ├── models/              # SQLAlchemy модели
│   │   ├── ticket.py
│   │   └── event.py
│   └── services/
│       └── expiration_service.py  # Логика проверки
├── requirements.txt
├── Dockerfile
└── README.md
```

