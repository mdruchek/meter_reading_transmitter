from abc import ABC, abstractmethod
import requests

from .models import CampaignData


CAMPAIGN_REGISTRY: dict[str, type[CampaignInterface]] = {
    KVCCampaign.key: KVCCampaign,
}


class CampaignInterface(ABC):
    key: str
    title: str

    @staticmethod
    @abstractmethod
    def make_campaign(
        personal_account: str,
    ) -> CampaignData:
        ...


class KVCCampaign(CampaignInterface):
    key = "kvc"
    title = "КВЦ"

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
    def make_campaign(
        region_id: int,
        region_name: str,
        personal_account: str,
    ) -> CampaignData:
        return CampaignData(
            key='title',
            title="КВЦ",
            region_id=region_id,
            region_name=region_name,
            personal_account=personal_account,
        )
