-- Внимание! Данный скрипт неисполняемый и является примером синтаксиса
-- для Lua-скриптов
-- Переменные
local x = 10  -- Локальная переменная

-- Условный оператор
if x > 0 then
    return "Positive"
else
    return "Non-positive"
end

-- Цикл: добавляем числа в список
for i = 1, 5 do
    redis.call("LPUSH", KEYS[1], i)
end

-- Функция умножения двух чисел
local function multiply(a, b)
    return a * b
end
redis.call("SET", "res", multiply(3,4))
-- Сохраняем результат умножения 3 * 4 в ключ "res"

-- Таблица (структура данных Lua, аналог словаря)
local t = { a = 1, b = 2 }
return t
-- Redis вернёт массив, так как ключи не строковые

-- Итерация по таблице
local t = { "apple", "banana", "cherry" }
for _, v in ipairs(t) do
    redis.call("RPUSH", KEYS[1], v)
end
-- Добавляет элементы в список Redis, используя Lua-таблицу.

-- Проверка существования ключа
if redis.call("EXISTS", KEYS[1]) == 1 then
    return redis.call("GET", KEYS[1])
else
    return "Key does not exist"
end

-- Инкремент с ограничением
local current = redis.call("INCR", KEYS[1])
if current > tonumber(ARGV[1]) then
    return redis.call("DECR", KEYS[1])
    -- Откатываем, если превышен лимит
else
    return current
end
