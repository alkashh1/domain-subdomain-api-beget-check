import requests
import json

# Чтение данных из файла login.txt
def get_login_credentials(file_path):
    credentials = {}
    with open(file_path, "r") as file:
        for line in file:
            if "login" in line:
                credentials["login"] = line.split('=')[1].strip().strip("'")
            elif "password" in line:
                credentials["password"] = line.split('=')[1].strip().strip("'")
    return credentials

# Получаем логин и пароль из файла login.txt
login_data = get_login_credentials('src/login.txt')
login = login_data["login"]
password = login_data["password"]

# URL для запроса к API (getDomain)
url_domain = f'https://api.beget.com/api/domain/getList?login={login}&passwd={password}&output_format=json'

# Выполнение GET-запроса
response = requests.get(url_domain)

# Проверка успешности запроса
if response.status_code == 200:
    # Получаем JSON-ответ
    data = response.json()

    # Сохраняем его в файл domain.json
    with open('domain.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Данные успешно сохранены в файл domain.json")
else:
    print(f"Ошибка выполнения запроса: {response.status_code}")

# URL для запроса к API (getZone)
url_zone = f'https://api.beget.com/api/domain/getZoneList?login={login}&passwd={password}&output_format=json'

# Выполнение GET-запроса
response = requests.get(url_zone)

# Проверка успешности запроса
if response.status_code == 200:
    # Получаем JSON-ответ
    data = response.json()

    # Сохраняем его в файл zone.json
    with open('zone.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Данные успешно сохранены в файл zone.json")
else:
    print(f"Ошибка выполнения запроса: {response.status_code}")

