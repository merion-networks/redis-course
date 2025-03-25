-- BEGIN YOUR SOLUTION HERE
-- Скрипт для атомарного увеличения счётчика просмотров поста 
-- (в отсортированном множестве "post:views:ranking")
-- и сохранения post_id в историю просмотров (список "views:{user_id}") 
-- с ограничением её длины.
local post_id = ARGV[1]
local user_id = ARGV[2]
local history_limit = tonumber(ARGV[3])

redis.call("ZINCRBY", "post:views:ranking", 1, post_id)
redis.call("LPUSH", "views:" .. user_id, post_id)
redis.call("LTRIM", "views:" .. user_id, 0, history_limit - 1)

return true
-- END