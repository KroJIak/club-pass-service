# Club Pass Service

> Система продажи билетов для ночных клубов через Telegram-бота с веб-админ-панелью, автоматической обработкой платежей через ЮKassa, генерацией QR-кодов и управлением событиями.

## Содержание

- [Описание проекта](#описание-проекта)
- [Функциональность](#функциональность)
- [Быстрый старт](#быстрый-старт)
- [Архитектура системы](#архитектура-системы)
- [Варианты запуска](#варианты-запуска)
- [Конфигурация](#конфигурация)
- [Разработка](#разработка)
- [Документация](#документация)

## Описание проекта

**Club Pass Service** — это комплексная микросервисная система для ночных клубов, которая позволяет:

* **Продажа билетов через Telegram**: Удобная покупка билетов в несколько шагов прямо в Telegram-боте
* **Оплата через ЮKassa**: Интеграция с платежной системой ЮKassa для безопасных транзакций
* **QR-коды**: Автоматическая генерация уникальных QR-кодов для каждого билета
* **Веб-админ-панель**: Полнофункциональная панель управления для менеджеров клуба
* **Сканирование QR-кодов**: Встроенный сканер для проверки билетов на входе
* **Автоматизация**: Автоматическая обработка просроченных билетов и деактивация прошедших событий
* **Мультиязычность**: Поддержка русского и английского языков
* **Промокоды**: Система скидок и промокодов для акций

## Функциональность

### Для клиентов (Telegram-бот)

- 🎫 **Покупка билетов**: Выбор события, типа билета, количества с оплатой через ЮKassa
- 📱 **Мои билеты**: Просмотр всех купленных билетов с QR-кодами
- 🔄 **Возврат билетов**: Возможность вернуть билет с возвратом средств
- 📅 **Ближайшие события**: Просмотр предстоящих мероприятий
- ℹ️ **Информация о клубе**: Контакты, адрес, правила
- 💬 **Поддержка**: Связь с администрацией клуба

### Для администраторов (Веб-панель)

- 📊 **Управление событиями**: Создание, редактирование, деактивация мероприятий
- 🎟️ **Управление типами билетов**: Настройка цен, лимитов, описаний
- 👥 **Управление пользователями**: Просмотр списка пользователей и их данных
- 🎫 **Управление билетами**: Просмотр всех билетов, фильтрация, изменение статусов
- 💰 **Управление заказами**: Просмотр заказов, история платежей
- 🎁 **Промокоды**: Создание и управление промокодами
- ⚙️ **Настройки истечения**: Конфигурация автоматической обработки просроченных билетов
- 📱 **Сканер QR-кодов**: Проверка билетов при входе через веб-камеру
- 📈 **Аналитика**: Статистика продаж и посещаемости

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- ЮKassa Shop ID и Secret Key (для обработки платежей)

### Стандартный запуск (Docker Compose)

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd club-pass-service
   ```

2. **Создайте файл `.env` на основе `.env.example`:**
   ```bash
   cp .env.example .env
   ```

3. **Настройте переменные окружения** (см. [Конфигурация](#конфигурация)):
   - `TELEGRAM_BOT_TOKEN` - токен вашего Telegram-бота
   - `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY` - данные для ЮKassa
   - `ADMIN_USERNAME` и `ADMIN_PASSWORD` - учетные данные для админ-панели
   - Остальные параметры при необходимости

4. **Запустите все сервисы:**
   ```bash
   # Для ARM64 (Raspberry Pi, Apple Silicon)
   docker compose -f docker-compose-arm64.yml up -d
   
   # Для AMD64 (обычные серверы)
   docker compose -f docker-compose-amd64.yml up -d
   
   # Без CloudPub (локальная разработка)
   docker compose -f docker-compose-without-cloudpub.yml up -d
   ```

5. **Проверьте статус сервисов:**
   ```bash
   docker compose ps
   ```

6. **Откройте админ-панель:**
   - Локально: `http://localhost:8101` (или порт из `ADMIN_PORT`)
   - Или по домену, если настроен CloudPub

## Архитектура системы

Система состоит из следующих микросервисов:

| Сервис | Описание | Порт | Технологии |
|--------|----------|------|------------|
| **API** | REST API для всех сервисов | 8000 | Python FastAPI |
| **Bot** | Telegram-бот для клиентов | - | Python Aiogram |
| **Admin Panel** | Веб-админ-панель | 8101 | React + TypeScript + MUI |
| **Expiration Service** | Автоматическая обработка просроченных билетов | 8001 | Python FastAPI + APScheduler |
| **PostgreSQL** | База данных | 5432 | PostgreSQL 15 |

### Основные компоненты

- **API** (`api/`): Основной REST API с эндпоинтами для бота, админ-панели и внешних интеграций
- **Bot** (`bot/`): Telegram-бот на Aiogram с поддержкой мультиязычности
- **Admin Panel** (`admin-panel/`): React-приложение с Material-UI для управления системой
- **Expiration Service** (`expiration-service/`): Независимый сервис для автоматической обработки билетов и событий
- **Mini App** (`mini-app/`): Telegram Mini App (в разработке)

### База данных

- **PostgreSQL 15**: Основная база данных
- **Автоматическая инициализация**: При первом запуске создаются все необходимые таблицы
- **Миграции**: Поддержка Alembic для управления схемой БД

## Варианты запуска

### Стандартный запуск (с CloudPub)

CloudPub позволяет публиковать админ-панель в интернете без настройки домена и SSL.

**Для ARM64 (Raspberry Pi, Apple Silicon):**
```bash
docker compose -f docker-compose-arm64.yml up -d
```

**Для AMD64 (обычные серверы):**
```bash
docker compose -f docker-compose-amd64.yml up -d
```

**Требования:**
- Переменная `CLOUDPUB_TOKEN` в `.env` файле
- CloudPub автоматически создаст публичный URL для админ-панели

### Без CloudPub (локальная разработка)

Для локальной разработки или если у вас уже есть настроенный домен:

```bash
docker compose -f docker-compose-without-cloudpub.yml up -d
```

**Доступ:**
- Админ-панель: `http://localhost:8101` (или порт из `ADMIN_PORT`)
- API: `http://localhost:8000`
- API документация: `http://localhost:8000/docs`

## Конфигурация

Основные переменные окружения (см. `.env.example`):

### База данных
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=club_pass
```

### API
```env
API_PORT=8000
DEBUG=false
CORS_ORIGINS=*
```

### Telegram Bot
```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
CLUB_NAME=Night Club
CLUB_ADDRESS=Москва, ул. Примерная, 1
CLUB_PHONE=
CLUB_EMAIL=
```

### Админ-панель
```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ADMIN_PORT=8101
```

### Expiration Service
```env
EXPIRATION_CHECK_INTERVAL=30  # Интервал проверки в минутах
EXPIRATION_API_PORT=8001
```

### CloudPub (опционально)
```env
CLOUDPUB_TOKEN=your-cloudpub-token-here
```

### ЮKassa (для обработки платежей)
```env
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
```

## Разработка

### Структура проекта

```
club-pass-service/
├── api/                    # REST API (FastAPI)
│   ├── api/v1/            # API эндпоинты
│   ├── core/              # Конфигурация, БД, аутентификация
│   ├── models/            # SQLAlchemy модели
│   ├── repositories/      # Репозитории для работы с БД
│   ├── services/          # Бизнес-логика
│   └── scripts/           # Скрипты (инициализация БД, seed данные)
├── bot/                    # Telegram-бот (Aiogram)
│   ├── handlers/          # Обработчики команд и сообщений
│   ├── keyboards/         # Клавиатуры для бота
│   ├── services/          # Сервисы бота
│   └── lang/              # Файлы локализации
├── admin-panel/           # Веб-админ-панель (React + TypeScript)
│   └── src/
│       ├── pages/         # Страницы приложения
│       ├── components/    # React компоненты
│       └── services/      # API клиенты
├── expiration-service/    # Сервис обработки просроченных билетов
│   └── src/
│       ├── services/      # Логика обработки
│       └── api.py         # FastAPI для обновления настроек
├── mini-app/              # Telegram Mini App (в разработке)
├── docker/                # Dockerfile'ы
├── cloudpub-config/       # Конфигурация CloudPub
└── docs/                  # Документация
```

### Локальная разработка

1. **Установите зависимости:**
   ```bash
   # API
   cd api
   pip install -r requirements.txt
   
   # Bot
   cd ../bot
   pip install -r requirements.txt
   
   # Admin Panel
   cd ../admin-panel
   npm install
   ```

2. **Настройте переменные окружения** (см. `.env.example`)

3. **Запустите базу данных:**
   ```bash
   docker compose up db -d
   ```

4. **Инициализируйте базу данных:**
   ```bash
   docker compose run --rm db-init
   ```

5. **Запустите сервисы:**
   ```bash
   # API
   cd api
   uvicorn api.main:app --reload
   
   # Bot
   cd bot
   python -m bot.main
   
   # Admin Panel
   cd admin-panel
   npm run dev
   ```

### Скрипты

- **Инициализация БД**: `python -m api.scripts.init_db` - создает таблицы при первом запуске
- **Seed данные**: `python -m api.scripts.seed_data` - заполняет БД тестовыми данными

## Документация

Подробная документация находится в директории `docs/`:

- **PROJECT_DESCRIPTION.md** - Техническое задание и описание функциональности
- **PROJECT_STRUCTURE.md** - Архитектура и принципы построения системы
- **CRUD_OPERATIONS.md** - Описание CRUD операций
- **yookassa/** - Документация по интеграции с ЮKassa

### API Документация

После запуска API доступна интерактивная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Решение проблем

### База данных не инициализируется

Убедитесь, что сервис `db-init` успешно завершился:
```bash
docker compose logs db-init
```

### CORS ошибки

Проверьте настройку `CORS_ORIGINS` в `.env`. Для локальной разработки используйте:
```env
CORS_ORIGINS=http://localhost:8101
```

### Telegram бот не отвечает

1. Проверьте правильность `TELEGRAM_BOT_TOKEN`
2. Убедитесь, что бот запущен: `docker compose logs bot`
3. Проверьте подключение к API: `docker compose logs api`

### Платежи не обрабатываются

1. Проверьте настройки ЮKassa в `.env`
2. Убедитесь, что webhook URL правильно настроен в личном кабинете ЮKassa
3. Проверьте логи API: `docker compose logs api`

## Технологии

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Aiogram
- **Frontend**: React 18, TypeScript, Material-UI, Vite
- **Database**: PostgreSQL 15
- **Containerization**: Docker, Docker Compose
- **Payment**: ЮKassa API
- **QR Codes**: qrcode, Pillow
- **Scheduling**: APScheduler

## Лицензия

Этот проект является приватным и предназначен для внутреннего использования.

## Контакты

Для вопросов и предложений обращайтесь к разработчикам проекта.

---

**Примечание**: При первом запуске система автоматически создаст все необходимые таблицы в базе данных. Убедитесь, что переменные окружения настроены правильно перед запуском.
