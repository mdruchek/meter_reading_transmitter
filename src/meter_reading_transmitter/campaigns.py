from abc import ABC, abstractmethod
from pydantic import ValidationError
import requests

from .models import CampaignModel


class CampaignInterface(ABC):
    key: str
    title: str

    @staticmethod
    @abstractmethod
    def make_campaign(
        key: str,
        title: str,
        region_required: bool
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
    def get_locations_for_region(region_id: int) -> list[dict]:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion"
        params = {"idRegion": region_id}
        response = requests.post(url, params=params)
        return response.json()

    @staticmethod
    def get_abonent_info(location_for_region: list[dict[str, str | int]], personal_account: str) -> dict:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetAbonentInfo"
        location_for_region_with_personal_account = {
            "servDbs": location_for_region,
            "lc": personal_account,
            "target": 0
        }

        response = requests.post(url, json=location_for_region_with_personal_account)
        return response.json()

    @staticmethod
    def get_message_for_abonent(location_for_region: list[dict[str, str | int]], id_abonent: int):
        url = 'https://send.kvc-nn.ru/api/ControlIndications/GetMessageForAbonent'
        request_data = {
            "servDb": location_for_region[0],
            "idA": id_abonent
        }
        response = requests.post(url, json=request_data)
        return response.json()

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
