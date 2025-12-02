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

    @classmethod
    def update_setting(cls, file_name, key, value):
        settings = cls.load_settings(file_name)
        settings[key] = value
        cls.save_settings(file_name, settings)

    @classmethod
    def delete_setting(cls, file_name, key, value):
        settings = cls.load_settings(file_name)

        for i, item in enumerate(settings):
            if item.get(key) == value:
                del profiles[i]
                break
        
        Settings.save_settings(self.SETTINGS_FILE, profiles)