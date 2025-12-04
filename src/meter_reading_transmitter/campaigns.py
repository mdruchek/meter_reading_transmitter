from abc import ABC, abstractmethod
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
    def get_abonent_info(location_for_region: dict) -> dict:
        url = "https://send.kvc-nn.ru/api/ControlIndications/GetAbonentInfo"
        response = requests.post(url, json=location_for_region)
        return response.json()

    @staticmethod
    def make_campaign_profile(
        region_id: int,
        region_name: str,
        personal_account: str,
    ) -> CampaignModel:
        return CampaignModel(
            key=KVCCampaign.key,
            title=KVCCampaign.title,
            region_id=region_id,
            region_name=region_name,
            personal_account=personal_account,
        )
        
        
class TNScompaign(CompaignInterface):
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
}
