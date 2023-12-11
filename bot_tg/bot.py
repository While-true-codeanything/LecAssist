from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import TOKEN
from tasks import *
from user import *

LOGIN_URL = "https://functions.yandexcloud.net/d4efscqf4ea38at1ass5"
TASKS_URL = "https://functions.yandexcloud.net/d4emqi4g5hsl1tufets9"


bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
user_token = ''
user_id = ''

class RegistrationState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_second_password = State()
class LoginState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
class VideoState(StatesGroup):
    waiting_for_video = State()
class NameForVideo(StatesGroup):
    waiting_for_videoname = State()

def download_file_from_telegram(file_id):
    telegram_api_url = 'https://api.telegram.org/bot' + TOKEN + f'/getFile?file_id={file_id}'
    response = requests.get(telegram_api_url)
    file_path = response.json()['result']['file_path']
    download_url = 'https://api.telegram.org/file/bot' + TOKEN + f'/{file_path}'

    file_response = requests.get(download_url)
    local_file_path = f'video{os.path.splitext(file_path)[1]}'
    with open(local_file_path, 'wb') as file:
        file.write(file_response.content)

    return local_file_path


main_ikb = InlineKeyboardMarkup()
but_1 = InlineKeyboardButton(text='Открыть профиль', callback_data='open_users_profile')
but_2 = InlineKeyboardButton(text='Отправить новое видео', callback_data='send_video')
but_3 = InlineKeyboardButton(text='Получить историю запросов', callback_data='get_history')
main_ikb.add(but_1).add(but_2).add(but_3)

async def on_startup(_):
    print("Бот запущен")

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    ikb = InlineKeyboardMarkup()
    ib1 = InlineKeyboardButton(text='Зарегистрироваться', callback_data='registration')
    ib2 = InlineKeyboardButton(text='Выполнить вход', callback_data='log_in')
    ikb.add(ib1).add(ib2)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Доброе пожаловать в бот! Вам необходимо выбрать:",
                           parse_mode="HTML",
                           reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data == "registration")
async def registration(call: types.CallbackQuery):
    await call.message.answer(text='Введите логин:')
    await RegistrationState.waiting_for_login.set()
    await call.answer()

@dp.message_handler(state=RegistrationState.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    await message.answer(text='Введите пароль:')
    await state.update_data(login=login)
    await RegistrationState.waiting_for_password.set()

@dp.message_handler(state=RegistrationState.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    pas1 = message.text
    await message.answer(text='Введите пароль повторно:')
    await state.update_data(password=pas1)
    await RegistrationState.waiting_for_second_password.set()

@dp.message_handler(state=RegistrationState.waiting_for_second_password)
async def process_second_password(message: types.Message, state: FSMContext):
    pas2 = message.text
    data = await state.get_data()
    login = data.get('login', '')
    pas1 = data.get('password', '')
    if pas2 == pas1:
        global user_id
        user_id = create_user(login, pas2)
        global user_token
        user_token = auto_check_login(login, pas2)
        await message.answer(
            text='Поздравляю! Вы успешно зарегистрированы. Выберите, что вы хотите сделать дальше: ',
            reply_markup=main_ikb)
        await state.finish()
        await message.answer()
    else:
        await message.answer(text='Введенные пароли не совпадают, введите второй пароль еще раз:')

#--------------------
@dp.callback_query_handler(lambda c: c.data == "log_in")
async def log_in(call: types.CallbackQuery):
    await call.message.answer(text='Введите логин:')
    await LoginState.waiting_for_login.set()
    await call.answer()


@dp.message_handler(state=LoginState.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    await message.answer(text='Введите пароль:')
    await state.update_data(login=login)
    await LoginState.waiting_for_password.set()

@dp.message_handler(state=LoginState.waiting_for_password)
async def process_login_password(message: types.Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    login = data.get('login', '')
    user_token = auto_check_login(login, password)
    await message.answer(
        text='Поздравляю! Вы успешно вошли в аккаунт. Выберите, что вы хотите сделать дальше:',
        reply_markup=main_ikb)
    await state.finish()
    await message.answer()

#-----------------
@dp.callback_query_handler(lambda c: c.data == "open_users_profile")
async def open_users_profile(call: types.CallbackQuery):
    result = get_user_info(user_id["user-id"], user_token['jwt_token'])
    for i in result:
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'{i} : {result[i]}')
    await call.answer()

#-----------------
@dp.callback_query_handler(lambda c: c.data == "send_video")
async def video_name(call: types.CallbackQuery):
    await call.message.answer(text='Введите название для видео:')
    await NameForVideo.waiting_for_videoname.set()
    await call.answer()
#-----------------
@dp.message_handler(state=NameForVideo.waiting_for_videoname)
async def send_video(message: types.Message, state: FSMContext):
    video_name = message.text
    await state.update_data(videoname=video_name)
    await message.answer("Загрузите видео, которое вы хотите отправить.")
    await VideoState.waiting_for_video.set()


@dp.message_handler(content_types=types.ContentType.VIDEO, state=VideoState.waiting_for_video)
async def process_video(message: types.Message, state: FSMContext):
    video = message.video.file_id
    data = await state.get_data()
    video_name = data.get('videoname', '')
    u_file = download_file_from_telegram(video)
    video_name = os.path.splitext(u_file)[0]+os.path.splitext(u_file)[1]
    test_load(u_file, video_name)
    await message.answer('Поздравляю! Вы успешно загрузили видео')
    #await message.answer_video(video.file_id, caption="Ваше видео успешно загружено.")
    create_task(video_name,user_id, user_token)
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)