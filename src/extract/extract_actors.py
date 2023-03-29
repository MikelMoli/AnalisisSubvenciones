import os
import sys
import requests
from utils.constants import ITEMS_PER_PETITION, DB_CONNECTION_URL, MAX_RETRIES, SLEEP_TIME
import utils.functions as auxiliar_functions
from models.directory_models import Actor, Municipality, Sector, ContactPhone, ContactEmail, ContactWebsite, RelatedActors, CreateDatabase

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from requests.exceptions import ConnectionError

from time import sleep
from tqdm import tqdm
import multiprocessing as mp

sys.path.append(os.getcwd())


class ExtractActors:

    def __init__(self):
        self._BASE_URL = "https://api.euskadi.eus/directory?lang=SPANISH&fromItemAt={}&pageSize={}"
        self._pagination_factor = auxiliar_functions.get_pagination_factor(self._BASE_URL.format(0, 10), "actor")

    @staticmethod
    def _parse_contact_methods(data, actor_id):
        phone_list = []
        email_list = []
        website_list = []
        if "contactInfo" in data.keys():
            data = data.get("contactInfo")
            if "phones" in data.keys():
                phone_list = [ContactPhone(phone_number=phone.get("number"), id=None, actor_id=actor_id, type=phone.get("type"), usage=phone.get("usage")) for phone in data.get("phones")]
            if "emails" in data.keys():
                email_list = [ContactEmail(email=email.get("email"), id=None, actor_id=actor_id, usage=email.get("usage")) for email in data.get("emails")]
            if "websites" in data.keys():
                website_list = [ContactWebsite(website=website.get("url"), id=None, actor_id=actor_id, usage=website.get("usage")) for website in data.get("websites")]

        return phone_list, email_list, website_list

    @staticmethod
    def _parse_municipality(data, actor_id):
        if "geoPosition" in data.keys():
            data = data.get("geoPosition")
            portal = None
            state = None
            country = None
            county = None
            municipality = None
            locality = None
            street = None      
            
            if "portal" in data.keys():
                portal = data.get("portal").get("name")
            if "state" in data.keys():
                state = data.get("state").get("oid")
            if "country" in data.keys():
                country = data.get("country").get("oid")
            if "county" in data.keys():
                county = data.get("county").get("oid")
            if "municipality" in data.keys():
                municipality = data.get("municipality").get("oid")
            if "locality" in data.keys():
                locality = data.get("locality").get("oid")
            if "street" in data.keys():
                street = data.get("street").get("name")

            return Municipality(
                id=None,
                actor_id=actor_id,
                actor=None,
                country=country,
                state=state,
                county=county,
                municipality=municipality,
                locality=locality,
                street=street,
                portal=portal,
                zipcode=data.get("zipCode"),
                floor=data.get("floor")
            )
        else:
            return None

    @staticmethod
    def _parse_sectors(data, actor_id):
        sectors = []
        if "sectors" in data.keys():
            data = data.get("sectors")
            return [Sector(id=None, actor_id=actor_id, name=sector.get("name")) for sector in data]
        return sectors

    @staticmethod
    def _parse_linked_agents(data, actor_oid):
        links = []
        if "peopleLinks" in data.keys():
            links += data.get("peopleLinks")
        if "entitiesLinks" in data.keys():
            links += data.get("entitiesLinks")
        if "equipmentsLinks" in data.keys():
            links += data.get("equipmentsLinks")

        related_actors = []
        for link in links:
            if "href" in link.keys():
                actor_id_2 = link.get("href").split("/")[-1]
                related_actors.append(
                    RelatedActors(id=None, actor_one_id=actor_oid, actor_two_id=actor_id_2)
                )
        return related_actors

    @staticmethod
    def _parse_actor_response(data):
        actor_oid = data.get("oid")
        try:
            municipality = ExtractActors._parse_municipality(data, actor_oid)
            sectors = ExtractActors._parse_sectors(data.get("_links"), actor_oid)
            phone_list, email_list, website_list = ExtractActors._parse_contact_methods(data, actor_oid)
            related_actors = ExtractActors._parse_linked_agents(data.get("_links"), actor_oid)

            actor = Actor(
                oid=actor_oid,
                id=data.get("id"), 
                name=data.get("name"),
                type=data.get("type"),
                subtype=data.get("subType"),
                creation_date=data.get("createDate"),
                last_update=data.get("lastUpdate"),
                sector_list=sectors,
                municipality=municipality,
                contact_phone_list=phone_list, 
                contact_email_list=email_list, 
                contact_website_list=website_list
            )
            
            return actor, related_actors
        except Exception as e:
            print(e, flush=True)
            raise Exception()

    @staticmethod
    def _make_petition(url):
        success = False
        tries = 1
        while not success:
            try:
                response = requests.get(url)
                auxiliar_functions.check_response_code(response)
                success = True
            except ConnectionError:
                if tries == MAX_RETRIES:
                    print(url, flush=True)
                print(f"Retying {url}...", flush=True)
                sleep(SLEEP_TIME)
                tries += 1

        return response.json()

    @staticmethod
    def _process_page_data(items):
        engine = create_engine(DB_CONNECTION_URL, echo=False)
        with Session(engine) as session:
            for item in tqdm(items):
                item_url = item.get("_links").get("self").get("href")
                response_data = ExtractActors._make_petition(item_url)
                actor, related_actors = ExtractActors._parse_actor_response(response_data)
                session.add(actor)
                session.add_all(related_actors)
            
            session.commit()
            # session.flush()

    @staticmethod
    def _handle_directory_call(url):
        success = False
        tries = 1
        while not success:
            try:
                response = requests.get(url)
                auxiliar_functions.check_response_code(response)
                success = True
            except ConnectionError:
                if tries == MAX_RETRIES:
                    print(url, flush=True)
                    raise Exception()
                else:
                    print(f"Retying {url}...", flush=True)
                    sleep(SLEEP_TIME)
                    tries += 1
        return response

    def run(self):
        parallelize = False
        if parallelize:
            with mp.Pool(processes=4) as pool:
                for page_number in tqdm(range(0, self._pagination_factor)):
                    item_index = page_number * ITEMS_PER_PETITION
                    directory_url = self._BASE_URL.format(item_index, ITEMS_PER_PETITION)
                    response = ExtractActors._handle_directory_call(directory_url)
                    items = response.json()['pageItems']
                    _ = pool.apply_async(ExtractActors._process_page_data, (items,))
        else:
            for page_number in range(0, self._pagination_factor):
                print(f"------------------------ {page_number} / {self._pagination_factor} ------------------------")
                item_index = page_number * ITEMS_PER_PETITION
                directory_url = self._BASE_URL.format(item_index, ITEMS_PER_PETITION)
                response = requests.get(directory_url)
                auxiliar_functions.check_response_code(response)
                items = response.json()['pageItems']
                self._process_page_data(items)


if __name__ == '__main__':
    cd = CreateDatabase()
    cd.run()

    extract_entities_task = ExtractActors()
    extract_entities_task.run()
