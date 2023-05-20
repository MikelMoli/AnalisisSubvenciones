BASE_URL_DICT = {
    "entity": "https://api.euskadi.eus/directory/entities?lang=SPANISH&fromItemAt={}&pageSize={}",
    "entity-general": "https://api.euskadi.eus/directory/entities?lang=SPANISH&fromItemAt={}&pageSize={}",
    "entity-specific": "https://api.euskadi.eus/directory/entities/{}"
}

DEBUG = False

if DEBUG:
    ITEMS_PER_PETITION = 10
else:
    ITEMS_PER_PETITION = 100


MAX_RETRIES = 5
SLEEP_TIME = 5

DB_CONNECTION_URL = "postgresql+psycopg2://postgres:postgres@192.168.1.21/subvenciones_euskadi"