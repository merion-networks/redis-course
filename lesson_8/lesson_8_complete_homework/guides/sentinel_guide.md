# Автоматическое переключение Redis с помощью Sentinel

## Что мы будем делать

- Запустим мастер Redis на порту `6380`
- Запустим реплику на порту `6379`
- Настроим Sentinel на порту `26379`, чтобы он следил за мастером

---

## Шаг 1. Конфигурация Redis-мастера

Создай файл `redis_6380.conf`:

```ini
port 6380
dir /home/имя_пользователя/redis-sentinel/6380
appendonly yes
```

---

## Шаг 2. Конфигурация Redis-реплики

Создай файл `redis_6379.conf`:

```ini
port 6379
dir /home/имя_пользователя/redis-sentinel/6379
appendonly yes
replicaof 127.0.0.1 6380
```

---

## Шаг 3. Конфигурация Sentinel

Создай файл `sentinel.conf`:

```ini
port 26379
dir /home/имя_пользователя/redis-sentinel/sentinel
sentinel monitor mymaster 127.0.0.1 6380 1
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
protected-mode no
```

Пояснение:
- `mymaster` — имя мастера
- `127.0.0.1 6380` — адрес мастера
- `1` — кворум (минимум 1 Sentinel должен подтвердить сбой)

---

## Шаг 4. Запуск всех компонентов

Мастер:

```bash
redis-server redis_6380.conf
```

Реплика:

```bash
redis-server redis_6379.conf
```

Sentinel:

```bash
redis-server sentinel.conf --sentinel
```

---

## Шаг 5. Проверка

Проверить, кого Sentinel считает мастером:

```bash
redis-cli -p 26379 sentinel get-master-addr-by-name mymaster
```

Ожидается:

```
1) "127.0.0.1"
2) "6380"
```

---

## Шаг 6. Симуляция отказа

Останови мастер:

```bash
sudo systemctl stop redis
```

Через 5 секунд Sentinel выберет реплику (6379) новым мастером.

---

## Шаг 7. Проверка

Подключись к реплике (теперь она мастер):

```bash
redis-cli -p 6379 INFO replication
```

Ожидается:

```
role:master
```
