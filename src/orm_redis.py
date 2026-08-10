import redis.asyncio
from typing import NoReturn
from time import time


from src.config import settings

__all__ = 'RedisTools',


class RedisTools:
    __redis_connection = redis.asyncio.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


    @classmethod
    async def add_data(cls, user_id: str | int, value: str) -> NoReturn:
        condition = await cls.__redis_connection.exists(f'tg:{user_id}')
        if condition:
            all_values = await cls.__redis_connection.hgetall(f'tg:{user_id}')
            all_values = all_values.values()

            if value not in all_values:
                ids = await cls.__redis_connection.hgetall(f'tg:{user_id}')
                k = max([int(i) for i in ids.keys()])

                await cls.__redis_connection.hset(name=f'tg:{user_id}',
                                                  key=k + 1,
                                                  value=value
                                                  )
                await cls.__redis_connection.hexpire(f'tg:{user_id}', 375720, k + 1)
                for i in range(1, 6): await cls.__redis_connection.rpush(f'ins:logic:{i}', f'{int(time())} {user_id} {k + 1}')

        else:
            await cls.__redis_connection.hset(name=f'tg:{user_id}',
                                              key=0,
                                              value=value
                                              )
            await cls.__redis_connection.hexpire(f'tg:{user_id}', 375720, 0)

            for i in range(1, 6): await cls.__redis_connection.rpush(f'ins:logic:{i}', f'{int(time())} {user_id} {0}')


    @classmethod
    async def delete_item_from_memory_list(cls, list_id: int, index: int) -> NoReturn:
        memory_to_delete = await cls.__redis_connection.lindex(f'ins:logic:{list_id}', index)
        await cls.__redis_connection.lrem(f'ins:logic:{list_id}',
                                          1,
                                          memory_to_delete)

    @classmethod
    async def delete_item_from_hashtable(cls, user_id: int, remembering: str):
        all_data = await cls.__redis_connection.hgetall(f'tg:{user_id}')
        remembering = ' '.join([i for i in remembering.split()])

        for key in all_data.keys():
            if all_data[key] == remembering:
                await cls.__redis_connection.hdel(f'tg:{user_id}', key)

                for ind in range(1, 6):
                    list_len = await cls.__redis_connection.llen(f'ins:logic:{ind}')
                    all_list_data = await cls.__redis_connection.lrange(f'ins:logic:{ind}', 0, list_len)

                    for data in all_list_data:
                        if key in data:
                            await cls.__redis_connection.lrem(f'ins:logic:{ind}', 1, data)
                            break
                break


    @classmethod
    async def get_element_from_list(cls, list_id: int, index: int):
        element = await cls.__redis_connection.lindex(f'ins:logic:{list_id}', index)
        return element


    @classmethod
    async def get_remembering(cls, user_id: str, field: str):
        remembering = await cls.__redis_connection.hget(f'tg:{user_id}', field)
        return remembering
