from dataclasses import dataclass, field


@dataclass
class CampaignData:
    name: str
    region_id: int | None = None
    region_name: str | None = None
    personal_account: str | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        return {
            "campaign_name": self.name,
            "region_id": self.region_id,
            "region_name": self.region_name,
            "personal_account": self.personal_account,
        }


@dataclass
class Profile:
    profile_name: str
    campaigns: list[dict[str, str | int | None]] = field(default_factory=list)
