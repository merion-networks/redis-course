## Задача: имитация обработки заказов с 3 микросервисами

### Сценарий

1. Пользователь отправляет запрос в основной сервис (FastAPI «orders») – например, `POST /orders/create`.
2. «orders»-сервис:
   - Сохраняет заказ в своей БД (можно имитировать in-memory словарь).
   - Отправляет три «задачи» / «события» в Redis:
     1. «Печать чека» (cheque service).
     2. «Обновить склад» (warehouse service).
     3. «Отправить email» (notification service).
3. Три микросервиса (cheque, warehouse, notify) слушают Redis в фоновом режиме:
   - Получают соответствующие события / задачи (Queue или Streams).
   - Выполняют «обработку» (имитируют работу: печать PDF, обновление склада, отправка email).
   - Логируют/выводят в консоль, что обработали задачу.

4. Проверка:
   - При вызове `POST /orders/create`, увидеть, что в логе микросервисов появляются соответствующие сообщения о «чеке», «складе», «email».

---

## Структура проекта

1. main_service (FastAPI «orders»)  
   - `orders_main.py`:  
     - Endpoint `POST /orders/create` → генерирует `order_id` (просто int) + user_id (из тела запроса).  
     - После «сохранения» (в in-memory dict), отправляет в Redis три сообщения (cheque, warehouse, email).

2. cheque_service (скрипт)  
   - Слушает Redis-очередь (или Stream) `queue:cheque` (или `stream:cheque`).  
   - При получении задачи (order_id, user_id) → имитирует «генерацию PDF чека». Печатает «[cheque_service] Generated cheque for order 123…».

3. warehouse_service (скрипт)  
   - Слушает `queue:warehouse` (или `stream:warehouse`).  
   - При получении «update stock for order …», выводит «[warehouse_service] Stock updated for order 123…».

4. notify_service (скрипт)  
   - Слушает `queue:notify` (или `stream:notify`).  
   - При получении «send email to user …», выводит «[notify_service] Email sent…».


## Задание

1. Развернуть эти 4 сервисных скрипта:
   - main_service (FastAPI) – создаёт заказы.
   - 3 consumer’а (cheque, warehouse, notify) – слушают Redis.
2. Lists вариант или Streams вариант (ваш выбор). Если Streams – создайте consumer groups.
3. Проверить:
   - При `POST /orders/create`, все 3 consumer’а получают задачи.  
   - Логи в консолях показывают «имитацию» обработки.
