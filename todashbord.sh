#!/bin/bash

# Скрипт для отправки содержимого файла в Zabbix
ZABBIX_SERVER="127.0.0.1:10050"  # IP Zabbix сервера
HOSTNAME="vpn-server6"  # Имя хоста в Zabbix
ITEM_KEY="domain.subdomain.fromfile"  # Уникальный ключ элемента данных
FILE_PATH="/home/zabbix/scripts/DomainTree/domain_tree.txt"  # Путь к файлу

# Чтение файла
FILE_CONTENT=$(cat "$FILE_PATH")

# Отправка содержимого файла в Zabbix
zabbix_sender -z "$ZABBIX_SERVER" -s "$HOSTNAME" -k "$ITEM_KEY" -o "$FILE_CONTENT"
