import os
import time
from csv import DictReader, DictWriter
from random import randint

from dotenv import load_dotenv
from selenium.common import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

from src.exceptions import MissingDotenvData, AuthorizationFailedException


def get_driver():
    options = ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--log-level=3')
    driver = Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;'
                  'delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;'
                  'delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;'
                  'delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;'
                  'delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;'
    })
    return driver


def auth(driver: Chrome, login: str, password: str):
    login_url = os.getenv('login_url')
    if not login_url:
        raise MissingDotenvData('В переменных среды отсутствует login_url')
    driver.get(login_url)
    for input_name, verbose_name, value in [('email', 'логина', login), ('password', 'пароля', password)]:
        try:
            field = driver.find_element(By.XPATH, f'//input[@name="{input_name}"]')
        except NoSuchElementException:
            raise AuthorizationFailedException(f'Не удалось найти поле для ввода {verbose_name}')
        for s in value:
            field.send_keys(s)
            time.sleep(float(f'0.1{randint(0, 9)}'))
    try:
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    except (NoSuchElementException, ElementClickInterceptedException,
            ElementNotInteractableException) as e:
        raise AuthorizationFailedException(
            f'Не удалось нажать на кнопку авторизации [{e.__class__.__name__}]')


# noinspection PyTypeChecker
def unite(folder: str, output_filename: str = 'output.csv'):
    d = dict()
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), encoding='utf-8') as f:
            for row in DictReader(f, f.readline().strip().split(','), delimiter=',', quotechar='"'):
                if (keyword := row['Keyword']) not in d:
                    d[keyword] = {'Count': 1, 'SERP features': row['SERP features'],
                                  'Volume': row['Volume'] if row['Volume'] else 1,
                                  'KD': (row['KD']
                                         if row['KD'] is not None and row['KD'] != ''
                                         else 100),
                                  'URL': [row['Current URL inside']] if row['Current URL inside'] else []}
                else:
                    d[keyword]['Count'] += 1
                    if row['Current URL inside']:
                        d[keyword]['URL'].append(row['Current URL inside'])
    fieldnames = ['Keyword', 'Count', 'SERP features', 'Volume', 'KD', 'URL']
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, fieldnames, delimiter=',', quotechar='"')
        writer.writeheader()
        for keyword in d:
            url_list = d[keyword].pop('URL')
            if len(url_list) > 2:
                print(url_list)
            url = '|'.join(url_list)
            writer.writerow({'Keyword': keyword, **d[keyword], 'URL': url})


def missing_handler(driver: Chrome, text: str):
    if input(f'{text}. Продолжить? (y\\n): ').lower() != 'y':
        driver.close()
        driver.quit()
        exit()
    return


if __name__ == '__main__':
    load_dotenv()
    unite(os.path.join('..', os.getenv('folder')))
