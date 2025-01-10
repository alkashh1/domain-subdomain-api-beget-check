import requests
import json
import time
from datetime import datetime

# Параметры API
BASE_URL = "https://api.reg.ru/api/regru2/service/get_list"
CREDENTIALS_FILE = "src/loginregru.txt"

# Функция для чтения логинов и паролей из файла
def read_credentials(file_path):
    credentials = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if ":" in line:
                    username, password = line.split(":", 1)
                    credentials.append((username.strip(), password.strip()))
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    return credentials

# Функция для проверки корректности ответа
def is_valid_response(data):
    try:
        return "answer" in data and "services" in data["answer"]
    except (TypeError, KeyError):
        return False

def get_domains(username, password, result_index):
    # Формирование данных для отправки в теле запроса
    payload = {
        "input_data": '{"servtype":"domain"}',
        "input_format": "json",
        "output_content_type": "plain",
        "username": username,
        "password": password
    }

    data = None
    while not is_valid_response(data):
        try:
            response = requests.post(BASE_URL, data=payload)
            response.raise_for_status()
            data = response.json()
            if not is_valid_response(data):
                time.sleep(1)  # Задержка в 1 секунду
        except requests.RequestException:
            time.sleep(1)  # Задержка в случае ошибки

    # Сохранение результатов запроса в JSON-файл
    result_file = f"res{result_index}.json"
    with open(result_file, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Результаты сохранены в {result_file}")

# Основной код
if __name__ == "__main__":
    start_time = datetime.now()  # Начало выполнения скрипта
    credentials = read_credentials(CREDENTIALS_FILE)
    
    if not credentials:
        print("Нет учетных данных для работы.")
    else:
        for index, (username, password) in enumerate(credentials, start=1):
            print(f"Обрабатывается аккаунт: {username}")
            get_domains(username, password, index)
    
    end_time = datetime.now()  # Конец выполнения скрипта
    elapsed_time = end_time - start_time
    print(f"Время выполнения скрипта: {elapsed_time}")
