import json
import os
import subprocess
import socket
import ssl

# Путь к папке src
src_folder = "src"

# Функция для чтения данных из файлов JSON
def load_json(filename):
    print(f"Чтение данных из файла: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Успешно прочитаны данные из файла {filename}")
            return data
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: не удалось декодировать JSON в файле {filename}")
        return None

# Функция для проверки наличия SSL
def check_ssl(domain):
    print(f"Проверка SSL для домена: {domain}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                print(f"SSL-сертификат найден для домена: {domain}")
                return True
    except (ssl.SSLError, socket.error) as e:
        print(f"SSL-сертификат отсутствует для домена {domain} или произошла ошибка: {e}")
        return False

# Функция для построения дерева доменов и поддоменов
def build_domain_tree(domain_data, subdomain_data):
    if not domain_data or not subdomain_data:
        print("Ошибка: данные о доменах или поддоменах отсутствуют.")
        return {}

    domain_tree = {}
    print("Начало построения дерева доменов и поддоменов")

    # Добавляем домены в дерево
    for domain in domain_data["answer"]["result"]:
        ssl_exists = check_ssl(domain["fqdn"])
        domain_tree[domain["id"]] = {
            "fqdn": domain["fqdn"],
            "subdomains": [],
            "ssl": ssl_exists
        }

    # Добавляем поддомены в соответствующие домены
    for subdomain in subdomain_data["answer"]["result"]:
        domain_id = subdomain["domain_id"]
        if domain_id in domain_tree:
            domain_tree[domain_id]["subdomains"].append(subdomain["fqdn"])

    print("Дерево доменов и поддоменов успешно построено")
    return domain_tree

# Функция для записи дерева доменов в файл и создания ssl/nossl файлов
def write_domain_tree_to_file(domain_tree, output_filename, ssl_filename, nossl_filename):
    print(f"Запись дерева доменов в файл: {output_filename}")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f, \
             open(ssl_filename, 'w', encoding='utf-8') as ssl_file, \
             open(nossl_filename, 'w', encoding='utf-8') as nossl_file:

            for domain_id, info in domain_tree.items():
                ssl_status = "SSL: Да" if info['ssl'] else "SSL: Нет"
                f.write(f"Домен: {info['fqdn']} ({ssl_status})\n")
                
                # Записываем в файл поддомены
                if info['subdomains']:
                    f.write("  Поддомены:\n")
                    for subdomain in info['subdomains']:
                        f.write(f"    - {subdomain}\n")
                else:
                    f.write("  Поддоменов нет\n")
                f.write("\n")
                
                # Запись доменов в соответствующие ssl и nossl файлы
                if info['ssl']:
                    ssl_file.write(f"{info['fqdn']}\n")
                else:
                    nossl_file.write(f"{info['fqdn']}\n")

        print("Запись в файл завершена успешно")
        print(f"Доменов с SSL записано в {ssl_filename}")
        print(f"Доменов без SSL записано в {nossl_filename}")

    except Exception as e:
        print(f"Ошибка при записи в файл {output_filename}: {e}")

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
        print(f"Запуск скрипта: {script_path}")
        try:
            subprocess.run(["python3", script_path], check=True)
            print(f"Скрипт {script} выполнен успешно")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении скрипта {script}: {e}")
            return

    # Чтение данных из файлов JSON
    domain_data = load_json('domain.json')
    subdomain_data = load_json('subdomain.json')

    # Построение дерева доменов и поддоменов
    domain_tree = build_domain_tree(domain_data, subdomain_data)

    # Запись дерева доменов в файл и создание ssl/nossl файлов
    write_domain_tree_to_file(domain_tree, 'domain_tree.txt', 'ssl.txt', 'nossl.txt')

    # Удаление файлов JSON
    try:
        os.remove('domain.json')
        os.remove('subdomain.json')
        print("Временные файлы удалены")
    except FileNotFoundError as e:
        print(f"Ошибка при удалении файлов: {e}")

if __name__ == "__main__":
    main()
