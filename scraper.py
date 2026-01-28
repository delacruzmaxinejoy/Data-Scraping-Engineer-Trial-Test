import requests
from bs4 import BeautifulSoup
import json
import time
import logging

BASE_URL = "https://scraping-trial-test.vercel.app"
OUTPUT_FILE = "output.json"

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_page(page_number):
    try:
        response = requests.get(f"{BASE_URL}?page={page_number}", timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Network error on page {page_number}: {e}")
        return None

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []

    cards = soup.select(".business-card")
    for card in cards:
        try:
            record = {
                "business_name": card.select_one(".business-name").get_text(strip=True),
                "registration_id": card.select_one(".entity-number").get_text(strip=True),
                "status": card.select_one(".status").get_text(strip=True),
                "filing_date": card.select_one(".filing-date").get_text(strip=True),
                "agent_name": card.select_one(".agent-name").get_text(strip=True),
                "agent_address": card.select_one(".agent-address").get_text(strip=True),
                "agent_email": card.select_one(".agent-email").get_text(strip=True),
            }
            records.append(record)
        except AttributeError as e:
            logging.warning(f"Missing field in record: {e}")
            continue

    return records

def scrape_all_pages():
    all_data = []
    page = 1

    while True:
        logging.info(f"Scraping page {page}")
        html = get_page(page)
        if not html:
            break

        page_data = parse_page(html)
        if not page_data:
            break

        all_data.extend(page_data)
        page += 1
        time.sleep(1)

    return all_data

def save_output(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    logging.info("Scraping started")
    data = scrape_all_pages()
    save_output(data)
    logging.info(f"Scraping finished. {len(data)} records saved.")
