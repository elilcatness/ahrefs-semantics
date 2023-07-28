import os
import random
import shutil
import time

from dotenv import load_dotenv

from src.exceptions import FileIsEmptyException, MissingDotenvData
from src.interface import *
from src.parse import export


def main():
    if input('Запуск в офлайн-режиме (y\\n): ').lower() != 'y':
        folder = os.getenv('folder', 'export')
        if os.path.exists(folder):
            if input(f'Папка {folder} будет удалена. Продолжить? (y\\n): ').lower() != 'y':
                return
            shutil.rmtree(folder)
        domains_filename = os.getenv('domains_filename', 'domains.txt')
        with open(domains_filename, encoding='utf-8') as f:
            domains = [line.strip() for line in f]
        if not domains:
            raise FileIsEmptyException(f'Файл {domains_filename} пуст')
        url_suffix = os.getenv('url_suffix')
        if not url_suffix:
            raise MissingDotenvData('Суффикс URL отсутствует в .env')
        country_code = ''
        while not country_code:
            country_code = input('Введите код страны: ').lower()
        interval = get_interval('между запросами')
        driver, base_url = proceed()
        for i in range(len(domains)):
            print(f'{i}. {domains[i]}')
            export(driver, base_url + url_suffix.format(country_code, domains[i]))
            # time.sleep(random())
    pass


if __name__ == '__main__':
    load_dotenv()
    main()
