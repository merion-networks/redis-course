# README: Master-Replica FastAPI App

1. **Описание**  
   Приложение на FastAPI, работающее с Redis в режиме master-replica, управляемом через Sentinel.  
   Чтение идёт с реплики, запись – в мастер.

2. **Состав репозитория**  
   ```
   master_replica_app/
   ├── configs/
   │   ├── redis_master.conf
   │   ├── redis_replica.conf
   │   └── sentinel.conf
   └── main.py
   ```

3. **Настройка Redis**
   Из директории `homework/master_replica_app`:
   - Запустите мастер:  
     ```bash
     redis-server configs/redis_master.conf
     ```
   - Запустите реплику:  
     ```bash
     redis-server configs/redis_replica.conf
     ```
   - Запустите Sentinel:  
     ```bash
     redis-server configs/sentinel.conf --sentinel
     ```

4. **Запуск приложения**  
   ```bash
   cd master_replica_app
   uvicorn main:app --reload
   ```

5. **Использование**  
   - **POST** `/set?key=xxx&value=yyy` – Запись данных в мастер.  
   - **GET** `/get?key=xxx` – Чтение данных с реплики.

6. **Проверка**  
   - Остановите мастер и убедитесь, что Sentinel переведёт реплику в мастер.  
   - Приложение продолжит корректно работать (запись/чтение).

7. **Примечания**  
   - Порты и IP указаны в конфиге Sentinel (`mymaster`).  
   - Убедитесь, что все экземпляры Redis и Sentinel слушают нужные порты без конфликтов.
