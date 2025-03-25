#!/bin/bash

cd "$(dirname "$0")"

mkdir -p data

for port in {7000..7008}; do
  echo "Запуск Redis на порту $port..."
  redis-server configs/redis_node_$port.conf &
done

echo "Все инстансы Redis запущены."
