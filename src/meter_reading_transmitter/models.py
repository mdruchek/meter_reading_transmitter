from typing import Any, Dict, TypeVar, Type

from pydantic import BaseModel, Field

from .config import PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS


T = TypeVar('T', bound=BaseModel)

def model_dump(self: T, **kwargs: Any) -> Dict[str, Any]:
    return self.dict(**kwargs)

BaseModel.model_dump = model_dump


class CampaignModel(BaseModel):
    key: str
    title: str


class CounterDataModel(BaseModel):
    id: int
    id_type: str
    number: str
    value_last: str
    checking_data: str


class SubscriberKVCCampaignModelSettings(BaseModel):
    campaign: CampaignModel
    region_id: int | None = None
    region_name: str | None = None
    personal_account: str = Field(
        min_length=PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS,
        max_length=PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS,
        pattern=rf'^[1-9][0-9]{{{PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS - 1}}}$',
        description=f'ровно {PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS}',
    )


class SubscriberKCVCampaignModelDataUpload(SubscriberKVCCampaignModelSettings):
    id: int
    address: str
    counters: list[CounterDataModel]


class ProfileModel(BaseModel):
    profile_name: str
    subscriber_campaigns: list[SubscriberKVCCampaignModelSettings] = []
