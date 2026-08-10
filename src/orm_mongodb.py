from pymongo.asynchronous.mongo_client import AsyncMongoClient
from src.config import settings


__all__ = 'MongoDBClient',


class MongoDBClient:
    __driver = AsyncMongoClient(host=f'{settings.MONGO_HOST}', port=settings.MONGO_PORT)
    __db = __driver['tgusersdatabase']
    __collection = __db['usersdata']

    @classmethod
    async def add_data(cls, user_id: int, remembering: str, theme: str = 'Без темы'):
        orm = cls.__collection
        user: dict[str: str | int] = await orm.find_one({'_id': user_id})
        if user is None:
            if theme is not None:
                await orm.insert_one({'_id': user_id, 'remembering': {theme: [remembering]}})
            else:
                await orm.insert_one({'_id': user_id, 'remembering': {theme: [remembering]}})
        else:
            try:
                if remembering not in user.get('remembering').get(theme):
                    await orm.update_one(
                                    {'_id': user_id},
                                  {'$push': {f'remembering.{theme}': remembering}})
            except TypeError:
                await orm.update_one(
                    {'_id': user_id},
                    {'$push': {f'remembering.{theme}': remembering}})


    @classmethod
    async def get_data_form_theme(cls, user_id: int, theme: str = 'Без темы'):
        orm = cls.__collection
        user_data: dict[str: str | int] = await orm.find_one({'_id': user_id})
        # print(user_data)
        if user_data is not None:
            try:
                if user_data.get('remembering').get(theme) is not None:
                    return [theme, *user_data.get('remembering').get(theme)]
                return ['Данной темы нет', '\n']
            except AttributeError:
                return ['Данной темы нет', '\n']
        else:
            return ['Данной темы нет', '\n']

    @classmethod
    async def delete_data(cls, user_id: int, remembering_to_delete: str, theme: str = 'Без темы'):
        orm = cls.__collection
        await orm.update_one({'_id': user_id}, {'$pull': {f'remembering.{theme}': f'{remembering_to_delete}'}})


    @classmethod
    async def get_all_memories(cls, user_id: int) -> dict[str: list[str]]:
        orm = cls.__collection
        user = await orm.find_one({'_id': user_id})
        if user is not None:
            return user.get('remembering')
        else:
            return {'У вас нет запоминаний': ''}
