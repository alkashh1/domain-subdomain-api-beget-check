import json

# Путь к файлам
converted_list_path = "converted_list.json"
zone_file_path = "zone.json"
domain_file_path = "domain.json"
output_file_path = "end.txt"

# Чтение данных из файлов
with open(converted_list_path, "r", encoding="utf-8") as file:
    domains = json.load(file)

with open(zone_file_path, "r", encoding="utf-8") as file:
    zone_data = json.load(file)["answer"]["result"]

with open(domain_file_path, "r", encoding="utf-8") as file:
    domain_info = json.load(file)["answer"]["result"]

# Функция для получения зоны домена
def get_zone_from_fqdn(fqdn):
    return fqdn.split('.')[-1]

# Функция для поиска регистратора по fqdn
def get_registrar(fqdn):
    for domain in domain_info:
        if domain["fqdn"] == fqdn:
            return domain.get("registrar", "не найден")
    return "не найден"

# Открываем файл для записи результатов
with open(output_file_path, "w", encoding="utf-8") as output_file:
    # Проходим по всем доменам
    for domain in domains:
        fqdn = domain["fqdn"]
        expire = domain["expire"]

        # Получение зоны домена
        zone = get_zone_from_fqdn(fqdn)

        # Получение стоимости продления
        price_renew = None
        if zone in zone_data:
            price_renew = zone_data[zone].get("price_renew")
        
        # Получение регистратора
        registrar = get_registrar(fqdn)
        
        # Формирование строки для вывода
        if price_renew is not None:
            output_line = f"{fqdn} - дней до блокировки {expire}, стоимость продления {price_renew} руб., регистратор: {registrar}\n"
        else:
            output_line = f"{fqdn} - дней до блокировки {expire}, стоимость продления не найдена, регистратор: {registrar}\n"
        
        # Запись строки в файл
        output_file.write(output_line)

print(f"Информация о доменах сохранена в файл {output_file_path}")
