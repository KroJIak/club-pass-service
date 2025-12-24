# API Scripts

## check_expired_tickets.py

Скрипт для проверки и пометки просроченных билетов.

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

### Автоматический запуск (cron)

Добавьте в crontab для запуска каждый час:

```bash
0 * * * * cd /path/to/club-pass-service && docker compose exec -T api python api/scripts/check_expired_tickets.py
```

Или для запуска каждые 30 минут:

```bash
*/30 * * * * cd /path/to/club-pass-service && docker compose exec -T api python api/scripts/check_expired_tickets.py
```

### Интеграция с системой

Скрипт можно интегрировать в:
- **Celery** с периодическими задачами
- **cron** для простого планирования
- **systemd timer** для более продвинутого планирования
- **Kubernetes CronJob** для контейнеризованных сред
