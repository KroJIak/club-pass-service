# CRUD Operations Overview

Документ описывает все доступные CRUD операции в API.

## Events (События)

### READ
- `GET /api/v1/events` - Список активных событий
- `GET /api/v1/events/{event_id}` - Детали события
- `GET /api/v1/events/{event_id}/ticket-types` - Типы билетов для события

### CREATE (Admin)
- `POST /api/v1/admin/events` - Создать новое событие

### UPDATE (Admin)
- `PUT /api/v1/admin/events/{event_id}` - Обновить событие

### DELETE (Admin)
- `DELETE /api/v1/admin/events/{event_id}` - Деактивировать событие (soft delete)

## TicketTypes (Типы билетов)

### READ
- `GET /api/v1/events/{event_id}/ticket-types` - Список типов билетов для события

### CREATE (Admin)
- `POST /api/v1/admin/ticket-types` - Создать новый тип билета

### UPDATE (Admin)
- `PUT /api/v1/admin/ticket-types/{ticket_type_id}` - Обновить тип билета

### DELETE (Admin)
- `DELETE /api/v1/admin/ticket-types/{ticket_type_id}` - Деактивировать тип билета (soft delete)

## Tickets (Билеты)

### READ
- `GET /api/v1/users/{user_id}/tickets` - Список билетов пользователя
- `GET /api/v1/tickets/{ticket_id}` - Детали билета

### CREATE
- Автоматически создаются при успешной оплате через `PaymentService.handle_payment_success()`

### UPDATE
- `POST /api/v1/tickets/{ticket_id}/refund` - Вернуть билет (пометить как refunded)
- `POST /api/v1/tickets/{ticket_id}/mark-used` - Пометить билет как использованный

### DELETE
- Билеты не удаляются (только помечаются как refunded или cancelled)

## Users (Пользователи)

### READ
- Через репозиторий: `UserRepository.get_by_telegram_id()`, `UserRepository.get_by_id()`

### CREATE
- Автоматически создаются через `UserRepository.get_or_create()` при первом обращении

### UPDATE
- Частично через `get_or_create()` (обновление username, first_name, last_name)

### DELETE
- Пользователи не удаляются (CASCADE удаление при удалении связанных записей)

## Payments (Платежи)

### READ
- Через репозиторий: `PaymentRepository.get_by_id()`, `PaymentRepository.get_by_order_id()`

### CREATE
- Автоматически создаются через `PaymentService.create_payment_invoice()`

### UPDATE
- `PaymentRepository.update_status()` - Обновление статуса платежа

### DELETE
- Платежи не удаляются (исторические данные)

## Orders (Заказы)

### READ
- Через репозиторий: `OrderRepository.get_by_order_id()`

### CREATE
- Автоматически создаются через `OrderRepository.create()` при создании заказа

### UPDATE
- `OrderRepository.link_payment()` - Связывание заказа с платежом

### DELETE
- Заказы не удаляются (исторические данные)

## Примечания

- **Soft Delete**: События и типы билетов не удаляются физически, а помечаются как неактивные (`is_active=False`)
- **Автоматическое создание**: Пользователи и билеты создаются автоматически при необходимости
- **Исторические данные**: Платежи и заказы не удаляются для сохранения истории транзакций

