## 1. Установка и запуск
- **Через APT**:  
  ```bash
  sudo apt update
  sudo apt install redis-server
  sudo systemctl start redis
  ```
- **Через Docker**:  
  ```bash
  docker run -d --name redis -p 6379:6379 redis
  ```
- **Проверка**:  
  ```bash
  redis-cli PING
  ```

---

## 2. Базовые операции
1. **Создать ключ**:  
   ```bash
   SET user "Вася"
   ```
2. **Проверить и удалить**:  
   ```bash
   EXISTS user
   DEL user
   EXISTS user
   ```
3. **Ключ с TTL**:  
   ```bash
   SET session "xyz" EX 10
   TTL session
   ```

---

## 3. Основные структуры данных
1. **Список**:  
   ```bash
   RPUSH mylist "one" "two" "three"
   LRANGE mylist 0 -1
   ```
2. **Хэш**:  
   ```bash
   HSET user:1 name "Иван" age 25
   HGETALL user:1
   ```
3. **Множество**:  
   ```bash
   SADD myset "apple" "banana" "cherry"
   SMEMBERS myset
   ```
4. **Отсортированное множество**:  
   ```bash
   ZADD scores 100 "Player1" 200 "Player2" 50 "Player3"
   ZRANGE scores 0 -1 WITHSCORES
   ```

---

## 4. Расширенные операции
1. **Несколько ключей сразу**:  
   ```bash
   MSET user:name "Вася" user:age "30" user:city "Москва"
   MGET user:name user:age user:city
   ```
2. **Скан ключей**:  
   ```bash
   KEYS *
   SCAN 0 MATCH user:* COUNT 10
   ```
3. **Транзакция**:  
   ```bash
   WATCH counter
   MULTI
   INCR counter
   EXEC
   ```

---

## 5. Pub/Sub
1. **Подписка**:  
   ```bash
   SUBSCRIBE news
   ```
2. **Публикация**:  
   ```bash
   PUBLISH news "Новость дня"
   ```
3. **Подписка по шаблону**:  
   ```bash
   PSUBSCRIBE news.*
   ```

---

## 6. Redis Insight
1. **Добавить подключение**: указать `Host`, `Port`, по умолчанию `6379`, пароль (если надо).  
2. **Смотреть ключи**: в разделе “Browser” будут все ключи.  
3. **Изменение**: выбрать ключ, нажать “Edit”, внести изменения.

*(Здесь конкретных CLI-команд нет, просто действия в GUI.)*

---

## 7. Безопасность
1. **Включить пароль** (через файл или параметр):
   - **redis.conf**:  
     ```
     requirepass mypassword
     ```
   - **Docker**:  
     ```bash
     docker run -d -p 6379:6379 redis redis-server --requirepass mypassword
     ```
2. **Подключение с паролем**:  
   ```bash
   redis-cli -a mypassword
   ```
3. **Redis Insight**: в настройках подключения указать `mypassword` и сохранить.

---

Это самая сжатая «шпаргалка» для проверки выполнения заданий.