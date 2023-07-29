import os
from random import randint
import shutil
import time

from dotenv import load_dotenv

from src.exceptions import FileIsEmptyException, MissingDotenvData
from src.interface import *
from src.parse import export
from src.utils import unite


def main():
    folder = os.getenv('folder', 'export')
    if input('Запуск в офлайн-режиме (y\\n): ').lower() != 'y':
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
        os.mkdir(folder)
        driver, base_url = proceed(folder)
        count = len(domains)
        for i in range(len(domains)):
            print(f'{i + 1}/{count}. {domains[i]}')
            export(driver, base_url + url_suffix.format(country_code, domains[i]))
            if interval != (0, 0) and i < len(domains) - 1:
                time_arg = float(f'{randint(*interval)}.{randint(0, 9)}')
                print(f'Отдыхаем {time_arg} секунд перед запросом следующим доменом')
                time.sleep(time_arg)
    unite(folder, os.getenv('output_filename', 'output.csv'))


if __name__ == '__main__':
    load_dotenv()
    main()
