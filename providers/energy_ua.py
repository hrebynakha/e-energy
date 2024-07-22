import os
from dotenv import load_dotenv
import re
import requests
from bs4 import BeautifulSoup

load_dotenv()

ENERGY_BASE_URL = os.getenv('ENERGY_BASE_URL')
DEBUG = False

def get_queue_html_info(queue_number):
    url  = ENERGY_BASE_URL + str(queue_number)
    if DEBUG:
        with open("test.html", 'r', encoding='utf-8') as file:
        # Read the entire content of the file into a string
            html_content = file.read()

        # Now html_content contains the entire HTML file as a string
        return html_content
    
    response = requests.get(url)
    if response.status_code != 200:
        print(response)
        raise Exception("Cannot get energy info.")
    
    return response.text    


def parce_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    info = {
        "date": None,
        "date_confirmed": False,
        "state_now": False,
        "state_confirmed": False,
    }

    script_tags = soup.find_all('script', type='text/javascript')

    # Iterate through each link and print its text and href attribute
    for script in script_tags:
        if "$('.countdown_2').downCount" in script.text:
            match = re.search(r"date: '([^']*)'", script.text)
            if match:
                date_value = match.group(1)
                info["date"] = date_value
                info["date_confirmed"] = True
            else:
                print("Date value not found in script.")

    countdown_div = soup.find('div', class_='countdown_info')
    if countdown_div:
        print("Found Countdown <div>")
        first_span = countdown_div.find('span')
        if first_span:
            
            enery_text = first_span.text.strip()
            if "має бути присутня" in enery_text:
                info["state_now"] = True
            info["state_confirmed"] = True
        else:
            print("No <span> found inside Countdown <div>.")

    return info


def get_queue_info(queue_number):
    html = get_queue_html_info(queue_number)
    info = parce_html(html)
    return queue_number, info

if __name__ == "__main__":
    html = get_queue_html_info("5")
    print(parce_html(html))