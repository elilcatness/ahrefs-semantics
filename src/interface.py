import os
import time

from src.constants import DEFAULT_INTERVAL, AUTH_TIMEOUT
from src.exceptions import MissingDotenvData, InvalidFileData
from src.utils import get_driver, auth


def get_interval(text: str = '', default: tuple = DEFAULT_INTERVAL):
    while True:
        interval = input(
            f'Введите интервал{" " + text + " "}через пробел '
            '(для значения по умолчанию '
            f'{(" ".join(map(str, default)) if isinstance(default, (tuple, list)) else default)} '
            f'нажмите Enter): ')
        if not interval:
            return default
        try:
            interval = tuple(map(int, interval.split()))
            assert len(interval) == 2
            if interval[0] > interval[1]:
                print('\nНачало интервала должно быть меньше или равно концу\n')
            elif interval[0] < 0 or interval[1] < 0:
                raise ValueError
            else:
                return interval
        except ValueError:
            print('\nКонцы интервала должны быть неотрицательными целыми числами\n')
        except AssertionError:
            print('Концов интервала должно быть 2', end='\n\n')


def proceed():
    credentials_filename = os.getenv('credentials_filename', 'credentials.txt')
    third_party_source = False
    driver = get_driver()
    with open(credentials_filename, encoding='utf-8') as f:
        lines = [x.strip() for x in f.readlines()]
        if len(lines) > 1:
            third_party_source = True
            login_url, base_url = lines
        else:
            base_url = os.getenv('base_url')
            if not base_url:
                raise MissingDotenvData('В переменных среды отсутствует base_url')
        base_url = base_url.rstrip('/')
        try:
            login, password = lines[0].split(':')
        except ValueError:
            raise InvalidFileData(f'Неверный формат данных в {credentials_filename}')
    if not third_party_source:
        auth(driver, login, password)
        time.sleep(AUTH_TIMEOUT)
        if driver.current_url == os.getenv('login_url'):
            auth(driver, login, password)
    else:
        driver.get(login_url)
        print('Ожидание авторизации пользователем...')
        while driver.current_url == login_url:
            pass
    if 'verification-required' in driver.current_url.lower():
        verification_url = input('Введите ссылку с почты: ')
        driver.get(verification_url)
        time.sleep(AUTH_TIMEOUT)
    return driver, base_url


__all__ = ['get_interval', 'proceed']
