import json

# Имена входных и выходного файлов
input_files = ["res1.json", "res2.json"]
output_file = "regru.txt"

# Список для хранения значений dname
dnames = []

# Чтение данных из файлов и извлечение значений dname
for file in input_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        services = data.get("answer", {}).get("services", [])
        for service in services:
            dname = service.get("dname")
            if dname:
                dnames.append(dname)

# Запись значений dname в выходной файл
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(dnames))

print(f"Список доменов успешно сохранён в файл {output_file}.")
