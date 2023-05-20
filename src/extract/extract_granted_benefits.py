import json
import os
import sys
sys.path.append(os.getcwd())

from sqlalchemy.exc import IntegrityError
from utils.constants import ITEMS_PER_PETITION, DB_CONNECTION_URL, MAX_RETRIES, SLEEP_TIME
import utils.functions as auxiliar_functions
from models.granted_benefits_models import GrantedBenefit, OrganizationGroup, Organization, Area, Service, Convener

from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from requests.exceptions import ConnectionError
from sqlalchemy.dialects.postgresql import insert

from time import sleep
from tqdm import tqdm
import multiprocessing as mp

import requests

ERROR_FILE_PATH = os.path.join(os.getcwd(), "src", "extract", "errors", "errors.json")


class ExtractGrantedBenefits:

    def __init__(self):
        self._BASE_URL = "https://api.euskadi.eus/granted-benefit/v1.0/granted-benefits?_elements={}&_page={}"
        self._pagination_factor = auxiliar_functions.get_pagination_factor(self._BASE_URL.format(20, 1), "benefits")
        self._error_file_path = os.path.join(os.getcwd(), "src", "extract", "errors", "errors.json")

    @staticmethod
    def _handle_request_call(url):
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
                    print(f"Retrying for {tries} time...", flush=True)
                    sleep(SLEEP_TIME)
                    tries += 1
        
        return response.json().get("granted-benefits")

    @staticmethod
    def _parse_convener_components(data):
        org_group = None
        organization = None
        area = None
        service = None
        response_keys = data.keys()
        if "organizationGroup" in response_keys:
            org_group_data = data.get("organizationGroup")
            org_group = OrganizationGroup(
                organization_group_id=org_group_data.get("id"),
                organization_group_name=org_group_data.get("nameByLang").get("SPANISH")
            )

        if "organization" in response_keys:
            org_data = data.get("organization")
            organization = Organization(
                organization_id=org_data.get("id"),
                organization_name=org_data.get("nameByLang").get("SPANISH")
            )

        if "area" in response_keys:
            area_data = data.get("area")
            area = Area(
                area_id=area_data.get("id"),
                area_name=area_data.get("nameByLang").get("SPANISH")
            )

        if "service" in response_keys:
            service_data = data.get("service")
            service = Service(
                service_id=service_data.get("id"),
                service_name=service_data.get("nameByLang").get("SPANISH")
            )

        return org_group, organization, area, service

    @staticmethod
    def _get_convener_id(org_group, organization, area, service):
        id_convener = ""
        if org_group is not None:
            id_convener += org_group.organization_group_id + "-"
        else:
            id_convener += "x-"

        if organization is not None:
            id_convener += organization.organization_id + "-"
        else:
            id_convener += "x-"

        if area is not None:
            id_convener += area.area_id + "-"
        else:
            id_convener += "x-"

        if service is not None:
            id_convener += service.service_id
        else:
            id_convener += "x"

        return id_convener

    @staticmethod
    def _parse_convener(data):
        try:
            org_group, organization, area, service = ExtractGrantedBenefits._parse_convener_components(data)
        except AttributeError:
            raise Exception()
        convener_id = ExtractGrantedBenefits._get_convener_id(org_group, organization, area, service)
        convener_inside_ids = convener_id.split("-")
        convener_inside_ids = [x if x != "x" else None for x in convener_inside_ids]
        convener = Convener(
            id=convener_id,
            organization_group_id=convener_inside_ids[0],
            organization_id=convener_inside_ids[1],
            area_id=convener_inside_ids[2],
            service_id=convener_inside_ids[3]
        )

        return org_group, organization, area, service, convener

    @staticmethod
    def _parse_granted_benefit(data, convener_id):
        beneficiary = data.get("beneficiary")
        granted = data.get("granted")
        granted_benefit = GrantedBenefit(
            oid=data.get("oid"),
            benefit_id=data.get("benefitId"),
            name=data.get("nameByLang").get("SPANISH"),
            regulation=data.get("regulationByLang").get("SPANISH"),
            beneficiary_id=beneficiary.get("id"),
            beneficiary_name=beneficiary.get("name"),
            granted_date=granted.get("date"),
            granted_amount=granted.get("amount"),
            import_package_oid=data.get("importPackageOid"),
            convener_id=convener_id
        )
        return granted_benefit

    @staticmethod
    def _create_insert_statement_list(**dict_objects):
        insert_statements = []
        ins_stmt = insert(OrganizationGroup).values(
            organization_group_id=dict_objects['org_group'].organization_group_id,
            organization_group_name=dict_objects['org_group'].organization_group_name
        ).on_conflict_do_nothing()
        insert_statements.append(ins_stmt)

        ins_stmt = insert(Organization).values(
            organization_id=dict_objects['organization'].organization_id,
            organization_name=dict_objects['organization'].organization_name
        ).on_conflict_do_nothing()
        insert_statements.append(ins_stmt)
        try:
            ins_stmt = insert(Area).values(
                area_id=dict_objects['area'].area_id,
                area_name=dict_objects['area'].area_name
            ).on_conflict_do_nothing()
            insert_statements.append(ins_stmt)
        except AttributeError:
            """ No area object in the answer """

        try:
            ins_stmt = insert(Service).values(
                service_id=dict_objects['service'].service_id,
                service_name=dict_objects['service'].service_name
            ).on_conflict_do_nothing()
            insert_statements.append(ins_stmt)
        except AttributeError:
            """ No service object in the answer """

        ins_stmt = insert(Convener).values(id=dict_objects['convener'].id,
                                           organization_group_id=dict_objects['convener'].organization_group_id,
                                           organization_id=dict_objects['convener'].organization_id,
                                           area_id=dict_objects['convener'].area_id,
                                           service_id=dict_objects['convener'].service_id
                                        ).on_conflict_do_nothing()
        insert_statements.append(ins_stmt)

        ins_stmt = insert(GrantedBenefit).values(
            oid=dict_objects['benefit'].oid,
            benefit_id=dict_objects['benefit'].benefit_id,
            name=dict_objects['benefit'].name,
            regulation=dict_objects['benefit'].regulation,
            beneficiary_id=dict_objects['benefit'].beneficiary_id,
            beneficiary_name=dict_objects['benefit'].beneficiary_name,
            granted_date=dict_objects['benefit'].granted_date,
            granted_amount=dict_objects['benefit'].granted_amount,
            import_package_oid=dict_objects['benefit'].import_package_oid,
            convener_id=dict_objects['benefit'].convener_id,
        ).on_conflict_do_nothing()
        insert_statements.append(ins_stmt)

        return insert_statements

    @staticmethod
    def _process_expected_exception(error_url, item, error):
        print(f"---------------------------- PROCESS FAILED: {mp.current_process().name} --------------------------- ", flush=True)
        print(f"{error_url} \n {item}")
        print(error)
        item["url"] = error_url
        with open(ERROR_FILE_PATH, 'a') as error_file:
            error_file.write(json.dumps(item))
            error_file.write(",\n")

    @staticmethod
    def _process_page_data(url):
        engine = create_engine(DB_CONNECTION_URL, echo=False)
        data = ExtractGrantedBenefits._handle_request_call(url)
        process_name = mp.current_process().name
        with Session(engine) as session:
            for item in data:
                org_group, organization, area, service, convener = ExtractGrantedBenefits._parse_convener(item.get("convener"))
                granted_benefit = ExtractGrantedBenefits._parse_granted_benefit(item, convener.id)
                try:
                    statement_list = ExtractGrantedBenefits._create_insert_statement_list(org_group=org_group, organization=organization,
                                                                                          area= area, service=service,
                                                                                          convener=convener, benefit=granted_benefit)
                except AttributeError as e:
                    print("HAY UN ERROR", flush=True)
                    ExtractGrantedBenefits._process_expected_exception(url, item, e)
                    raise Exception()
                try:
                    for stt in statement_list:
                        session.execute(stt)
                    session.commit()

                except IntegrityError as e:
                    print("HAY UN ERROR", flush=True)
                    ExtractGrantedBenefits._process_expected_exception(url, item, e)
                    raise Exception()

    def update_progress_bar(self, *a):
        self.pbar.update()

    def _parallel_run(self):

        self.pbar = tqdm(iterable=range(INDEX, self._pagination_factor))
        with mp.Pool(processes=8) as pool:
            for page_number in range(INDEX, self._pagination_factor):
                petition_page_number = page_number + 1
                url = self._BASE_URL.format(ITEMS_PER_PETITION, petition_page_number)
                res = pool.apply_async(ExtractGrantedBenefits._process_page_data, (url,), callback=self.update_progress_bar)
                """ DEBUG SILENT ERRORS """

            pool.close()
            pool.join()
    
    def _sequential_run(self):
        for page_number in tqdm(range(INDEX, self._pagination_factor)):
            petition_page_number = page_number + 1
            url = self._BASE_URL.format(ITEMS_PER_PETITION, petition_page_number)
            ExtractGrantedBenefits._process_page_data(url)

    def run(self):
        parallelize = True
        if parallelize:
            self._parallel_run()
        else:
            self._sequential_run()


if __name__ == '__main__':
    # No se ha hecho la extracción entera bien. Se han conseguido 546261 registros de un total de 759661
    # Ahora hay que aprovechar para hacerlo incremental
    INDEX = 0
    egb = ExtractGrantedBenefits()
    egb.run()
    # url = ""
    # x = {'oid': '7C2DA529-E825-4FCF-BCD5-26673D971122', 'benefitId': '1503230006', 'nameByLang': {'SPANISH': 'PROGRAMA GLOBAL LEHIAN 2015', 'BASQUE': 'GLOBAL LEHIAN PROGRAMA (2015)'}, 'regulationByLang': {'SPANISH': 'Fecha de Publicacion en BOPV 07/05/2015', 'BASQUE': 'EHAAn argitaratu den eguna 2015/05/07'}, 'convener': {'organizationGroup': {'id': '00', 'nameByLang': {'SPANISH': 'Gobierno Vasco', 'BASQUE': 'Eusko Jaurlaritza'}}, 'organization': {'id': '00100', 'nameByLang': {'SPANISH': 'ADMINISTRACIÓN GENERAL DE LA CAE', 'BASQUE': 'EAE-KO ADMINISTRAZIO OROKORRA'}}, 'area': {'id': '03', 'nameByLang': {'SPANISH': 'DESARROLLO ECONOMICO E INFRAESTRUCTURAS', 'BASQUE': 'EKONOMIAREN GARAPENA ETA AZPIEGITURAK'}}, 'service': {'id': '0323', 'nameByLang': {}}}, 'beneficiary': {'id': 'F20091740', 'name': 'PINGON S.COOP.'}, 'granted': {'date': '2015-12-29', 'amount': 2747.35}, 'importPackageOid': '73666C1D-FAFB-4A5C-932D-8E23774538A8'}
    # egb._process_expected_exception(url, x, Exception())
