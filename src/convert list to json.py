import json
import re

# Функция для конвертации строки в словарь
def parse_line(line):
    pattern = r'id: (\d+), fqdn: ([^,]+), date_expire: ([^,]+), can_renew: ([^,]+), expire: (-?\d+)'
    match = re.match(pattern, line.strip())
    if match:
        return {
            "id": int(match.group(1)),
            "fqdn": match.group(2),
            "date_expire": match.group(3),
            "can_renew": None if match.group(4) == 'None' else match.group(4),
            "expire": int(match.group(5))
        }
    return None

# Путь к исходному файлу
input_file = "list.json"

# Путь к файлу, куда будем сохранять преобразованный JSON
output_file = "converted_list.json"

# Чтение данных из исходного файла
with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Преобразование каждой строки в объект JSON
json_data = []
for line in lines:
    parsed = parse_line(line)
    if parsed:
        json_data.append(parsed)

# Сохранение данных в формате JSON
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(json_data, file, indent=4)

print(f"Данные успешно преобразованы и сохранены в {output_file}")
