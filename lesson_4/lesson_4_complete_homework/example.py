import asyncio
import redis.asyncio as aioredis

# Ключ, под которым храним наше упорядоченное множество
LEADERBOARD_KEY = "leaderboard_example"

async def main():
    # Подключаемся к Redis
    client = aioredis.Redis(host="localhost", port=6379, decode_responses=True)

    # 1) ZADD: Добавление элементов с определённым score
    # CLI:   ZADD leaderboard_example 100 userA 200 userB 150 userC
    print("=== 1) ZADD ===")
    await client.zadd(LEADERBOARD_KEY, {"userA": 100, "userB": 200, "userC": 150})
    # Этот вызов добавляет (или обновляет) 3 элемента: userA, userB, userC

    # 2) ZINCRBY: Увеличение score
    # CLI:   ZINCRBY leaderboard_example 50 userA
    print("\n=== 2) ZINCRBY ===")
    new_score = await client.zincrby(LEADERBOARD_KEY, 50, "userA")
    print(f"userA new score after +50 => {new_score}")

    # 3) ZSCORE: Узнать текущий score элемента
    # CLI:   ZSCORE leaderboard_example userA
    print("\n=== 3) ZSCORE ===")
    scoreA = await client.zscore(LEADERBOARD_KEY, "userA")
    print(f"userA current score => {scoreA}")

    # 4) ZRANK: Узнать позицию (по возрастанию score)
    # CLI:   ZRANK leaderboard_example userB
    print("\n=== 4) ZRANK ===")
    rankB = await client.zrank(LEADERBOARD_KEY, "userB")  # 0-based индекс, 0 = наименьший score
    print(f"userB rank by ascending order => {rankB}")

    # 5) ZREVRANK: Позиция в убывающем порядке (0 = лидер)
    # CLI:   ZREVRANK leaderboard_example userB
    print("\n=== 5) ZREVRANK ===")
    rev_rankB = await client.zrevrank(LEADERBOARD_KEY, "userB")
    print(f"userB rank by descending order => {rev_rankB}")

    # 6) ZRANGE: Получить элементы в порядке возрастания score
    # CLI:   ZRANGE leaderboard_example 0 -1 WITHSCORES
    print("\n=== 6) ZRANGE ===")
    ascending_list = await client.zrange(LEADERBOARD_KEY, 0, -1, withscores=True)
    print(f"Ascending order full list => {ascending_list}")

    # 7) ZREVRANGE: Элементы в порядке убывания (топ-лист)
    # CLI:   ZREVRANGE leaderboard_example 0 2 WITHSCORES
    print("\n=== 7) ZREVRANGE (top 3) ===")
    descending_top = await client.zrevrange(LEADERBOARD_KEY, 0, 2, withscores=True)
    print(f"Top 3 by descending score => {descending_top}")

    # 8) ZRANGEBYSCORE: Выборка по диапазону score
    # CLI:   ZRANGEBYSCORE leaderboard_example 100 200 WITHSCORES
    print("\n=== 8) ZRANGEBYSCORE ===")
    between_100_200 = await client.zrangebyscore(LEADERBOARD_KEY, 100, 200, withscores=True)
    print(f"Elements with score 100..200 => {between_100_200}")

    # 9) ZREM: Удаляем элемент
    # CLI:   ZREM leaderboard_example userC
    print("\n=== 9) ZREM ===")
    removed_count = await client.zrem(LEADERBOARD_KEY, "userC")
    print(f"Removed userC => {removed_count} (0 or 1)")

    # Проверяем, что userC удалён
    new_list = await client.zrange(LEADERBOARD_KEY, 0, -1, withscores=True)
    print(f"After removal => {new_list}")

    # 10) ZREMRANGEBYRANK: Удаляем диапазон по позициям
    # CLI:   ZREMRANGEBYRANK leaderboard_example 0 0  (удаляем самого последнего)
    print("\n=== 10) ZREMRANGEBYRANK ===")
    # Например, оставим только 1 элемент (удаляем всё с rank >= 1)
    removed_count = await client.zremrangebyrank(LEADERBOARD_KEY, 1, -1)
    print(f"Removed (rank >=1) => {removed_count}")

    # Смотрим, что осталось
    final_list = await client.zrange(LEADERBOARD_KEY, 0, -1, withscores=True)
    print(f"Final list => {final_list}")

    # 11) Дополнительно: ZCARD - узнать, сколько элементов в ZSET
    # CLI:   ZCARD leaderboard_example
    count = await client.zcard(LEADERBOARD_KEY)
    print(f"\n=== 11) ZCARD ===\nCurrent total => {count}")

    # Закрываем соединение
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
