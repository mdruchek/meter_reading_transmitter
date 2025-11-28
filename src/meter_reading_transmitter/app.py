"""
An application for transmitting meter readings
"""
import json
import os
from zipfile import stringFileHeader

import requests
import toga
from toga import Box, Button, Label, TextInput, MainWindow, Selection
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class MeterReadingTransmitter(toga.App):

    # toga.Widget.DEBUG_LAYOUT_ENABLED = True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

    def __init__(self, **kwargs):
        super().__init__(formal_name='передача показаний счетчиков', **kwargs)

        self.view_box = toga.Box(style=Pack(direction=COLUMN))

        self.header_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        self.body_box = toga.Box(style=Pack(direction=COLUMN, margin=5, flex=1))
        self.footer_box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        self.view_box.add(self.header_box, self.body_box, self.footer_box)

        self.campaigns_box = Box(style=Pack(flex=1, direction=COLUMN))

    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.view_box
        self.show_profiles_view(widget=None)
        self.main_window.show()

    def show_profiles_view(self, widget):
        self.header_box.clear()
        header_label = toga.Label(text='профили', style=Pack(flex=1))
        self.header_box.add(header_label)

        self.body_box.clear()
        profiles_box = Box(style=Pack(direction=COLUMN, flex=1))
        self.body_box.add(profiles_box)

        self.footer_box.clear()
        create_profile_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        create_profile_btn = Button(
            text='Создать профиль',
            on_press=self.show_create_profile_view
        )

        create_profile_btn_box.add(create_profile_btn)
        self.footer_box.add(profiles_box, create_profile_btn_box)

    def show_create_profile_view(self, widget):
        self.header_box.clear()
        header_label = Label(text='создание нового профиля')
        self.header_box.add(header_label)

        self.body_box.clear()
        name_profile_box = Box(style=Pack(direction=ROW, flex=0))
        name_profile_label = Label(style=Pack(flex=0), text='Имя профиля')
        name_profile_txt_input = TextInput(style=Pack(flex=1))
        name_profile_box.add(name_profile_label, name_profile_txt_input)
        self.body_box.add(name_profile_box, self.campaigns_box)

        # def get_settings_campaign_for_add(settings_for_add):
        #     campaign_name = settings_for_add['campaign_name']
        #     personal_account = settings_for_add['personal_account']
        #     campaign_box = Box(style=Pack(direction=COLUMN, flex=0))
        #     text_campaign_label = f'кампания {campaign_name}, лицевой счет {personal_account}'
        #     campaign_label = Label(text=text_campaign_label)
        #     campaign_box.add(campaign_label)
        #     campaigns_box.add(campaign_box)
        #     print(campaign_box.children)
        #     print(campaigns_box)

            # settings_upload = self.Settings.load_settings(self.SETTINGS_FILE)
            # if settings_upload:
            #     settings_upload.append(settings_for_add)
            # else:
            #     settings_upload = [settings_for_add,]
            # self.Settings.save_settings(self.SETTINGS_FILE, settings=settings_upload)

        self.footer_box.clear()
        choose_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        choose_campaign_btn = Button(
            style=Pack(flex=1),
            text='Выбрать кампанию',
            on_press=lambda widget: self.show_choice_campaign_view(
                widget=widget
            )
        )

        choose_campaign_btn_box.add(choose_campaign_btn)

        create_profile_box = Box(style=Pack(direction=ROW, flex=0))
        return_btn = Button(text='Назад', style=Pack(flex=1), on_press=self.show_profiles_view)
        create_profile_btn = Button(text='Создать', style=Pack(flex=1))
        create_profile_box.add(return_btn, create_profile_btn)

        self.footer_box.add( choose_campaign_btn_box, create_profile_box)

    def show_choice_campaign_view(self, widget):
        self.header_box.clear()
        header_label = Label(text='выбор кампании')
        self.header_box.add(header_label)

        self.body_box.clear()
        campaigns_box = Box(style=Pack(direction=ROW, flex=1))

        campaign_kvc_btn = Button(
            style=Pack(flex=1),
            text=self.KVC.name,
            on_press=lambda widget: self.KVC.show_create_profile_campaign_view(
                app_instance=self,
                widget=widget
            )
        )

        campaigns_box.add(campaign_kvc_btn)
        self.body_box.add(campaigns_box)

        self.footer_box.clear()
        return_btn_box = Box(style=Pack(direction=ROW, flex=0))

        return_btn = Button(
            style=Pack(flex=1),
            text='Назад',
            on_press=self.show_create_profile_view
        )

        return_btn_box.add(return_btn)

        self.footer_box.add(return_btn_box)


    class KVC:
        name = 'КВЦ'

        @classmethod
        def show_create_profile_campaign_view(cls, app_instance: "MeterReadingTransmitter", widget):
            app_instance.header_box.clear()
            head_label = Label(text='данные кампании')
            app_instance.header_box.add(head_label)

            app_instance.body_box.clear()
            region_box = Box(style=Pack(direction=COLUMN, flex=0))
            regions = cls.get_active_ctr_regions()
            region_selection = Selection(items=regions, accessor="name")
            region_box.add(region_selection)

            personal_account_box = Box(style=Pack(direction=ROW, flex=1))
            personal_account_label = Label(text='Лицевой счет:', style=Pack(flex=0))
            personal_account_txt_input = TextInput(style=Pack(flex=1))
            personal_account_box.add(personal_account_label, personal_account_txt_input)

            app_instance.body_box.add(region_box, personal_account_box)

            app_instance.footer_box.clear()
            add_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))
            add_campaign_btn = Button(
                style=Pack(flex=1),
                text='Добавить кампанию',
                on_press=lambda widget: cls.add_campaign(
                    app_instance=app_instance,
                    widget=widget,
                    region_id=999,
                    personal_account=555
                )
            )
            add_campaign_btn_box.add(add_campaign_btn)

            return_btn_box = Box(style=Pack(direction=ROW, flex=0))

            return_btn = Button(
                style=Pack(flex=1),
                text='Назад',
                on_press=app_instance.show_choice_campaign_view
            )

            return_btn_box.add(return_btn)

            app_instance.footer_box.add(add_campaign_btn_box, return_btn_box)

        @classmethod
        def add_campaign(cls, app_instance, widget, region_id, personal_account):
            setting_add = {
                    "campaign_name": "квц",
                    "region_id": region_id,
                    "personal_account": personal_account
            }
            campaign_box = Box(style=Pack(flex=0, direction=COLUMN))
            campaign_label = Label(text=f'{setting_add['campaign_name']}')
            campaign_box.add(campaign_label)
            app_instance.campaigns_box.add(campaign_box)

            app_instance.show_create_profile_view(
                widget=widget
            )


        @staticmethod
        def get_active_ctr_regions():
            url = 'https://send.kvc-nn.ru/api/ControlIndications/GetActiveCtrRegions'
            response = requests.post(url)
            regions_json = response.json()
            return regions_json

        @staticmethod
        def get_locations_for_region(region_id):
            url = 'https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion'
            params = {'idRegion': region_id}
            response = requests.post(url, params=params)
            locations_for_region_json = response.json()
            return locations_for_region_json

        @staticmethod
        def get_abonent_info(location_for_region):
            url = 'https://send.kvc-nn.ru/api/ControlIndications/GetAbonentInfo'
            response = requests.post(url)


    class Settings:
        @classmethod
        def load_settings(cls, file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    settings = json.load(file)
            except FileNotFoundError:
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump([], file, indent=4, ensure_ascii=False)
            if 'settings' in locals():
                return settings


        @classmethod
        def update_setting(cls, file_name, key, value):
            settings = cls.load_settings(file_name)
            settings[key] = value
            cls.save_settings(file_name, settings)

        @classmethod
        def delete_setting(cls, file_name, key):
            settings = cls.load_settings(file_name)
            if key in settings:
                del settings[key]
                cls.save_settings(file_name, settings)

        @classmethod
        def save_settings(cls, file_name, settings):
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)


def main():
    return MeterReadingTransmitter()
