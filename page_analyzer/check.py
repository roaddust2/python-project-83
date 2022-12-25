import requests
from bs4 import BeautifulSoup


def get_status_code(url: str) -> int:
    try:
        response = requests.get(url)
        return response.status_code
    except Exception:
        return


def get_data(url: str) -> dict:
    page_text = {
        'h1': '',
        'title': '',
        'content': ''
    }

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.get_text()
    title = soup.title.get_text()
    content = soup.find(
        "meta", attrs={'name': 'description'}
        )

    page_text.update(
        {'h1': h1}
        ) if h1 is not None else page_text.setdefault('h1', '')
    page_text.update(
        {'title': title}
        ) if title is not None else page_text.setdefault('title', '')
    page_text.update(
        {'content': content["content"]}
        ) if content is not None else page_text.setdefault('content', '')
    return page_text
