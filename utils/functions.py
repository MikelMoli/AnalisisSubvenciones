import requests
from utils.constants import ITEMS_PER_PETITION


class IncorrectAPIResponseException(Exception):
    """If API response code is not 200 then this error will be risen"""


class NoTotalItemsCountAttributeException(Exception):
    """API response has no 'totalItemsCount' attribute."""


def check_response_code(response):
    if response.status_code != 200:
        print(f"-------------------- RESPONSE CODE {response.status_code} ------------------------------")
        raise IncorrectAPIResponseException()


def get_total_item_key(extraction_name):
    item_count_key = ''
    if extraction_name == 'actor':
        item_count_key = "totalItemsCount"
    elif extraction_name == 'benefits':
        item_count_key = "totalItems"
    else:
        raise Exception()
    return item_count_key


def get_total_item_count(url: str, extraction: str):
    item_count_key = get_total_item_key(extraction)
    response = requests.get(url)
    check_response_code(response)
    request_total_items = response.json().get(item_count_key)
    
    if request_total_items is None:
        raise NoTotalItemsCountAttributeException()
    
    return request_total_items


def get_pagination_factor(url: str, extraction: str):
    total_items = get_total_item_count(url, extraction)
    num_pages = total_items // ITEMS_PER_PETITION + 1
    return num_pages
