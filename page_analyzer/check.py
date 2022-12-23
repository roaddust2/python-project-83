import requests


def get_status_code(url: str) -> int:
    try:
        response = requests.get(url)
        return response.status_code
    except:
        return
