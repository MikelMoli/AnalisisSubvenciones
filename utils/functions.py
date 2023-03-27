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

def get_total_item_count(url: str):
    response = requests.get(url)
    check_response_code(response)
    request_total_items = response.json().get("totalItemsCount")
    
    if request_total_items is None:
        raise NoTotalItemsCountAttributeException()
    
    return request_total_items

def get_pagination_factor(url: str):
    total_items = get_total_item_count(url)
    num_pages = total_items // ITEMS_PER_PETITION + 1
    return num_pages
