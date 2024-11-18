import os
import time

def ensure_trailing_newline(file_path):
    """
    Проверяет наличие пустой строки в конце файла и добавляет её, если отсутствует.

    :param file_path: Путь к файлу.
    """
    try:
        with open(file_path, "r+", encoding="utf-8") as file:
            content = file.read()
            if not content.endswith("\n"):
                file.write("\n")  # Добавляем пустую строку в конце файла
    except Exception as e:
        print(f"Ошибка при проверке файла {file_path}: {e}")

def remove_empty_lines(file_path):
    """
    Удаляет пустые строки из файла.

    :param file_path: Путь к файлу.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        # Убираем пустые строки
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Перезаписываем файл только с непустыми строками
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(non_empty_lines)
    except Exception as e:
        print(f"Ошибка при удалении пустых строк в файле {file_path}: {e}")

def compare_files(file1_path, file2_path, output_path):
    """
    Сравнивает два файла построчно и записывает уникальные строки в новый файл.

    :param file1_path: Путь к первому файлу.
    :param file2_path: Путь ко второму файлу.
    :param output_path: Путь к файлу, куда будут записаны уникальные строки.
    """
    try:
        # Проверяем существование файлов
        if not os.path.exists(file1_path):
            print(f"Ошибка: Файл {file1_path} не существует.")
            return
        if not os.path.exists(file2_path):
            print(f"Ошибка: Файл {file2_path} не существует.")
            return

        # Проверяем и добавляем пустую строку в конце каждого файла
        ensure_trailing_newline(file1_path)
        ensure_trailing_newline(file2_path)

        # Чтение строк из файлов
        with open(file1_path, "r", encoding="utf-8") as file1, open(file2_path, "r", encoding="utf-8") as file2:
            file1_lines = set(file1.readlines())  # Уникальные строки из первого файла
            file2_lines = set(file2.readlines())  # Уникальные строки из второго файла

        # Вычисляем симметрическую разность строк (уникальные строки)
        unique_lines = file1_lines.symmetric_difference(file2_lines)

        # Записываем уникальные строки в новый файл
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(unique_lines)

        # Удаляем пустые строки из выходного файла
        remove_empty_lines(output_path)

        print(f"Уникальные строки успешно записаны в файл: {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Измерение времени выполнения
start_time = time.time()

# Параметры файлов
file1_path = "manual.txt"  # Путь к первому файлу
file2_path = "auto.txt"  # Путь ко второму файлу
output_path = "/etc/zabbix/scripts/ssl_https.txt"  # Путь к файлу с уникальными строками

# Вызов функции сравнения файлов
compare_files(file1_path, file2_path, output_path)

# Завершение измерения времени
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Время выполнения скрипта: {elapsed_time:.2f} секунд.")
