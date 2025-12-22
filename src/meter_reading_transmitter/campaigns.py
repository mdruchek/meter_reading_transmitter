import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json

from requests.sessions import should_bypass_proxies
from pydantic import ValidationError
import requests
from bs4 import BeautifulSoup 

from .models import CampaignModel, SubscriberKVCCampaignModelSettings, SubscriberKCVCampaignModelDataUpload, CounterDataModel


class CampaignInterface(ABC):
    key: str
    title: str
   
    @staticmethod
    @abstractmethod
    def api_request(method: str, url: str, *, timeout: float = 10, **kwargs):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError):
            return None

    @staticmethod
    @abstractmethod
    def get_subscriber_data(
        _campaign_model: CampaignModel
    ):
        ...

    @staticmethod
    @abstractmethod
    def make_campaign_profile(
        _key: str,
        _title: str,
        _region_required: bool
    ) -> CampaignModel:
        ...


class KVCCampaign(CampaignInterface):
    key = "kvc"
    title = "КВЦ"
    region_required = True

    @staticmethod
    def get_active_regions() -> list[dict]:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetActiveCtrRegions"
        resp = requests.post(url)
        return resp.json()

    @staticmethod
    def get_locations_for_region(_region_id: int) -> list[dict]:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion"
        params = {"idRegion": _region_id}
        response = requests.post(url, params=params)
        return response.json()

    @staticmethod
    def get_abonent_info(_location_for_region: list[dict[str, str | int]], _personal_account: str) -> dict:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetAbonentInfo"
        location_for_region_with_personal_account = {
            "servDbs": _location_for_region,
            "lc": _personal_account,
            "target": 0
        }

        response = requests.post(url, json=location_for_region_with_personal_account)
        return response.json()

    @staticmethod
    def get_message_for_abonent(_location_for_region: list[dict[str, str | int]], _abonent_id: int):
        url = 'https://send.kvc-nn.ru/api/ControlIndications/GetMessageForAbonent'
        request_data = {
            "servDb": _location_for_region,
            "idA": _abonent_id
        }
        response = requests.post(url, json=request_data)
        return response.json()

    @staticmethod
    def get_cnt_list(_location_for_region: list[dict[str, str | int]], _personal_account: str):
        url = 'https://send.kvc-nn.ru/api/ControlIndications/GetCntList'
        request_data = {
            "servDb": _location_for_region,
            "lc": _personal_account
        }
        response = requests.post(url, json=request_data)
        return response.json()

    @staticmethod
    def get_ctr_days(_location_for_region: list[dict[str, str | int]], _personal_account: str):
        url = 'https://send.kvc-nn.ru/api/ControlIndications/GetCtrDays'
        request_data = {
            "servDb": _location_for_region,
            "lc": _personal_account
        }
        response = requests.post(url, json=request_data)
        return response.json()

    @staticmethod
    def get_ctr_list(_location_for_region: list[dict[str, str | int]], _personal_account: str, _counter_id: int):
        url = 'https://send.kvc-nn.ru/api/ControlIndications/GetCtrList'
        request_data = {
            "servDb": _location_for_region,
            "lc": _personal_account,
            "idCnt": _counter_id
        }
        response = requests.post(url, json=request_data)
        return response.json()

    @staticmethod
    def  api_request(method: str, url: str, *, timeout: float = 3, **kwargs):
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.ok, response.json()


    @staticmethod
    def get_subscriber_data(_subscriber_campaign: SubscriberKVCCampaignModelSettings):
        region_id = _subscriber_campaign.region_id
        personal_account = _subscriber_campaign.personal_account

        response_ok, locations_for_region = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion',
            params={"idRegion": region_id}
        )

        response_ok, subscriber_info = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetAbonentInfo',
            json={
                "servDbs": locations_for_region,
                "lc": personal_account,
                "target": 0
            }
        )

        print(subscriber_info)

        subscriber_id = subscriber_info['id']

        location_for_region = next((loc for loc in locations_for_region if loc['db_name'] == 'co_vyksa'), None)

        response_ok, message_for_subscriber = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetMessageForAbonent',
            json = {
                "servDb": location_for_region,
                "idA": subscriber_id
            }
        )

        print(message_for_subscriber)

        response_ok, counters_list = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetCntList',
            json = {
                "servDb": location_for_region,
                "lc": personal_account
            }
        )

        print(counters_list)

        response_ok, tranzit_days = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetCtrDays',
            json = {
                "servDb": location_for_region,
                "lc": personal_account
            }
        )

        response_ok, counter_list = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetCtrList',
            json = {
                "servDb": location_for_region,
                "lc": personal_account,
                "idCnt": 58946
            }
        )

        city = subscriber_info['tn_name']
        street = subscriber_info['st_name']
        house_and_apartment_number = subscriber_info['dom_kv']
        subscriber_address = f'{city} {street} {house_and_apartment_number}'
        personal_account = subscriber_info['lc'].strip()
        subscriber_id = subscriber_info['id']

        counters = []

        for counter in counters_list:
            counter_id = counter['id_cnt']
            counter_server = counter['server']
            counter_db_name = counter['db_name']
            counter_id_a = counter['id_a']
            counter_id_type = counter['id_type']
            counter_date_b = counter['dat_b']
            counter_number: str = counter['number'].strip()
            counter_value_last = counter['c_val_lst']
            counter_checking_data = counter['dat_sn']
            
            counter_model = CounterDataModel(
                id=counter_id,
                server=counter_server,
                db_name=counter_db_name,
                id_a=counter_id_a,
                id_type=counter_id_type,
                date_b=counter_date_b,
                number=counter_number,
                value_last=counter_value_last,
                checking_data=counter_checking_data,
                server_data=location_for_region
            )

            counters.append(counter_model)

        return SubscriberKCVCampaignModelDataUpload(
            id=subscriber_id,
            address=subscriber_address,
            counters=counters,
            **_subscriber_campaign.model_dump()
        )

    @staticmethod
    def sending_data_counter(counter: CounterDataModel, value_sending: str):
        response_ok, response_json = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/InsertCtr',
            json={
                "servDb": counter.server_data,
                "ctrForInsert": [
                    {
                        "idCnt": counter.id,
                        "server": counter.server,
                        "db_name": counter.db_name,
                        "idA": counter.id_a,
                        "val": value_sending,
                        "idType": counter.id_type,
                        "date": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                        "datB": counter.date_b
                    }
                ],
                "notes": "Передано через сайт",
                "category": 0
            }
        )

        return response_ok

    @staticmethod
    def make_subscriber_campaign_profile(
        _region_id: int,
        _region_name: str,
        _personal_account: str,
    ) -> CampaignModel | str:

        personal_account = (_personal_account or "").strip()

        try:
            subscriber_campaign = SubscriberKVCCampaignModelSettings(
                campaign=CampaignModel(
                    title=KVCCampaign.title,
                    key=KVCCampaign.key
                ),
                region_id=_region_id,
                region_name=_region_name,
                personal_account=personal_account,
            )

            return subscriber_campaign

        except ValidationError as e:
            message_error = 'лицевой счет жолжен содержать 10 цифр'
            return message_error



class TNSCampaign(CampaignInterface):
    key = "tns"
    title = "ТНС"
    region_required = False   # регион не вводится, только ЛС

    @staticmethod
    def api_request(method: str, url: str, *, timeout: float = 5, **kwargs) -> requests.Response:
        resp = requests.request(method, url, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp

    @staticmethod
    def _get_csrf_and_first_html(session: requests.Session) -> tuple[str, str]:
        """Загрузка /populationsend-and-pay → csrf + полный HTML."""
        resp = session.get("https://nn.tns-e.ru/populationsend-and-pay")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "delementcsrf"})
        csrf = csrf_input["value"] if csrf_input else ""
        return csrf, resp.text

    @staticmethod
    def _step_ls(session: requests.Session, csrf: str, personal_account: str) -> str:
        """Шаг ввода ЛС: POST на handleAjax, получаем HTML с адресом, lshash и счётчиками."""
        url = (
            "https://nn.tns-e.ru/"
            "bitrix/services/main/ajax.php?mode=class&c=delementform.submittingmeterreadings&action=handleAjax"
        )
        data = {
            "delementcsrf": csrf,
            "delementformid": "delementform.submittingmeterreadings",
            "ls": personal_account,
            "currentstep": "0",
            "nextstep": "1",
        }
        resp = session.post(url, data=data)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def _parse_subscriber_html(html: str, personal_account: str) -> tuple[str, list[CounterTNSDataModel]]:
        """Парсинг HTML из шага 1: адрес + список счётчиков и их последние показания."""
        soup = BeautifulSoup(html, "html.parser")

        # адрес абонента — в теге <address> или похожем фрагменте
        address_tag = soup.find("address")
        if address_tag:
            address = " ".join(address_tag.get_text(strip=True).split())
        else:
            # запасной вариант: ищем по тексту лицевого счёта рядом
            address = ""

        counters: list[CounterTNSDataModel] = []

        # поля вида <input name="reading38315760" value="5809">
        for inp in soup.find_all("input", {"name": re.compile(r"^readingd+$")}):
            name = inp.get("name")
            value = inp.get("value") or ""
            try:
                value_last = float(value.replace(",", "."))
            except ValueError:
                value_last = 0

            # номер счётчика обычно рядом в разметке, поищем в соседях
            number = ""
            label = inp.find_parent().find_previous(string=re.compile(r"d"))
            if label:
                number = label.strip()

            counter = CounterTNSDataModel(
                id=name,               # пока используем имя поля как id
                number=number,
                value_last=value_last,
                checking_date=None,    # дату поверки можно будет добрать, когда найдём в HTML
                raw_html=str(inp),
            )
            counters.append(counter)

        return address, counters

    @staticmethod
    def get_subscriber_data(_subscriber_campaign: SubscriberTNSCampaignModelSettings):
        personal_account = _subscriber_campaign.personal_account.strip()

        session = requests.Session()

        csrf, _ = TNSCampaign._get_csrf_and_first_html(session)

        html_step1 = TNSCampaign._step_ls(session, csrf, personal_account)

        address, counters = TNSCampaign._parse_subscriber_html(html_step1, personal_account)

        # id абонента TNS явно не отдаёт в API‑виде, оставляем None
        return SubscriberTNSCampaignModelDataUpload(
            id=None,
            address=address,
            personal_account=personal_account,
            counters=counters,
            campaign=_subscriber_campaign.campaign,
        )

    @staticmethod
    def sending_data_counter(counter: CounterTNSDataModel, value_sending: str, personal_account: str):
        """Отправка показаний по одному счётчику."""
        session = requests.Session()
        csrf, _ = TNSCampaign._get_csrf_and_first_html(session)

        url = (
            "https://nn.tns-e.ru/"
            "bitrix/services/main/ajax.php?mode=class&c=delementform.submittingmeterreadings&action=handleAjax"
        )

        data = {
            "delementcsrf": csrf,
            "delementformid": "delementform.submittingmeterreadings",
            "ls": personal_account,
            # lshash можно дополнительно распарсить из html шага 1, когда потребуется
            "policy": "Y",
            "policy2": "Y",
            "requestType": "sendReadings",
            "currentstep": "1",
            "nextstep": "2",
            counter.id: value_sending,
        }

        resp = session.post(url, data=data)
        resp.raise_for_status()
        return resp.text



CAMPAIGN_REGISTRY: dict[str, type[CampaignInterface]] = {
    KVCCampaign.key: KVCCampaign,
    TNScompaign.key: TNScompaign
}
