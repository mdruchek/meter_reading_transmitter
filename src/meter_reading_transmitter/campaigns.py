from abc import ABC, abstractmethod
from pydantic import ValidationError
import requests

from .models import CampaignModel


class CampaignInterface(ABC):
    key: str
    title: str

    @staticmethod
    @abstractmethod
    def get_abonent_data(
        _campaign_model: CampaignModel
    ):
        ...

    @staticmethod
    @abstractmethod
    def make_campaign(
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
    def get_abonent_data(_campaign_model: CampaignModel):
        region_id = _campaign_model.region_id
        personal_account = _campaign_model.personal_account
        locations_for_region = KVCCampaign.get_locations_for_region(_region_id=region_id)
        abonent_info = KVCCampaign.get_abonent_info(locations_for_region, _personal_account=personal_account)
        abonent_id = abonent_info['id']
        location_for_region = next((loc for loc in locations_for_region if loc['db_name'] == 'co_vyksa'), None)
        message_for_abonent = KVCCampaign.get_message_for_abonent(_location_for_region=location_for_region, _abonent_id=abonent_id)
        cnt_list = KVCCampaign.get_cnt_list(_location_for_region=location_for_region, _personal_account=personal_account)
        print(cnt_list)
        ctr_days = KVCCampaign.get_ctr_days(_location_for_region=location_for_region, _personal_account=personal_account)
        print(ctr_days)
        ctr_list = KVCCampaign.get_ctr_list(_location_for_region=location_for_region, _personal_account=personal_account, _counter_id=58946)
        print(ctr_list)
        return {
            'message': message_for_abonent
        }

    @staticmethod
    def make_campaign_profile(
        _region_id: int,
        _region_name: str,
        _personal_account: str,
    ) -> CampaignModel | str:

        personal_account = (_personal_account or "").strip()

        try:
            campaign_profile = CampaignModel(
                key=KVCCampaign.key,
                title=KVCCampaign.title,
                region_id=_region_id,
                region_name=_region_name,
                personal_account=personal_account,
            )

            return campaign_profile

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
