import asyncio
from redis.asyncio.cluster import RedisCluster, ClusterNode

async def main():
    cluster = RedisCluster(
        startup_nodes=[
            ClusterNode(host="127.0.0.1", port=7000),
            ClusterNode(host="127.0.0.1", port=7001),
            ClusterNode(host="127.0.0.1", port=7002),
            ],
            decode_responses=True
    )

    await cluster.set("key_cluster", "value_cluster")
    print("Write in cluster")
    
    val = await cluster.get("key_cluster")
    print(f"Get from cluster {val}")

    await cluster.aclose()

if __name__ == '__main__':
    asyncio.run(main())
