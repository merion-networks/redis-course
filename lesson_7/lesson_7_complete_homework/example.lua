local t = { "apple", "banana", "cherry" }
for _, v in ipairs(t) do
    redis.call("RPUSH", KEYS[1], v)
end