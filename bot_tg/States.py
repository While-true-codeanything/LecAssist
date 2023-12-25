from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_second_password = State()
    prev_handler = State()


class LoginState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_data = State()


class VideoState(StatesGroup):
    waiting_for_video = State()


class NameForVideo(StatesGroup):
    waiting_for_videoname = State()


class StartState(StatesGroup):
    start = State()


class ProfileState(StatesGroup):
    waiting_for_new_mail = State()
    waiting_for_new_password = State()
    clean_profile = State()
