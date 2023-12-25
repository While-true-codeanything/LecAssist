from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


main_ikb = InlineKeyboardMarkup()
but_1 = InlineKeyboardButton(text='Открыть профиль', callback_data='open_users_profile')
but_2 = InlineKeyboardButton(text='Отправить новое видео', callback_data='send_video')
but_3 = InlineKeyboardButton(text='Получить историю запросов', callback_data='get_history')
main_ikb.add(but_1).add(but_2).add(but_3)

ikb = InlineKeyboardMarkup()
ib1 = InlineKeyboardButton(text='Зарегистрироваться', callback_data='registration')
ib2 = InlineKeyboardButton(text='Выполнить вход', callback_data='log_in')
ib3 = InlineKeyboardButton(text='Выполнить вход c помощью телеграм ID', callback_data='log_in_tg')
ikb.add(ib1).add(ib2).add(ib3)

profile_ikb = InlineKeyboardMarkup()
pib1 = InlineKeyboardButton(text='Изменить почту', callback_data='change_mail')
pib2 = InlineKeyboardButton(text='Изменить пароль', callback_data='change_password')
pib3 = InlineKeyboardButton(text='Привязать телеграм ID', callback_data='connect_tg')
pib4 = InlineKeyboardButton(text='Основное меню', callback_data='main_menu')
profile_ikb.add(pib1).add(pib2).add(pib3).add(pib4)
