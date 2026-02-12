import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

SEARCH_CONFIG = {
    "🎓 STUDENT ROLE": os.environ["URL_STUDENT"],
    "🟢 ENTRY LEVEL": os.environ["URL_ENTRY"],
    "🔵 EXPERIENCED": os.environ["URL_EXPERIENCED"],
}

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "60"))

HEADERS = {"User-Agent": "Mozilla/5.0"}

seen = {label: set() for label in SEARCH_CONFIG}

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=20)

def extract_job_links(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/job/" in href:
            links.add(urljoin(base_url, href))
    return links

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def initialize():
    for label, url in SEARCH_CONFIG.items():
        try:
            html = fetch(url)
            seen[label].update(extract_job_links(html, url))
        except Exception as e:
            print("Init error", label, e)

def check_once():
    for label, url in SEARCH_CONFIG.items():
        try:
            html = fetch(url)
            jobs = extract_job_links(html, url)
            for job in jobs:
                if job not in seen[label]:
                    seen[label].add(job)
                    send_telegram(f"{label}\nNew Microsoft posting:\n{job}")
        except Exception as e:
            print("Check error", label, e)

if __name__ == "__main__":
    initialize()
    send_telegram("✅ Microsoft monitor started.")
    while True:
        check_once()
        time.sleep(POLL_SECONDS)
