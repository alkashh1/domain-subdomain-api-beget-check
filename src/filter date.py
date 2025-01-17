import json
from datetime import datetime, timedelta

# Путь к файлу с данными
domain_file_path = "domain.json"
ids_file_path = "id.json"
list_file_path = "list.json"

# Загружаем данные из файла
with open(domain_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Текущая дата
current_date = datetime.now()

# Список для хранения id доменов, которые нужно продлить
ids_to_renew = []

# Проверяем, что данные корректны
if data.get("status") == "success" and "result" in data["answer"]:
    domains = data["answer"]["result"]
    
    with open(list_file_path, "w", encoding="utf-8") as list_file:    
    # Проходим по всем доменам и анализируем параметр date_expire
        for domain in domains:
            id = domain.get("id")
            fqdn = domain.get("fqdn")
            date_expire_str = domain.get("date_expire")
            can_renew = domain.get("can_renew")
            domain_id = domain.get("id")

            # Проверяем, есть ли дата истечения
            if date_expire_str:
                # Преобразуем строку даты в объект datetime
                date_expire = datetime.strptime(date_expire_str, "%Y-%m-%d")

                # Проверяем, сколько дней осталось до истечения
                days_until_expire = (date_expire - current_date).days

                # Если осталось менее 30 дней
                if days_until_expire < 60:
                    # Выводим данные в терминал
                    # print(f"fqdn: {fqdn}, date_expire: {date_expire_str}, can_renew: {can_renew}")
                    print(f"До истечения домена {fqdn} осталось {days_until_expire} дней.")

                    # Выводим данные в фаил list.json
                    # with open(list_file_path, "a", encoding="utf-8") as list_file:
                    line = f"id: {id}, fqdn: {fqdn}, date_expire: {date_expire_str}, can_renew: {can_renew}, expire: {days_until_expire}\n"
                        
                        # Записываем строку в файл
                    list_file.write(line)
                    print(f"Записали домен {fqdn} в файл.")

                    # Добавляем id домена в список для продления
                ids_to_renew.append(domain_id)

    # Сохраняем id доменов в отдельный файл
    if ids_to_renew:
        with open(ids_file_path, "w") as id_file:
            json.dump(ids_to_renew, id_file, indent=4)
        print("ID доменов сохранены в файл id.json")
    else:
        print("Нет доменов, требующих продления.")
else:
    print("Некорректная структура данных.")


