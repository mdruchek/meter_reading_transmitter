from typing import Any
from pydantic import BaseModel

class CampaignModel(BaseModel):
    key: str
    title: str
    region_id: int | None = None
    region_name: str | None = None
    personal_account: str


class ProfileModel(BaseModel):
    profile_name: str
    campaigns: list[CampaignModel] = []
