import requests
from bs4 import BeautifulSoup

def scrape_course(url):

    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("h1")

    description = soup.find("p")

    return {
        "title": title.text if title else "",
        "description": description.text if description else ""
    }