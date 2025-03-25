local counter_key = KEYS[1]
local list_key = KEYS[2]
local increment = tonumber(ARGV[1])
local value = ARGV[2]

local new_counter = redis.call("INCRBY", counter_key, increment)
redis.call("LPUSH", list_key, value)

return {new_counter, "Value pushed to list" .. list_key}