# https://www.poe.pl.ua/disconnection/power-outages/

# pylint: disable=import-error

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from energybot.helpers.logger import logger

# from energybot.helpers.data import load_data,
from energybot import config


# Specify the path to the chromedriver executable
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")


service = Service(ChromeDriverManager().install())  # Path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)


OKGREEN = "\033[92m"
FAIL = "\033[91m"
ENDC = "\033[0m"


def get_queue_html_info():
    """Get queue html info"""
    url = config.PROVIDER_URL
    if config.DEBUG:
        logger.info("Debug mode enabled, loading test.html")
        with open("test.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return html_content
    try:
        # Open a web page
        logger.info("Opening web page: %s", url)
        driver.get(url)

        # Wait for a specific element to be loaded (use appropriate condition and locator)
        logger.info("Waiting for element to be loaded")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gpvinfo"))
        )
        # Interact with the element (example: clicking a button)
        logger.info("Getting element html")
        element_html = element.get_attribute("outerHTML")
        return element_html
    finally:
        # Close the browser
        driver.quit()


def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if not table:
        raise ValueError("No <table> element found in HTML")

    rows = table.find_all("tr")
    data = []
    lights_map = {
        "light_1": "ON",
        "light_2": "OFF",
        "light_3": "WAIT",
        "unknown": "NO_INFO",
    }

    current_queue = None
    for row in rows[1:]:
        queue_td = row.select_one(".turnoff-scheduleui-table-queue")
        subqueue_td = row.select_one(".turnoff-scheduleui-table-subqueue")

        light_cells = row.select("td[class^=light_]")
        if not light_cells:
            continue

        if queue_td:
            current_queue = queue_td.get_text(strip=True)

        subqueue = subqueue_td.get_text(strip=True) if subqueue_td else None
        logger.info(
            "Processing queue: %s, subqueue: %s, light: %s",
            current_queue,
            subqueue,
            len(light_cells),
        )
        slots = []
        minute_iterator = 0
        for _, td in enumerate(light_cells):
            value = td.get("class", ["unknown"])[0]

            slots.append(
                {
                    "start_time_min": minute_iterator,
                    "end_time_min": minute_iterator + 30,
                    "state": lights_map[value],
                }
            )
            minute_iterator += 30

        data.append(
            {
                "queue_number": current_queue,
                "subqueue_number": subqueue,
                "queue_name": f"{current_queue}/{subqueue}",
                "slots": slots,
            }
        )
    return data


def print_queue_info(q_info, queue_number):
    """Print queue info"""
    queue = q_info[queue_number]
    for k, v in queue.items():
        if v["text"] == "ON":
            text = OKGREEN + "[" + str(k) + "] " + v["text"] + ENDC
        else:
            text = FAIL + "[" + str(k) + "] " + v["text"] + ENDC
        print(text)


def get_queue_info():
    """Get queue info"""
    html_info = get_queue_html_info()
    q_info = parse_html(html=html_info)
    return q_info


if __name__ == "__main__":
    html_ = get_queue_html_info()
    q_info_ = parse_html(html=html_)
    print_queue_info(q_info_, "5")
