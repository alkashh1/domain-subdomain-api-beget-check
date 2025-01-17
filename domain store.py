import json
import re
import os
import subprocess

# Путь к файлам
domain_file = "domain.json"
zone_file = "zone.json"
output_file = "store.txt"

# Путь к папке src
src_folder = "src"

# Список скриптов 
scripts = [
    "all get.py",
]

# Запускаем скрипт
for script in scripts:
    script_path = os.path.join(src_folder, script)
    print(f"Запускаем {script_path}...")
    subprocess.run(["python", script_path], check=True)

# Функция для фильтрации доменов с зоной .store без поддоменов
def filter_store_domains(domains):
    store_domains = []
    for domain in domains:
        fqdn = domain.get("fqdn", "")
        # Проверяем, что домен имеет зону .store и является основным (нет поддомена)
        if re.match(r"^[a-zA-Z0-9-]+\.(store)$", fqdn):
            store_domains.append(fqdn)
    return store_domains

# Чтение данных из файла domain.json
with open(domain_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Извлечение списка доменов
domains = data.get("answer", {}).get("result", [])

# Фильтруем домены с зоной .store
filtered_domains = filter_store_domains(domains)

# Записываем отфильтрованные домены в файл store.txt
with open(output_file, "w", encoding="utf-8") as file:
    for domain in filtered_domains:
        file.write(domain + "\n")

print(f"Отфильтрованные домены сохранены в {output_file}")

# Удаляем файлы domain.json и zone.json
if os.path.exists(domain_file):
    os.remove(domain_file)
    print(f"Файл {domain_file} успешно удален.")
if os.path.exists(zone_file):
    os.remove(zone_file)
    print(f"Файл {zone_file} успешно удален.")
