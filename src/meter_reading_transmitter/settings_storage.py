import json


class Settings:
    @classmethod
    def load_settings(cls, file_name: str):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4, ensure_ascii=False)
            return []

    @classmethod
    def save_settings(cls, file_name: str, settings):
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)
