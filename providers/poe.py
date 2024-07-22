# https://www.poe.pl.ua/disconnection/power-outages/
import logging
import os
from dotenv import load_dotenv
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

load_dotenv()


OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'




try:
    data = load_data()
except FileNotFoundError:
    data = {'table': None}

def get_queue_html_info():
    url  = config.PROVIDER_URL
    is_updated = False

    if config.DEBUG == True:
        logging.info("debug mode")
        print("DEBUG")
        with open("test.html", 'r', encoding='utf-8') as file:
        # Read the entire content of the file into a string
            html_content = file.read()

        # Now html_content contains the entire HTML file as a string
        if html != html_content:
            print("UPDATED")
            is_updated = True
        return html_content, is_updated
    
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
        if html != element_html:
            is_updated = True
            print(OKGREEN + "[UPDATED]" + ENDC)
        return element_html, is_updated
    finally:
        # Close the browser
        driver.quit()


def parce_html(html):
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
                i, n = 1, 1
                continue

            if queue_num in result:
                #if i % 2 == 0:
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
                #i = i+1
    data['table'] = result
    return result


def print_queue_info(q_info, queue_number):
    queue = q_info[queue_number]
    for k, v in queue.items():
        if v['text'] == "ON":
            text = OKGREEN + "[" + str(k) + "] " + v['text']  + ENDC
        else:
            text =  FAIL  + "[" + str(k) + "] " + v['text'] + ENDC
        print(text)

def get_queue_info():
    html, is_updated = get_queue_html_info()
    if is_updated:
        q_info = parce_html(html=html)
        save_data(data)
    else:
        q_info = data['table']
    return q_info, is_updated

if __name__ == "__main__":
    html, is_updated = get_queue_html_info()
    q_info = parce_html(html=html)
    print_queue_info(q_info, '5')
