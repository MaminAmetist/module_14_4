# План написания админ панели
# Задача "Продуктовая база":

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from crud_functions import get_all_products, connection

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Общая клавиатура
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_main_1 = KeyboardButton(text='Информация')
kb.add(button_main_1)
button_main_2 = KeyboardButton(text='Рассчитать')
kb.add(button_main_2)
button_main_3 = KeyboardButton(text='Купить')
kb.add(button_main_3)

# Инлайн-клавиатура к расчету
kbm = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
kbm.add(button_1)
button_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kbm.add(button_2)

# Инлайн-клавиатура к выбору пола
gender_kb = InlineKeyboardMarkup()
button_m = InlineKeyboardButton(text='Я мэн', callback_data='gender_male')
button_f = InlineKeyboardButton(text='Я девочка вообщет', callback_data='gender_female')
gender_kb.add(button_m, button_f)

# Инлайн-клавиатура к выбору средства
medicine_kb = InlineKeyboardMarkup()
vitamine_list = ['радостин', 'ностальгиксин', 'релаксин', 'пакостин']

for vitamine in vitamine_list:
    button = InlineKeyboardButton(text=f'Витамин {vitamine}', callback_data='product_buying')
    medicine_kb.add(button)

medicine_list = ['catharsis.jpg', 'nostalgia.jpg', 'relax.jpg', 'smile.jpg']


class UserState(StatesGroup):
    gender = State()
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Для подсчета суточной нормы калорий нажмите кнопку "Рассчитать".',
                         reply_markup=kb)


@dp.message_handler(text='Информация')
async def info(message):
    with open('norma.jpg', 'rb') as img:
        await message.answer_photo(img, 'Привет! Я бот, помогающий вашему здоровью.')


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kbm)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    for i in range(len(medicine_list)):
        with open(medicine_list[i], 'rb') as img:
            await message.answer_photo(img, f'Название: Product {products[i][1]}\n'
                                            f'Описание: {products[i][2]}\n'
                                            f'Цена: {products[i][3]}')
    connection.close()
    await message.answer('Выберите продукт:', reply_markup=medicine_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Упрощенный вариант формулы Миффлина-Сан Жеора: \n'
                              'для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n'
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_gender(call):
    await call.message.answer('Выберите ваш пол:', reply_markup=gender_kb)
    await UserState.gender.set()
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('gender_'), state=UserState.gender)
async def process_gender(call: CallbackQuery, state):
    gender = 'М' if call.data == 'gender_male' else 'Ж'
    await state.update_data(gender=gender)
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост в сантиметрах:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес в килограммах:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    try:
        if data['gender'] == 'М' or data['gender'] == 'м':
            norm = 10 * abs(int(data['weight'])) + 6.25 * abs(int(data['growth'])) - 5 * abs(int(data['age'])) + 5
        else:
            norm = 10 * abs(int(data['weight'])) + 6.25 * abs(int(data['growth'])) - 5 * abs(int(data['age'])) - 161
        await message.answer(f'Ваша суточная нома {norm} калорий.')
    except:
        await message.answer('Вы воробушек.')
    finally:
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
