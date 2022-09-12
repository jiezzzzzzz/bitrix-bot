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

    await message.answer("Введите ИНН")
    await UserState.inn.set()


@dp.message_handler(state=UserState.inn)
async def inn_register(message: types.Message, state: FSMContext):
    await state.update_data(inn=message.text)
    await message.answer("Введите реквизиты")
    await UserState.next()


@dp.message_handler(state=UserState.number)
async def number_register(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text)
    data = await state.get_data()
    await message.answer(f"ИНН: {data['inn']}\n"
                         f"Реквизиты: {data['number']}")

    await state.finish()


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
    'UF_CRM_1662804274348': a,
    'UF_CRM_1662804286991': number

        }
    }
    for d in deals
]

bitrix.call('crm.deal.update', tasks)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)