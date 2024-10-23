import json
import os
import subprocess

# Функция для чтения данных из файлов JSON
def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# Функция для построения дерева доменов и поддоменов
def build_domain_tree(domain_data, subdomain_data):
    domain_tree = {}

    # Добавляем домены в дерево
    for domain in domain_data["answer"]["result"]:
        domain_tree[domain["id"]] = {
            "fqdn": domain["fqdn"],
            "subdomains": []
        }

    # Добавляем поддомены в соответствующие домены
    for subdomain in subdomain_data["answer"]["result"]:
        domain_id = subdomain["domain_id"]
        if domain_id in domain_tree:
            domain_tree[domain_id]["subdomains"].append(subdomain["fqdn"])

    return domain_tree

# Функция для записи дерева доменов в файл
def write_domain_tree_to_file(domain_tree, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as f:
        for domain_id, info in domain_tree.items():
            f.write(f"Домен: {info['fqdn']}\n")
            if info['subdomains']:
                f.write("  Поддомены:\n")
                for subdomain in info['subdomains']:
                    f.write(f"    - {subdomain}\n")
            else:
                f.write("  Поддоменов нет\n")
            f.write("\n")

# Основная функция
def main():
    # Список скриптов для последовательного запуска
    scripts = [
        "domain.py",
        "subdomain.py",
    ]   

    # Запускаем каждый скрипт по порядку
    for script in scripts:
        script_path = os.path.join(src_folder, script)
        print(f"Запускаем {script_path}...")
        subprocess.run(["python", script_path], check=True)

    # Чтение данных из файлов JSON
    domain_data = load_json('domain.json')
    subdomain_data = load_json('subdomain.json')

    # Построение дерева доменов и поддоменов
    domain_tree = build_domain_tree(domain_data, subdomain_data)

    # Запись дерева доменов в файл
    write_domain_tree_to_file(domain_tree, 'domain_tree.txt')

    # Удаление файлов JSON
    os.remove('domain.json')
    os.remove('subdomain.json')

if __name__ == "__main__":
    main()
