from .config import PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS


from pydantic import BaseModel, Field

class CampaignModel(BaseModel):
    key: str
    title: str
    region_id: int | None = None
    region_name: str | None = None
    personal_account: str = Field(
        min_length=PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS,
        max_length=PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS,
        pattern=rf'^[1-9][0-9]{{{PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS - 1}}}$',
        description=f'ровно {PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS}',
    )


class SubscriberDataModel(BaseModel):
    subscreber_id: int
    address: str
    personal_account: str
    counters: list[CounterDataModel]


class CounterDataModel(BaseModel):
    counter_id: int
    counter_number: str 
    value_last: str
    checking_data: str


class ProfileModel(BaseModel):
    profile_name: str
    campaigns: list[CampaignModel] = []
