import logging

from src.config import settings
from src.orm_redis import RedisTools
from src.orm_mongodb import MongoDBClient

from aiogram import Bot, types, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command

__all__ = 'start_bot',

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_message(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}')


@dp.message(Command('help'))
async def help_message(message: types.Message):
    text = ('Это бот создан для того, чтобы запоминать различные вещи. \n' +
            'Сверху видеоинструкция, как пользоваться ботом\n' + '   ' +
            '/start - начать пользоваться ботом\n' + '   ' +
            '/help - текущее окно помощи\n' + '\n'
            'Как сделать корректное запоминание.\n' +
            'Вам нужно написать вещь, которую хотите запомнить через тире, и тогда бот, в течение следующих 4 дней ' +
            'будет присылать определение (до тире),' +
            ' а вам нужно будет вспомнить значение (после тире).\n' + 'Например:\n' +
            'Теорема Пифагора - Квадрат гипотенузы равен сумме квадратов катетов' + '\n \n' +
            'Бот будет присылать:' + '\n' +
            'Теорема Пифагора - <tg-spoiler>Квадрат гипотенузы равен сумме квадратов катетов</tg-spoiler>' + '\n' + '\n' +
            'Ваши запоминания остаются в базе данных, если вы хотите что-то вспомнить по истечению 4 дней ' +
            'напишите соответствующую команду' + '\n' +
            '/all_memories' + '\n' +
            '/theme_memories' + '\n' +
            '/delete_memory'
            )
    await message.answer(text=text, parse_mode=ParseMode.HTML)


@dp.message(Command('all_memories'))
async def get_all_memories(message: types.Message):
    all_memories: dict[str: list[str]] = await MongoDBClient.get_all_memories(message.from_user.id)
    text = ''
    for k in all_memories.keys():
        text = text + f'{k}:\n \n'
        text = text + f'  {'\n  '.join(['- ' + s for s in all_memories[k]])}\n \n'
    await message.answer(text=text)


@dp.message(Command('theme_memories'))
async def get_theme_memories(message: types.Message):
    if len(message.text.split()) > 1:
        data = await MongoDBClient.get_data_form_theme(user_id=message.from_user.id, theme=message.text.split()[1])
        text = data[0] + '\n' + '\n' + '\n'.join(data[1:]) + '\n'
        await message.answer(text=text)
    else:
        data = await MongoDBClient.get_data_form_theme(user_id=message.from_user.id)
        text = data[0] + '\n' + '\n' + '\n'.join(data[1:]) + '\n'
        await message.answer(text=text)


@dp.message(Command('delete_memory'))
async def delete_memory(message: types.Message):
    if '#' in message.text:
        theme = message.text.split()[1]
        memory = ' '.join(message.text.split()[2:])
        await MongoDBClient.delete_data(user_id=message.from_user.id,
                                        remembering_to_delete=memory,
                                        theme=theme)
        await RedisTools.delete_item_from_hashtable(user_id=message.from_user.id,
                                                    remembering=theme + ' ' + memory)
    else:
        memory = ' '.join(message.text.split()[1:])
        await MongoDBClient.delete_data(user_id=message.from_user.id,
                                        remembering_to_delete=memory)
        await RedisTools.delete_item_from_hashtable(user_id=message.from_user.id,
                                                    remembering=memory)
    await message.answer(text='Запоминание удалено')


@dp.message()
async def create_memory(message: types.Message):
    if '#' in message.text:
        await message.answer(text='Добавлено в ваши запоминания')
        await MongoDBClient.add_data(user_id=message.from_user.id,
                                     theme=[i for i in message.text.split() if '#' in i][0],
                                     remembering=' '.join([i for i in message.text.split() if '#' not in i]))
        await RedisTools.add_data(user_id=message.from_user.id, value=message.text)
    else:
        await message.answer(text='Добавлено в ваши запоминания')
        await MongoDBClient.add_data(user_id=message.from_user.id,
                                     remembering=message.text)
        await RedisTools.add_data(user_id=message.from_user.id, value=message.text)


async def bot_send_notification(message: str, tg_id: int):
    text = '''Пришло время вспомнить одно из ваши запоминаний \n \n'''
    try:
        text = text + f'{message.split('-')[0]} - <tg-spoiler>{message.split('-')[1]}</tg-spoiler>'
    except IndexError:
        text = text + f'<tg-spoiler>{message}</tg-spoiler>'

    await bot.send_message(chat_id=tg_id,
                           text=text,
                           parse_mode=ParseMode.HTML)



async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
