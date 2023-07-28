import time

from selenium.common import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.wait import WebDriverWait

from src.selectors import *
from src.constants import EXPORT_BTN_TIMEOUT, RADIO_BTNS_TIMEOUT
from src.utils import missing_handler


def export(driver: Chrome, url: str):
    print(f'{url=}')
    driver.get(url)
    try:
        export_btn = WebDriverWait(driver, EXPORT_BTN_TIMEOUT).until(
            exp_cond.presence_of_element_located((By.XPATH, EXPORT_BTN_XPATH)))
    except TimeoutException:
        return missing_handler(driver, f'Не удалось найти кнопку экспорта на {url}')
    export_btn.click()
    try:
        rows_btns = WebDriverWait(driver, RADIO_BTNS_TIMEOUT).until(
            exp_cond.presence_of_all_elements_located((By.XPATH, ROWS_BTNS_XPATH)))
        assert rows_btns
    except (TimeoutException, AssertionError):
        return missing_handler(
            driver, f'Не удалось найти кнопки выбора кол-ва строк на {url}')
    if (len(rows_btns) <= 2 and rows_btns[0].find_element(
            By.XPATH, './..').text.strip().split()[-1] == '0'):
        return print(f'{url} пуст. Пропускаем...')
    if not (btn := rows_btns[1]).is_selected():
        btn.find_element(By.XPATH, './../div').click()
    try:
        encoding_btns = WebDriverWait(driver, RADIO_BTNS_TIMEOUT).until(
            exp_cond.presence_of_all_elements_located((By.XPATH, ENCODING_BTNS_XPATH)))
        assert len(encoding_btns) >= 2
    except (TimeoutException, AssertionError):
        return missing_handler(
            driver, f'Не удалось найти кнопки выбора кодировки на {url}')
    if not (btn := encoding_btns[1]).is_selected():
        btn.find_element(By.XPATH, './../div').click()
    time.sleep(0.5)
    try:
        export_inner_btn = WebDriverWait(driver, EXPORT_BTN_TIMEOUT).until(
            exp_cond.presence_of_element_located((By.XPATH, EXPORT_INNER_BTN_XPATH)))
    except TimeoutException:
        return missing_handler(
            driver, f'Не удалось найти кнопку экспорта внутри модального окна на {url}')
    export_inner_btn.click()
