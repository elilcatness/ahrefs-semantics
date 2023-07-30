import time

from selenium.common import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.wait import WebDriverWait

from src.selectors import *
from src.constants import (EXPORT_BTN_TIMEOUT, RADIO_BTNS_TIMEOUT,
                           EXPORT_BTN_CLICK_TIMEOUT, EXPORT_INNER_BTN_CLICK_TIMEOUT, COUNTRY_REDIRECT_TIMEOUT)
from src.utils import handle_exception


def export(driver: Chrome, url: str, country_code: str, domain: str):
    url = url.format(country_code, domain)
    driver.get(url)
    try:
        export_btn = WebDriverWait(driver, EXPORT_BTN_TIMEOUT).until(
            exp_cond.presence_of_element_located((By.XPATH, EXPORT_BTN_XPATH)))
    except TimeoutException as e:
        raise handle_exception(
            driver, e.__class__, f'Не удалось найти кнопку экспорта на {url}')
    time.sleep(COUNTRY_REDIRECT_TIMEOUT)
    if f'country={country_code}' not in driver.current_url:
        return print('Произошла переадресация на другую страну.\n'
                     f'{url} пуст. Пропускаем...')
    export_btn.click()
    time.sleep(EXPORT_BTN_CLICK_TIMEOUT)
    try:
        rows_btns = WebDriverWait(driver, RADIO_BTNS_TIMEOUT).until(
            exp_cond.presence_of_all_elements_located((By.XPATH, ROWS_BTNS_XPATH)))
        assert rows_btns
    except (TimeoutException, AssertionError) as e:
        raise handle_exception(
            driver, e.__class__, f'Не удалось найти кнопки выбора кол-ва строк на {url}')
    # костыль
    if len(rows_btns) == 0:
        raise handle_exception(
            driver, Exception, f'Не удалось найти кнопки выбора кол-ва строк на {url}')
    if ((rows_btns_count := len(rows_btns)) <= 2 and rows_btns[0].find_element(
            By.XPATH, './..').text.strip().split()[-1] == '0'):
        return print(f'{url} пуст. Пропускаем...')
    if rows_btns_count > 2 and not (btn := rows_btns[1]).is_selected():
        btn.find_element(By.XPATH, './../div').click()
    try:
        encoding_btns = WebDriverWait(driver, RADIO_BTNS_TIMEOUT).until(
            exp_cond.presence_of_all_elements_located((By.XPATH, ENCODING_BTNS_XPATH)))
        assert len(encoding_btns) >= 2
    except (TimeoutException, AssertionError) as e:
        raise handle_exception(
            driver, e.__class__, f'Не удалось найти кнопки выбора кодировки на {url}')
    if not (btn := encoding_btns[1]).is_selected():
        btn.find_element(By.XPATH, './../div').click()
    time.sleep(0.5)
    try:
        export_inner_btn = WebDriverWait(driver, EXPORT_BTN_TIMEOUT).until(
            exp_cond.presence_of_element_located((By.XPATH, EXPORT_INNER_BTN_XPATH)))
    except TimeoutException as e:
        raise handle_exception(
            driver, e.__class__,
            f'Не удалось найти кнопку экспорта внутри модального окна на {url}')
    export_inner_btn.click()
    return time.sleep(EXPORT_INNER_BTN_CLICK_TIMEOUT)
