"""
An application for transmitting meter readings
"""
import requests
import toga
from toga import Box, Button, Label, TextInput, MainWindow, Selection
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class MeterReadingTransmitter(toga.App):

    toga.Widget.DEBUG_LAYOUT_ENABLED = True

    def startup(self):
        self.main_box = Box()
        self.view_box = Box(style=Pack(direction=COLUMN, flex=1))
        self.main_box.add(self.view_box)
        self.show_profiles_view(widget=None)
        self.main_window = MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def show_profiles_view(self, widget):
        self.view_box.clear()

        profiles_box = Box(style=Pack(direction=COLUMN), flex=1)
        create_profile_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        create_profile_btn = Button(
            text='Создать профиль',
            on_press=self.show_create_profile_view
        )

        create_profile_btn_box.add(create_profile_btn)
        self.view_box.add(profiles_box, create_profile_btn_box)
        # self.main_box.add(self.view_box)

    def show_create_profile_view(self, widget):
        self.view_box.clear()

        name_profile_box = Box(style=Pack(direction=ROW, flex=0))
        name_profile_label = Label(style=Pack(flex=0), text='Имя профиля')
        name_profile_txt_input = TextInput(style=Pack(flex=1))
        name_profile_box.add(name_profile_label, name_profile_txt_input)

        campaign_box = Box(style=Pack(direction=COLUMN, flex=1))

        choose_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        choose_campaign_btn = Button(
            style=Pack(flex=1),
            text='Выбрать кампанию',
            on_press=self.show_choice_campaign_view
        )

        choose_campaign_btn_box.add(choose_campaign_btn)

        create_profile_box = Box(style=Pack(direction=ROW, flex=0))
        return_btn = Button(text='Назад', style=Pack(flex=1), on_press=self.show_profiles_view)
        create_profile_btn = Button(text='Создать', style=Pack(flex=1))
        create_profile_box.add(return_btn, create_profile_btn)

        self.view_box.add(name_profile_box, campaign_box, choose_campaign_btn_box, create_profile_box)

    def show_choice_campaign_view(self, widget):
        self.view_box.clear()

        campaigns_box = Box(style=Pack(direction=ROW, flex=1))

        campaign_kvc_btn = Button(
            style=Pack(flex=1),
            text=self.KVC.name,
            on_press=lambda widget: self.KVC.show_create_profile_campaign_view(self, widget)
        )

        campaigns_box.add(campaign_kvc_btn)

        return_btn_box = Box(style=Pack(direction=ROW, flex=0))

        return_btn = Button(
            style=Pack(flex=1),
            text='Назад',
            on_press=self.show_create_profile_view
        )

        return_btn_box.add(return_btn)

        self.view_box.add(campaigns_box, return_btn_box)


    class KVC:
        name = 'КВЦ'

        @classmethod
        def show_create_profile_campaign_view(cls, app_instance: "MeterReadingTransmitter", widget):
            app_instance.view_box.clear()

            region_box = Box(style=Pack(direction=COLUMN, flex=0))
            regions = cls.get_active_ctr_regions()
            region_selection = Selection(items=regions, accessor="name")
            region_box.add(region_selection)

            personal_account_box = Box(style=Pack(direction=ROW, flex=1))
            personal_account_label = Label(text='Лицевой счет:', style=Pack(flex=0))
            personal_account_txt_input = TextInput(style=Pack(flex=1))
            personal_account_box.add(personal_account_label, personal_account_txt_input)

            add_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))
            add_campaign_btn = Button(text='Добавить кампанию')
            add_campaign_btn_box.add(add_campaign_btn)

            return_btn_box = Box(style=Pack(direction=ROW, flex=0))

            return_btn = Button(
                style=Pack(flex=1),
                text='Назад',
                on_press=app_instance.show_choice_campaign_view
            )

            return_btn_box.add(return_btn)

            app_instance.view_box.add(region_box, personal_account_box, add_campaign_btn_box, return_btn_box)

        @staticmethod
        def get_active_ctr_regions():
            url = 'https://send.kvc-nn.ru/api/ControlIndications/GetActiveCtrRegions'
            response = requests.post(url)
            regions_json = response.json()
            print(regions_json)
            return regions_json

        @staticmethod
        def get_locations_for_region(region_id):
            url = 'https://send.kvc-nn.ru/api/ControlIndications/GetLocationsForRegion'
            params = {'idRegion': region_id}
            response = requests.post(url, params=params)
            locations_for_region_json = response.json()
            return locations_for_region_json

def main():
    return MeterReadingTransmitter()
