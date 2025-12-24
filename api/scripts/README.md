# API Scripts

## seed_data.py

Скрипт для заполнения базы данных тестовыми данными.

### Запуск

```bash
# Вручную
python api/scripts/seed_data.py

# Через Docker
docker compose exec api python api/scripts/seed_data.py
```

---

**Примечание**: Проверка просроченных билетов теперь выполняется отдельным независимым сервисом `ticket-expiration-service`. См. `ticket-expiration-service/README.md` для подробностей.
