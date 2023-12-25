import requests
import re
from config import TOKEN
import os

LOGIN_URL = "https://functions.yandexcloud.net/d4efscqf4ea38at1ass5"
TASKS_URL = "https://functions.yandexcloud.net/d4emqi4g5hsl1tufets9"


def parse_response(response):
    try:
        data = response.json()
        return f"Error: {data['error']}"
        return str(data)
    except:
        return "error: Unknown error"


def create_user(login, password, url=LOGIN_URL):
    payload = {
        "action": 'create',
        "login": login,
        "password": password
    }
    response = requests.get(url, params=payload)
    return response.json()


def tg_login(tg_id, url=LOGIN_URL):
    payload = {
        "action": "login-telegram",
        "tg-id": tg_id,
    }
    response = requests.post(url, params=payload)
    return response.json()


def user_login(login, mail, telegram, password, url=LOGIN_URL):
    payload = {
        "action": "login",
        "login": login,
        "mail": mail,
        "telegram": telegram,
        "password": password
    }
    response = requests.post(url, params=payload)
    return response.json()


def get_user_info(userid, token, url=LOGIN_URL):
    payload = {
        "action": "get-user-info",
        "user-id": userid,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def auto_check_login(input_string, password):
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    if email_pattern.match(input_string):
        return user_login("", input_string, "", password, url=LOGIN_URL)
    elif input_string.isdigit():
        return user_login("", "", input_string, password, url=LOGIN_URL)
    else:
        return user_login(input_string, "", "", password, url=LOGIN_URL)


def get_user_id(login, token, url=LOGIN_URL):
    payload = {
        "action": "get-user-id",
        "login": login,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def update_field(field, userid, value, token, url=LOGIN_URL):
    payload = {
        "action": "update",
        "field": field,
        "user-id": userid,
        "value": value,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


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
