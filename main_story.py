import subprocess
import shutil
import os

# Путь к папке src
src_folder = "src"

# Загружаем домены из blacklist.txt
blacklist_file = os.path.join(src_folder, "blacklist.txt")
blacklist = set()

# Список скриптов для последовательного запуска
scripts = [
    "all get.py",
    "filter date.py",
    "convert list to json.py",
    "list price renew.py"
]

# Запускаем каждый скрипт по порядку
for script in scripts:
    script_path = os.path.join(src_folder, script)
    print(f"Запускаем {script_path}...")
    subprocess.run(["python3", script_path], check=True)


if os.path.exists(blacklist_file):
    with open(blacklist_file, "r") as file:
        blacklist = set(line.strip() for line in file if line.strip())
    print("Черный список загружен:", blacklist)
else:
    print(f"Файл {blacklist_file} не найден.")
    exit()

# Чтение end.txt из корневой папки
end_file_dest = os.path.join(os.getcwd(), "end.txt")

if not os.path.exists(end_file_dest):
    print("Файл end.txt не найден в корневой папке.")
    exit()

# Фильтрация доменов в end.txt
filtered_lines = []
print("Содержимое end.txt до фильтрации:")

with open(end_file_dest, "r") as end_file:
    for line in end_file:
        print(line.strip())  # Диагностический вывод строки из end.txt
        domain = line.split()[0]  # Получаем первую часть строки как доменное имя
        if domain in blacklist:
            print(f"Исключаем домен: {domain} (в черном списке)")
        else:
            print(f"Добавляем домен: {domain} (не в черном списке)")
            filtered_lines.append(line)

# Записываем отфильтрованный результат в end.txt
with open(end_file_dest, "w") as end_file:
    end_file.writelines(filtered_lines)

print("\nФайл end.txt обновлен с отфильтрованными доменами.")

# Список JSON-файлов для удаления
json_files = [
    "converted_list.json",
    "domain.json",
    "zone.json",
    "id.json",
    "list.json"
]

# Удаление JSON-файлов
for json_file in json_files:
    json_file_path = os.path.join(os.getcwd(), json_file)
    if os.path.exists(json_file_path):
        print(f"Удаляем {json_file_path}...")
        os.remove(json_file_path)
    else:
        print(f"Файл {json_file_path} не найден.")

print("Все JSON-файлы успешно удалены.")
