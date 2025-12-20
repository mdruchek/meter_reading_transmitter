import os
import sys
import json

from pydantic import ValidationError

from .models import ProfileModel
from pathlib import Path
from .config import SETTINGS_FILE_DESKTOP, SETTINGS_FILE_ANDROID


class Settings:
    settings_file: Path | None = None

    @classmethod
    def init(cls, path: Path) -> None:
        """Задать полный путь к settings.json для текущей платформы."""
        cls.settings_file = path

    @classmethod
    def load_settings(cls):

        try:
            with open(cls.settings_file, "r", encoding="utf-8") as file:
                settings_raw = json.load(file)
                profiles: list[ProfileModel] = []

                for setting in settings_raw:
                    try:
                        profiles.append(ProfileModel(**setting))
                    except ValidationError as e:
                        print("Bad profile in settings.json:", e)

                return profiles
        
        except FileNotFoundError:
            with open(cls.settings_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4, ensure_ascii=False)
            return []

    @classmethod
    def save_settings(cls, profiles: list[ProfileModel]):
        profile_raw = [profile.model_dump() for profile in profiles]
        with open(cls.settings_file, "w", encoding="utf-8") as file:
            json.dump(profile_raw, file, indent=4, ensure_ascii=False)

    @classmethod
    def update_setting(cls, key, value):
        settings = cls.load_settings()
        settings[key] = value
        cls.save_settings(settings)

    @classmethod
    def delete_setting(cls, key, value):
        if key == 'profile_name':
            profiles: list = cls.load_settings()
            profiles = [profile for profile in profiles if profile.profile_name != value]

        Settings.save_settings(profiles)