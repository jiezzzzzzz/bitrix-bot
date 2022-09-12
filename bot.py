from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fast_bitrix24 import Bitrix
import os
import sqlite3


storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)
webhook = 'https://b24-2n1ca2.bitrix24.ru/rest/1/1048j59oitcrt3k2/'  # вебхук хранится в переменных окружения
bitrix = Bitrix(webhook)


class UserState(StatesGroup):
    inn = State()
    number = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await UserState.inn.set()
    await message.answer("Введите ИНН")


@dp.message_handler(state=UserState.inn)
async def inn_register(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['inn'] = message.text
        await UserState.next()
        await message.answer("Введите реквизиты")


@dp.message_handler(state=UserState.number)
async def number_register(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
        await message.answer(f"ИНН: {data['inn']}\n"
                             f"Реквизиты: {data['number']}")
        await send_bitrix(dict(data))
        await state.finish()


def send_bitrix(info: dict):
    fields = {'fields':
            {
                "TITLE": "Тестовая сделка",
                "TYPE_ID": "GOODS",
                "STAGE_ID": "NEW",
                "COMPANY_ID": 3,
                "CONTACT_ID": 3,
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "PROBABILITY": 30,
                "CURRENCY_ID": "USD",
                "OPPORTUNITY": 5000,
                "CATEGORY_ID": 5,
            }}

    bitrix.call('crm.deal.add', fields)

    deals = bitrix.get_all(
            'crm.deal.list',
            params={
                'select': ['*', 'UF_*'],
                'filter': {'CLOSED': 'N'}
        })

    tasks = [
            {
        'ID': d['ID'],
        'fields': {
            'UF_CRM_1662804274348': info['inn'],
            'UF_CRM_1662804286991': info['number']
                }
        }
        for d in deals
    ]
    bitrix.call('crm.deal.update', tasks)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
