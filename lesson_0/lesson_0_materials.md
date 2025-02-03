### **Методичка по Redis: Вводный урок**

---

#### **1. Установка Redis**
Установка и запуск Redis описаны в офицальной документации:  
[Redis Documentation - Download and Install](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)

---

#### **2. Базовые команды**

##### **Работа с ключами:**
- Установить значение:  
  ```bash
  SET key value
  ```
- получить значение:  
  ```bash
  GET key
  ```
- Удалить ключ :  
  ```bash
  DEL key
  ```
- Проверпить существование :  
  ```bash
  EXISTS key
  ```

##### **TTL и время жизни**
- Установить TTL:  
  ```bash
  EXPIRE key seconds
  ```
- проверить оставшееся время
  ```bash
  TTL key
  ```
- Удалить TTL:  
  ```bash
  PERSIST key
  ```

---

#### **3. Типы данных**

##### **Строки (Strings)**
- Увеличить значение на 1:  
  ```bash
  INCR key
  ```
- уменьшить значение на 1 :  
  ```bash
  DECR key
  ```

##### **Списки (Lists):**
- Добавить элементы в начало списка:  
  ```bash
  LPUSH list value1 value2
  ```
- Получить все элементы списка:  
  ```bash
  LRANGE list 0 -1
  ```
- Удалить первый элемент списка:  
  ```bash
  LPOP list
  ```

##### **Множества (Sets)**
- Добавить элементы в множество:  
  ```bash
  SADD set value1 value2
  ```
- Получить все элементы множества:  
  ```bash
  SMEMBERS set
  ```
- Проверить наличие элемента:  
  ```bash
  SISMEMBER set value
  ```

##### **Упорядоченные множества (Sorted Sets):**
- Добавить элементы с баллами:  
  ```bash
  ZADD zset score1 value1 score2 value2
  ```
- получить элементы с баллами:  
  ```bash
  ZRANGE zset 0 -1 WITHSCORES
  ```
- Удалить элемент:  
  ```bash
  ZREM zset value
  ```

##### **Хэши (Hashes)**

- Установить поля:  
  ```bash
  HSET hash field1 value1 field2 value2
  ```
- Получить все поля:  
  ```bash
  HGETALL hash
  ```
- Увеличить значение поля:  
  ```bash
  HINCRBY hash field increment
  ```

---

#### **4. Pub/Sub**
- Подписаться на канал:  
  ```bash
  SUBSCRIBE channel
  ```
- Опубликовать сообщение:  
  ```bash
  PUBLISH channel message
  ```

---

#### **5. Утилиты Redis**

- Получить все ключи (для небольших баз):  
  ```bash
  KEYS *
  ```
- Просмотреть ключи частями (для больших баз):  
  ```bash
  SCAN cursor
  ```

---

#### **6. Задачи для практики**

1. **Управление сессиями:**
   - Сохранить сессию пользователя с TTL:
     ```bash
     HSET session:123 user_id 1 status "active"
     EXPIRE session:123 3600
     ```

2. **Кэширование данных:**
   - Установить временный ключ :
     ```bash
     SET cache:data "Cached Value" EX 120
     ```

3. **Лидерборд:**
   - Добавить игроков и их очки :
     ```bash
     ZADD leaderboard 100 "Player1" 200 "Player2"
     ```
   - Получить топ игроков:
     ```bash
     ZRANGE leaderboard 0 -1 WITHSCORES
     ```
