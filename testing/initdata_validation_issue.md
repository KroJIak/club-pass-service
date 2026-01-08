# Проблема с валидацией Telegram Mini App initData

## Описание проблемы

Валидация подписи `initData` от Telegram Mini App не проходит - вычисленный хеш не совпадает с полученным хешем из параметра `hash`.

## Текущая реализация

### Файл: `api/utils/telegram_validation.py`

Алгоритм валидации:

1. **Парсинг initData:**
   - Разбиваем строку по `&`
   - Извлекаем ключ-значение пары
   - Сохраняем оригинальные URL-encoded значения для валидации
   - Декодируем значения для извлечения данных

2. **Извлечение hash:**
   - Удаляем параметр `hash` из параметров
   - Удаляем параметр `signature` (отдельная подпись, не участвует в валидации hash)

3. **Создание data_check_string:**
   - Сортируем параметры по ключу (алфавитный порядок)
   - Объединяем в строку формата `key=value\nkey=value`
   - **Используем оригинальные URL-encoded значения**

4. **Вычисление секретного ключа:**
   ```python
   secret_key = HMAC-SHA256('WebAppData', bot_token)
   ```

5. **Вычисление хеша:**
   ```python
   calculated_hash = HMAC-SHA256(secret_key, data_check_string)
   ```

6. **Сравнение:**
   - Сравниваем `calculated_hash` с `received_hash` из initData

### Токен бота

Используется токен staff бота: `8265427799:AAHF0hjKocDBdjRLci8fgRQxDDr5rjm4hio`

## Примеры из логов

### Пример 1

**initData (полный):**
```
user=%7B%22id%22%3A1250991011%2C%22first_name%22%3A%22Andrey%22%2C%22last_name%22%3A%22Rastopshin%22%2C%22username%22%3A%22krojiak%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fb0y5ECTXhbq3-YgnvqbXPZg9zu1p0nC6YVjyiwi-XJY.svg%22%7D&chat_instance=-4470602365613344272&chat_type=sender&auth_date=1767903351&signature=5XZRS3h9yK_o3_9ujst0aefxna2mIWrdYSdxYZsZgFuzDbpStZXwsBW6OBGfm7fGfEzHzyIpk1qrhMQRS965Aw&hash=051e1d70bd1f4472c7ef67a317c2a14eb12f615fffb72a2c73a0ce14d1705bb8
```

**Параметры после парсинга:**
- `user`: `%7B%22id%22%3A1250991011%2C%22first_name%22%3A%22Andrey%22%2C%22last_name%22%3A%22Rastopshin%22%2C%22username%22%3A%22krojiak%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fb0y5ECTXhbq3-YgnvqbXPZg9zu1p0nC6YVjyiwi-XJY.svg%22%7D`
- `chat_instance`: `-4470602365613344272`
- `chat_type`: `sender`
- `auth_date`: `1767903351`
- `signature`: `5XZRS3h9yK_o3_9ujst0aefxna2mIWrdYSdxYZsZgFuzDbpStZXwsBW6OBGfm7fGfEzHzyIpk1qrhMQRS965Aw` (исключается)
- `hash`: `051e1d70bd1f4472c7ef67a317c2a14eb12f615fffb72a2c73a0ce14d1705bb8` (извлекается)

**data_check_string (после сортировки, URL-encoded значения):**
```
auth_date=1767903351
chat_instance=-4470602365613344272
chat_type=sender
user=%7B%22id%22%3A1250991011%2C%22first_name%22%3A%22Andrey%22%2C%22last_name%22%3A%22Rastopshin%22%2C%22username%22%3A%22krojiak%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fb0y5ECTXhbq3-YgnvqbXPZg9zu1p0nC6YVjyiwi-XJY.svg%22%7D
```

**Результаты:**
- **Полученный hash:** `051e1d70bd1f4472c7ef67a317c2a14eb12f615fffb72a2c73a0ce14d1705bb8`
- **Вычисленный hash:** `b05cb9beb3593c2b2198495bf71947ffd1167a81a0c3982c0d5e9068e5e6dc83`
- **Совпадение:** ❌ НЕТ

**Secret key (hex, первые 40 символов):** `758d9e19a12a10982a207b997ffe6e9d61e231e7...`

**Длина data_check_string:** 323 символа

## Что было испробовано

1. ✅ **Использование URL-encoded значений** (текущая реализация)
   - Хеши не совпадают

2. ✅ **Использование декодированных значений**
   - Хеши не совпадают

3. ✅ **Исключение параметра `signature`**
   - Параметр исключается из валидации

4. ✅ **Проверка с основным токеном бота**
   - Хеши не совпадают ни с одним токеном

5. ✅ **Проверка формата data_check_string**
   - Используется `\n` как разделитель
   - Параметры отсортированы по ключу

## Код валидации

```python
def validate_telegram_init_data(init_data: str, bot_token: str) -> Dict[str, str]:
    # Парсинг
    params_raw = {}  # URL-encoded
    params_decoded = {}  # Decoded
    
    for pair in init_data.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            params_raw[key] = value
            params_decoded[key] = unquote(value)
    
    # Извлечение hash
    received_hash = params_raw.pop('hash')
    params_raw.pop('signature', None)  # Исключаем signature
    params_decoded.pop('hash', None)
    params_decoded.pop('signature', None)
    
    # Создание data_check_string с URL-encoded значениями
    sorted_params = sorted(params_raw.items(), key=lambda x: x[0])
    data_check_string = '\n'.join([f"{key}={value}" for key, value in sorted_params])
    
    # Создание секретного ключа
    secret_key = hmac.new(
        'WebAppData'.encode('utf-8'),
        bot_token.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Вычисление хеша
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Сравнение
    if calculated_hash != received_hash:
        raise ValueError("Invalid signature")
```

## Вопросы для профессионала

1. **Правильно ли использовать URL-encoded значения** для создания `data_check_string`, или нужно декодировать?

2. **Правильно ли исключать параметр `signature`** из валидации hash, или он должен участвовать?

3. **Правильный ли формат `data_check_string`?** Используется `\n` как разделитель, параметры отсортированы по ключу.

4. **Правильно ли вычисляется секретный ключ?** `HMAC-SHA256('WebAppData', bot_token)` - где `'WebAppData'` это ключ, а `bot_token` это сообщение?

5. **Может ли быть проблема в токене бота?** Используется токен staff бота, который открывает мини-приложение. Нужен ли токен того бота, который создал мини-приложение в BotFather?

6. **Есть ли какие-то особенности** в обработке параметров (например, пустые значения, специальные символы)?

## Ссылки на документацию

- [Telegram Bot API - Web Apps](https://core.telegram.org/bots/webapps)
- [Validating Data Received via the Mini App](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)

## Окружение

- Python 3.11
- FastAPI
- Библиотеки: `hmac`, `hashlib`, `urllib.parse`

## Дополнительная информация

Мини-приложение открывается через staff бота (токен: `8265427799:AAHF0hjKocDBdjRLci8fgRQxDDr5rjm4hio`).

В initData присутствуют параметры:
- `user` - JSON объект с данными пользователя (URL-encoded)
- `chat_instance` - ID чата
- `chat_type` - тип чата (`sender`)
- `auth_date` - timestamp авторизации
- `signature` - отдельная подпись Telegram
- `hash` - подпись для валидации

