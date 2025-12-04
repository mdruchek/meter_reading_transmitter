import json

from .config import SETTINGS_FILE


class Settings:
    @classmethod
    def load_settings(cls):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4, ensure_ascii=False)
            return []

    @classmethod
    def save_settings(cls, settings):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)

    @classmethod
    def update_setting(cls, key, value):
        settings = cls.load_settings(SETTINGS_FILE)
        settings[key] = value
        cls.save_settings(SETTINGS_FILE, settings)

    @classmethod
    def delete_setting(cls, key, value):
        settings: list = cls.load_settings(SETTINGS_FILE)

        for i, setting in enumerate(settings):
            if setting.get(key) == value:
                del settings[i]
                break
        
        Settings.save_settings(SETTINGS_FILE, settings)