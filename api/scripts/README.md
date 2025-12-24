# API Scripts

## check_expired_tickets.py

Скрипт для одноразовой проверки и пометки просроченных билетов.

### Логика просрочки

- Если мероприятие в 00:00-11:59, билет истекает в 12:00 того же дня
- Если мероприятие в 12:00-23:59, билет истекает в 12:00 следующего дня

### Запуск

```bash
# Вручную
python api/scripts/check_expired_tickets.py

# Через Docker
docker compose exec api python api/scripts/check_expired_tickets.py
```

## ticket-expiration-worker (Рекомендуется)

Отдельный фоновый сервис, который постоянно работает и автоматически проверяет просроченные билеты.

### Запуск

```bash
# Через Docker Compose (автоматически запускается)
docker compose up ticket-expiration-worker

# Или как часть всех сервисов
docker compose up
```

### Конфигурация

Интервал проверки настраивается через переменную окружения `EXPIRATION_CHECK_INTERVAL_MINUTES` (по умолчанию 30 минут).

### Логи

Логи сервиса можно просмотреть через:

```bash
docker compose logs -f ticket-expiration-worker
```

### Остановка

```bash
docker compose stop ticket-expiration-worker
```
