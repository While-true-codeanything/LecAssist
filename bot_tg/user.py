import requests
import re

LOGIN_URL = "https://functions.yandexcloud.net/d4efscqf4ea38at1ass5"
TASKS_URL = "https://functions.yandexcloud.net/d4emqi4g5hsl1tufets9"
def parse_response(response):
    try:
        data = response.json()
        return f"Error: {data['error']}"
        return str(data)
    except:
        return "error: Unknown error"


def create_user(login, password, url = LOGIN_URL):
    payload = {
        "action": 'create',
        "login": login,
        "password": password
        }
    response = requests.get(url, params=payload)
    return response.json()

def user_login(login, mail, telegram, password, url = LOGIN_URL):
    payload = {
        "action": "login",
        "login": login,
        "mail": mail,
        "telegram": telegram,
        "password": password
    }
    response = requests.post(url, params=payload)
    return response.json()

def get_user_info(userid, token, url = LOGIN_URL):
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
        return user_login("", input_string, "", password, url = LOGIN_URL)
    elif input_string.isdigit():
        return user_login("", "", input_string, password, url = LOGIN_URL)
    else:
        return user_login(input_string, "", "", password, url = LOGIN_URL)