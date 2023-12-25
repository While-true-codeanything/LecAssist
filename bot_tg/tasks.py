import requests
import boto3
from botocore.client import Config

LOGIN_URL = "https://functions.yandexcloud.net/d4efscqf4ea38at1ass5"
TASKS_URL = "https://functions.yandexcloud.net/d4emqi4g5hsl1tufets9"


def parse_response(response):
    try:
        data = response.json()
        return f"Error: {data['error']}"
        return str(data)
    except:
        return "error: Unknown error"


def create_task(vid_name, user_id, token, url=TASKS_URL):
    payload = {
        "action": "create-task",
        "vid_name": vid_name,
        "user-id": user_id,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def get_task_status(task_id, token, url=TASKS_URL):
    payload = {
        "action": "get-task-status",
        "task-id": task_id,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def update_task_status(task_id, field, value, token, url=TASKS_URL):
    payload = {
        "action": "update-task-status",
        "task-id": task_id,
        "field": field,
        "value": value,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def get_user_tasks(user_id, token, url=TASKS_URL):
    payload = {
        "action": "get-user-tasks",
        "user-id": user_id,
        "token": token
    }
    response = requests.post(url, params=payload)
    return response.json()


def test_load(vid_path, vid_name):
    client = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id="YCAJEthRSYAHgpVGpJ9F3nZZd",
        aws_secret_access_key="YCPGmVBR13PRJwl102QP70ywdTnlstSj9Li-Jn6J",
        config=Config(signature_version='s3v4')
    )
    bucket_name = 'testback.ked'
    try:
        with open(vid_path, 'rb') as data:
            client.upload_fileobj(data, bucket_name, vid_name)
        print("Файл успешно загружен.")
    except client.exceptions.NoSuchBucket:
        print("Указанный бакет не существует.")
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
