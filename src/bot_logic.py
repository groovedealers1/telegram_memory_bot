from time import time

from src.orm_redis import RedisTools
from src.bot import bot_send_notification


__all__ = 'send_message',
__time_gap_for_sending_notification = [0, 60, 1200, 28800, 86400, 259200]


async def send_message():
    while True:
        for num in range(1, 6):
            call = await RedisTools.get_element_from_list(num, 0)
            if call is not None and time() >= int(call.split()[0]) + __time_gap_for_sending_notification[num]:
                tg_id = call.split()[1]
                field_id_hashtable = call.split()[2]
                text_message = await RedisTools.get_remembering(tg_id, field_id_hashtable)

                if '#' in text_message:
                    text = ' '.join([s for s in text_message.split() if '#' not in s])
                    await bot_send_notification(text, tg_id)
                    await RedisTools.delete_item_from_memory_list(num, 0)
                else:
                    await bot_send_notification(text_message, tg_id)
                    await RedisTools.delete_item_from_memory_list(num, 0)
