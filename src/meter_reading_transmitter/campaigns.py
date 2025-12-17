from abc import ABC, abstractmethod
import json

from requests.sessions import should_bypass_proxies
from pydantic import ValidationError
import requests

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
        return response.json()


    @staticmethod
    def get_subscriber_data(_subscriber_campaign: SubscriberKVCCampaignModelSettings):
        region_id = _subscriber_campaign.region_id
        personal_account = _subscriber_campaign.personal_account

        locations_for_region = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion',
            params={"idRegion": region_id}
        )

        subscriber_info = KVCCampaign.api_request(
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

        message_for_subscriber = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetMessageForAbonent',
            json = {
                "servDb": location_for_region,
                "idA": subscriber_id
            }
        )

        print(message_for_subscriber)

        counters_list = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetCntList',
            json = {
                "servDb": location_for_region,
                "lc": personal_account
            }
        )

        print(counters_list)

        tranzit_days = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/GetCtrDays',
            json = {
                "servDb": location_for_region,
                "lc": personal_account
            }
        )

        counter_list = KVCCampaign.api_request(
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
            counter_number: str = counter['number'].strip()
            value_last = counter['c_val_lst']
            checking_data = counter['dat_sn']
            
            counter_model = CounterDataModel(
                id=counter_id,
                number=counter_number,
                value_last=value_last,
                checking_data=checking_data,
            )

            counters.append(counter_model)


        return SubscriberKCVCampaignModelDataUpload(
            campaign=_subscriber_campaign.campaign,
            id=subscriber_id,
            address=subscriber_address,
            personal_account=personal_account,
            counters=counters
        )

    @staticmethod
    def send_data_counters(counters: list[CounterDataModel]):
        response = KVCCampaign.api_request(
            'POST',
            'https://send.kvc-nn.ru/api/ControlIndications/InsertCtr',
            json={
                "servDb": {
                  "server": "DBASES03",
                  "db_name": "co_vyksa",
                  "login": null,
                  "id_user": null
                 },
                 "ctrForInsert": [
                  {
                   "idCnt": 58946,
                   "server": "DBASES03",
                   "db_name": "co_vyksa",
                   "idA": 10021624,
                   "val": "492",
                   "idType": "01",
                   "date": "2025-12-17T06:57:25.000Z",
                   "datB": "2025-11-30T21:00:00.000Z"
                  }
                 ],
                 "notes": "Передано через сайт",
                 "category": 0
                }
        )

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
        
        
class TNScompaign(CampaignInterface):
    key = "tns"
    title = "ТНС"
    region_required = False
    
    @staticmethod
    def make_campaign_profile(
        personal_account: str,
    ) -> CampaignModel:
        return CampaignModel(
            key=KVCCampaign.key,
            title=KVCCampaign.title,
            personal_account=personal_account,
        )


CAMPAIGN_REGISTRY: dict[str, type[CampaignInterface]] = {
    KVCCampaign.key: KVCCampaign,
    TNScompaign.key: TNScompaign
}
