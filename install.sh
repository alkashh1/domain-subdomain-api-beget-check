#!/bin/bash

# Описание скрипта
echo "Скрипт создания дерева доменов"

# Проверка прав суперпользователя
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен от имени суперпользователя (root)" 
   exit 1
fi

# Обновление списка пакетов
echo "Обновление списка пакетов..."
apt-get update

# Установка необходимых пакетов
echo "Установка пакетов..."
apt-get install -y python

# Настройка системы
echo "Настройка системы..."
pip install requests

# Копирование в рабочую папку
SRC_DIR=$(pwd)
DEST_DIR="/home/zabbix/scripts/DomainTree"
mkdir -p "$DEST_DIR"
cp -r "$SRC_DIR"/* "$DEST_DIR"/
echo "Все файлы успешно скопированы в $DEST_DIR"

# Крон
cron_job="30 2 * * * /usr/bin/python3 /home/zabbix/scripts/DomainTree/main.py" # Создание задачи
crontab -l | grep -F "$cron_job" > /dev/null # Проверка создания

# Проверка
if [ $? -eq 1 ]; then
  # Добавляем задачу в crontab
  (crontab -l; echo "$cron_job") | crontab -
  echo "Cron-задача успешно добавлена!"
else
  echo "Эта задача уже существует в crontab."
fi

# Первое выполнение скрипта
echo "Выполнение скрипта."
python3 main.py

# Очистка кеша пакетов
echo "Очистка кеша пакетов..."
apt-get clean

echo "Установка завершена, скрипт выполнен."
