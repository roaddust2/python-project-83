import requests
from bs4 import BeautifulSoup


def get_status_code(url: str) -> int:
    try:
        response = requests.get(url)
        return response.status_code

    except:
        return


def get_data(url: str) -> dict:
    page_text = {
    'h1': '',
    'title': '',
    'content': ''
    }

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    page_text['h1'] = soup.h1.get_text()
    page_text['title'] = soup.title.get_text()
    page_text['content'] = soup.find("meta", attrs={'name':'description'})["content"]
    return page_text
