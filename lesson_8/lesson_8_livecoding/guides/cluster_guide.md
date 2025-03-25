# Настройка Redis Cluster

Эта инструкция показывает, как развернуть Redis Cluster на одной машине с 6 нодами:  
3 мастера и 3 реплики.

---

## Что нужно

- Redis версии 5.0 или выше
- Готовые конфиги:
  - `configs/7000/7000.conf`
  - `configs/7001/7001.conf`
  - `configs/7002/7002.conf`
  - `configs/7003/7003.conf`
  - `configs/7004/7004.conf`
  - `configs/7005/7005.conf`

Каждая конфигурация должна включать строки:

```ini
port <порт>
cluster-enabled yes
cluster-config-file nodes-<порт>.conf
cluster-node-timeout 5000
appendonly yes
dir ./configs/<порт>
bind 127.0.0.1
protected-mode no
```

---

## Шаг 1. Запуск всех нод

Запускаем все 6 Redis-серверов:

```bash
for port in 7000 7001 7002 7003 7004 7005; do
  redis-server configs/$port/$port.conf &
done
```

Проверь, что все работают:

```bash
redis-cli -p 7000 ping
```

---

## Шаг 2. Создание кластера

Создаём кластер командой:

```bash
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

Введи `yes`, когда спросят.

Что произойдёт:
- 7000, 7001, 7002 станут мастерами
- 7003, 7004, 7005 станут репликами

---

## Шаг 3. Проверка

Проверим состояние кластера:

```bash
redis-cli -c -p 7000 cluster info
redis-cli -c -p 7000 cluster nodes
```

Попробуем записать и прочитать ключ:

```bash
redis-cli -c -p 7000 set user:1 "alex"
redis-cli -c -p 7000 get user:1
```

Ключ будет автоматически записан на нужную ноду в зависимости от слота.

---

## Шаг 4. Завершение

Остановить все ноды:

```bash
pkill redis-server
```