import requests
from utils.constants import ITEMS_PER_PETITION
from utils.exceptions import *
from utils.constants import  MAX_RETRIES
from time import sleep


def check_response_code(response):
    if response.status_code != 200:
        print(f"-------------------- RESPONSE CODE {response.status_code} ------------------------------")
        print(response)
        print(response.json())
        raise IncorrectAPIResponseException()


def get_total_item_key(extraction_name):
    if extraction_name == 'actor':
        item_count_key = "totalItemsCount"
    elif extraction_name == 'benefits':
        item_count_key = "totalItems"
    else:
        raise Exception()
    return item_count_key


def get_total_item_count(url: str, extraction: str):
    tries = 0
    success = False
    while not success:
        try:
            item_count_key = get_total_item_key(extraction)
            response = requests.get(url)
            check_response_code(response)
            success = True
            request_total_items = response.json().get(item_count_key)

            if request_total_items is None:
                raise NoTotalItemsCountAttributeException()

        except IncorrectAPIResponseException:
            tries += 1
            if tries == MAX_RETRIES:
                raise MaxRetriesReachesException()
            sleep(10)
    return request_total_items


def get_pagination_factor(url: str, extraction: str):
    total_items = get_total_item_count(url, extraction)
    num_pages = total_items // ITEMS_PER_PETITION + 1
    return num_pages
