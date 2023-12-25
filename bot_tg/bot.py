from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor

from config import TOKEN
from tasks import *
from user import *
from buttons import *
from States import *

LOGIN_URL = "https://functions.yandexcloud.net/d4efscqf4ea38at1ass5"
TASKS_URL = "https://functions.yandexcloud.net/d4emqi4g5hsl1tufets9"

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
user_token = {}
user_id = {}


async def on_startup(_):
    print("Бот запущен")


@dp.message_handler(commands=['restart'])
async def process_restart_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Перезапуск бота...")
    await bot.send_message(chat_id=message.from_user.id, text="Бот перезапущен! Чтобы начать, напишите /start")
    await on_startup(None)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Добро пожаловать! Я бот сервиса LecAssist. Умею создавать субтитры к лекциям! Но для начала Вам необходимо выбрать:",
                           parse_mode="HTML",
                           reply_markup=ikb)


@dp.message_handler(state=StartState.start)
async def start(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Вам необходимо выбрать:",
                           reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data == "registration")
async def registration(call: types.CallbackQuery):
    await call.message.answer(text='Введите логин:')
    await RegistrationState.waiting_for_login.set()
    await call.answer()


@dp.message_handler(state=RegistrationState.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    if login == '/restart':
        await process_restart_command(message)
    else:
        await message.answer(text='Введите пароль:')
        await state.update_data(login=login)
        await RegistrationState.waiting_for_password.set()


@dp.message_handler(state=RegistrationState.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    pas1 = message.text
    if pas1 == '/restart':
        await process_restart_command(message)
    else:
        await message.answer(text='Введите пароль повторно:')
        await state.update_data(password=pas1)
        await RegistrationState.waiting_for_second_password.set()


@dp.message_handler(state=RegistrationState.waiting_for_second_password)
async def process_second_password(message: types.Message, state: FSMContext):
    pas2 = message.text
    if pas2 == '/restart':
        await process_restart_command(message)
    else:
        data = await state.get_data()
        login = data.get('login', '')
        pas1 = data.get('password', '')
        if pas2 == pas1:
            global user_id
            user_id[message.from_user.id] = create_user(login, pas2)
            global user_token
            if 'error' in user_id[message.from_user.id]:
                if user_id[message.from_user.id]['error'] == 'already existing acc':
                    await message.answer(
                        text='Кажется, такой пользователь уже существует. Введите новые данные. Введите логин:')
                    await RegistrationState.waiting_for_login.set()
                else:
                    await message.answer(text=f'Ошибка входа: {user_id[message.from_user.id]["error"]}')
            else:
                user_token[message.from_user.id] = auto_check_login(login, pas2)
                await message.answer(
                    text='Поздравляю! Вы успешно зарегистрированы. Выберите, что вы хотите сделать дальше: ',
                    reply_markup=main_ikb)
                await state.finish()
        else:
            await message.answer(text='Введенные пароли не совпадают, введите второй пароль еще раз:')


@dp.callback_query_handler(lambda c: c.data == "log_in_tg")
async def log_in_tg(call: types.CallbackQuery):
    global user_id
    global user_token
    user_token[call.from_user.id] = tg_login(call.from_user.id)
    if not 'jwt_token' in user_token[call.from_user.id]:
        await bot.send_message(chat_id=call.from_user.id, text='Ошибка входа. Попробуйте еще раз', reply_markup=ikb)
    else:
        user_id[call.from_user.id] = get_user_id(call.from_user.id, user_token[call.from_user.id]['jwt_token'])
        await bot.send_message(
            chat_id=call.from_user.id,
            text='Поздравляю! Вы успешно вошли в аккаунт. Выберите, что вы хотите сделать дальше:',
            reply_markup=main_ikb)
        await call.answer()


@dp.callback_query_handler(lambda c: c.data == "log_in")
async def log_in(call: types.CallbackQuery):
    await call.message.answer(text='Введите логин:')
    await LoginState.waiting_for_login.set()
    await call.answer()


@dp.message_handler(state=LoginState.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    if login == '/restart':
        await process_restart_command(message)
    else:
        await message.answer(text='Введите пароль:')
        await state.update_data(login=login)
        await LoginState.waiting_for_password.set()


@dp.message_handler(state=LoginState.waiting_for_password)
async def process_login_password(message: types.Message, state: FSMContext):
    global user_id
    global user_token
    password = message.text
    if password == '/restart':
        await process_restart_command(message)
    else:
        data = await state.get_data()
        login = data.get('login', '')
        user_token[message.from_user.id] = auto_check_login(login, password)
        if not 'jwt_token' in user_token[message.from_user.id]:
            await message.answer(text='Ошибка входа. Попробуйте еще раз')
            await message.answer(text='Введите логин:')
            await LoginState.waiting_for_login.set()
        else:
            user_id[message.from_user.id] = get_user_id(login, user_token[message.from_user.id]['jwt_token'])
            await message.answer(
                text='Поздравляю! Вы успешно вошли в аккаунт. Выберите, что вы хотите сделать дальше:',
                reply_markup=main_ikb)
            await state.finish()
            await message.answer()


@dp.callback_query_handler(lambda c: c.data == "change_mail")
async def change_mail(call: types.CallbackQuery):
    await call.message.answer(text='Введите новое значение')
    await ProfileState.waiting_for_new_mail.set()
    await call.answer()


@dp.message_handler(state=ProfileState.waiting_for_new_mail)
async def process_mail(message: types.Message, state: FSMContext):
    mail = message.text
    if mail == '/restart':
        await process_restart_command(message)
    else:
        await state.update_data(mail=mail)
        global user_id
        global user_token
        a = update_field('mail', user_id[message.from_user.id]['user-id'], mail,
                         user_token[message.from_user.id]['jwt_token'])
        await bot.send_message(chat_id=message.from_user.id, text='Поле успешно изменено', reply_markup=profile_ikb)
        await state.finish()
        await message.answer()


@dp.callback_query_handler(lambda c: c.data == "change_password")
async def change_password(call: types.CallbackQuery):
    await call.message.answer(text='Введите новое значение')
    await ProfileState.waiting_for_new_password.set()
    await call.answer()


@dp.message_handler(state=ProfileState.waiting_for_new_password)
async def process_password(message: types.Message, state: FSMContext):
    pas = message.text
    if pas == '/restart':
        await process_restart_command(message)
    else:
        await state.update_data(pas=pas)
        global user_id
        global user_token
        a = update_field('password', user_id[message.from_user.id]['user-id'], pas,
                         user_token[message.from_user.id]['jwt_token'])
        await bot.send_message(chat_id=message.from_user.id, text='Поле успешно изменено', reply_markup=profile_ikb)
        await state.finish()
        await message.answer()


@dp.callback_query_handler(lambda c: c.data == "connect_tg")
async def connect_tg(call: types.CallbackQuery):
    a = update_field('telegram', user_id[call.from_user.id]['user-id'], [call.from_user.id],
                     user_token[call.from_user.id]['jwt_token'])
    await bot.send_message(chat_id=call.from_user.id,
                           text='Телеграм ID успешно прикрплен. Выберите, что хотите сделать дальше',
                           reply_markup=main_ikb)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def main_menu(call: types.CallbackQuery):
    await bot.send_message(chat_id=call.from_user.id,
                           text='Выберите, что хотите сделать дальше',
                           reply_markup=main_ikb)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "open_users_profile")
async def open_users_profile(call: types.CallbackQuery):
    result = get_user_info(user_id[call.from_user.id]["user-id"], user_token[call.from_user.id]['jwt_token'])
    for i in ['login', 'mail', 'telegram']:
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'{i} : {result[i] if i in result else None}')

    await bot.send_message(chat_id=call.from_user.id,
                           text='Действие успешно выполнено! Выберите, что хотите сделать дальше',
                           reply_markup=profile_ikb)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "send_video")
async def video_name(call: types.CallbackQuery):
    await call.message.answer(text='Введите название для видео:')
    await NameForVideo.waiting_for_videoname.set()
    await call.answer()


@dp.message_handler(state=NameForVideo.waiting_for_videoname)
async def send_video(message: types.Message, state: FSMContext):
    video_name = message.text
    if video_name == '/restart':
        await process_restart_command(message)
    else:
        await state.update_data(videoname=video_name)
        await message.answer("Загрузите видео, которое вы хотите отправить.")
        await VideoState.waiting_for_video.set()


@dp.message_handler(content_types=types.ContentType.VIDEO, state=VideoState.waiting_for_video)
async def process_video(message: types.Message, state: FSMContext):
    video = message.video.file_id
    data = await state.get_data()
    video_name = data.get('videoname', '')
    u_file = download_file_from_telegram(video)
    video_name = os.path.splitext(u_file)[0] + os.path.splitext(u_file)[1]
    test_load(u_file, video_name)
    await message.answer('Поздравляю! Вы успешно загрузили видео')
    a = create_task(video_name, user_id[message.from_user.id]['user-id'], user_token[message.from_user.id]['jwt_token'])
    if 'task-id' in a:
        await message.answer(f'id задания=: {a["task-id"]}')
        await message.answer(
            'Через несколько минут видео должно быть готово. Информацию о задании Вы можете получить с помощью истории запросов',
            reply_markup=main_ikb)
    await state.finish()
    await message.answer()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=VideoState.waiting_for_video)
async def process_video(message: types.Message, state: FSMContext):
    video = message.document.file_id
    data = await state.get_data()
    video_name = data.get('videoname', '')
    u_file = download_file_from_telegram(video)
    video_name = os.path.splitext(u_file)[0] + os.path.splitext(u_file)[1]
    test_load(u_file, video_name)
    await message.answer('Поздравляю! Вы успешно загрузили видео')
    a = create_task(video_name, user_id[message.from_user.id]['user-id'], user_token[message.from_user.id]['jwt_token'])
    if 'task-id' in a:
        await message.answer(f'id задания=: {a["task-id"]}')
        await message.answer(
            'Через несколько минут видео должно быть готово. Информацию о задании Вы можете получить с помощью истории запросов',
            reply_markup=main_ikb)
    await state.finish()
    await message.answer()


@dp.callback_query_handler(lambda c: c.data == "get_history")
async def get_user_history(call: types.CallbackQuery):
    result = get_user_tasks(user_id[call.from_user.id]["user-id"], user_token[call.from_user.id]['jwt_token'])
    for i in result['tasks']:
        c = i['consp-link']
        status = i['status']
        t_id = i['task-id']
        vid = i['vid-link']
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'Ссылка для конспекта: {c}\nСтатус задания: {status}\nID задания: {t_id}\nСсылка на видео с субтитрами: {vid}')
    await bot.send_message(chat_id=call.from_user.id,
                           text=' Выберите, что вы хотите сделать дальше:', reply_markup=main_ikb)
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
