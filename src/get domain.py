import requests
import json

# Данные для аутентификации
login = 'hexen2o1'
password = '1%26rsxnK5uXRr'

# URL для запроса к API
url = f'https://api.beget.com/api/domain/getList?login={login}&passwd={password}&output_format=json'

# Выполнение GET-запроса
response = requests.get(url)

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
