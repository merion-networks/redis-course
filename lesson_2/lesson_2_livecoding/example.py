import redis

# Подключаемся к Redis (синхронный пример)
client = redis.Redis(host="localhost", port=6379, db=0)

# Ключ, который будет хранить наш счётчик
counter_key = "page_views"

# Инкрементируем значение на 1
new_value = client.incr(counter_key)
print(f"New counter value: {new_value}")

# Получаем текущее значение
current_value = client.get(counter_key)
print(f"Current counter value: {current_value}")

# Инкрементируем и устанавливаем время жизни ключа 60 секунд
new_value = client.incr(counter_key)
client.expire(counter_key, 60)  # через 60 сек ключ исчезнет

# Устанавливаем поля в хэше user:100
client.hset("user:100", "name", "Alice")
client.hset("user:100", "email", "alice@example.com")
client.hset("user:100", "age", 25)

# Получаем конкретное поле
email = client.hget("user:100", "email")
print(email)

# Получаем все поля
all_fields = client.hgetall("user:100")
print(all_fields)

# Удаляем конкретное поле (email)
client.hdel("user:100", "email")

# Проверяем, что поле удалилось
all_fields_after_delete = client.hgetall("user:100")
print(all_fields_after_delete)

# Удаляем весь хэш
client.delete("user:100")

# Проверяем, что хэша больше нет
exists = client.exists("user:100")
print(exists)  # 0 (если ключ удалён)
