import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

# Аналог SET my_key "Hello, Redis!"
r.set("my_key", "Hello, Redis!")

# Аналог GET my_key
value = r.get("my_key")
print(value)  # b'Hello, Redis!' (байты, если decode_responses=False)

# Аналог DEL my_key
r.delete("my_key")

# Аналог SET temp_key "temp_value" EX 60
r.set("temp_key", "temp_value", ex=60)

time.sleep(5) # Ждем 5 секунд

# Аналог TTL temp_key
time_left = r.ttl("temp_key")
print(time_left)  # 55

# Аналог SET my_key "Hello, Redis!"
r.set("my_new_key", "Hello, Redis again!")

# Установить время жизни в секундах (EXPIRE my_key 60)
r.expire("my_new_key", 60)

# Установить время жизни в миллисекундах (PEXPIRE my_key 5000)
r.pexpire("my_new_key", 5000)

# Снять время жизни (PERSIST my_key)
r.persist("my_new_key")

# Переименовать ключ (RENAME my_key new_key)
r.rename("my_new_key", "my_newest_key")