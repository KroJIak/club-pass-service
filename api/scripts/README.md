# Database Seed Script

Скрипт для заполнения базы данных тестовыми данными.

## Использование

### Через Docker

```bash
docker-compose exec api python -m api.scripts.seed_data
```

### Локально

```bash
cd api
python -m scripts.seed_data
```

## Что создается

- 2 тестовых события (Events)
- 4 типа билетов (TicketTypes) - по 2 для каждого события

Скрипт проверяет наличие данных и не перезаписывает существующие записи.

