# https://www.poe.pl.ua/disconnection/power-outages/
import logging
from datetime import datetime, time, timedelta
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from energybot.helpers.data import load_data, save_data
from energybot import config
# Specify the path to the chromedriver executable
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')


service = Service(ChromeDriverManager().install())  # Path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)


OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'


try:
    data = load_data()
except FileNotFoundError:
    data = {'table': None}

def get_queue_html_info():
    url  = config.PROVIDER_URL
    if config.DEBUG == True:
        logging.info("debug mode")
        print("DEBUG")
        with open("test.html", 'r', encoding='utf-8') as file:
        # Read the entire content of the file into a string
            html_content = file.read()
        return html_content
    
    print( OKGREEN + "[PROD]" + ENDC)
    try:
        # Open a web page
        driver.get(url)

        # Wait for a specific element to be loaded (use appropriate condition and locator)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gpvinfo'))
        )
        # Interact with the element (example: clicking a button)
        element_html = element.get_attribute('outerHTML')
        return element_html
    finally:
        # Close the browser
        driver.quit()

def parce_html(html):
    is_updated = False
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody')
    if not table:
        raise ValueError("Table not found.")
    headers = table.find_all('tr')
    result = {}
    time_dict = {}
    current_date = datetime.now().date()
    queue_num = None
    for h in headers:
        for q in h:
            output = q.get_text(strip=True)
            if 'черга' in output:
                queue_num = output[0]
                time_dict = {}
                result[queue_num] = time_dict
                specific_datetime = datetime.combine(current_date, time(0, 0, 0))
                specific_datetime_next = specific_datetime + timedelta(minutes=30)
                n = 1
                continue

            if queue_num in result:
                td_class = q.get('class')
                if td_class  == ['light_on']:
                    current_value = "ON"
                    value = True
                else:
                    current_value = "OFF"
                    value = False
                time_dict[specific_datetime] = {
                    'text': current_value,
                    'id':n,
                    'value':value
                }
                specific_datetime = specific_datetime_next
                specific_datetime_next = specific_datetime + timedelta(minutes=30)
                n = n +1
    if data['table'] != result:
        is_updated = True
        data['table'] = result
        save_data(data)
    return result, is_updated

def print_queue_info(q_info, queue_number):
    queue = q_info[queue_number]
    for k, v in queue.items():
        if v['text'] == "ON":
            text = OKGREEN + "[" + str(k) + "] " + v['text']  + ENDC
        else:
            text =  FAIL  + "[" + str(k) + "] " + v['text'] + ENDC
        print(text)

def get_queue_info():
    html = get_queue_html_info()
    q_info, is_updated = parce_html(html=html)
    return q_info, is_updated

if __name__ == "__main__":
    html = get_queue_html_info()
    q_info, is_updated = parce_html(html=html)
    print_queue_info(q_info, '5')
