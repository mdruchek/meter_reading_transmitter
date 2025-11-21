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
        self.profile_creation_window_is_open = False

        main_box = Box(style=Pack(direction=COLUMN, margin=10))

        profile_box = Box(style=Pack(direction=COLUMN), flex=1)
        create_profile_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        create_profile_btn = Button(
            text='Создать профиль',
            on_press=self.open_create_profile_window
        )

        create_profile_btn_box.add(create_profile_btn)
        main_box.add(profile_box, create_profile_btn_box)

        self.main_window = MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def open_create_profile_window(self, widget):
        if self.profile_creation_window_is_open:
            return

        self.create_profile_window = toga.Window(
            title='Создание профиля'
        )
        self.create_profile_window.on_close = self.close_create_profile_window

        main_box = Box(style=Pack(direction=COLUMN))

        name_profile_box = Box(style=Pack(direction=ROW, flex=0))
        name_profile_label = Label(style=Pack(flex=0), text='Имя профиля')
        name_profile_txt_input = TextInput(style=Pack(flex=1))
        name_profile_box.add(name_profile_label, name_profile_txt_input)

        campaign_box = Box(style=Pack(direction=COLUMN, flex=1))

        choose_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        choose_campaign_btn = Button(
            text='Выбрать кампанию',
            on_press=self.open_choice_campaign_window
        )

        choose_campaign_btn_box.add(choose_campaign_btn)

        create_profile_box = Box(style=Pack(direction=ROW, flex=0))
        close_window_btn = Button(text='Закрыть', on_press=self.close_create_profile_window)
        create_profile_btn = Button(text='Создать')
        create_profile_box.add(close_window_btn, create_profile_btn)

        main_box.add(name_profile_box, campaign_box, choose_campaign_btn_box, create_profile_box)

        self.create_profile_window.content = main_box
        self.create_profile_window.show()
        self.profile_creation_window_is_open = True

    def close_create_profile_window(self, widget):
        self.create_profile_window.close()
        self.profile_creation_window_is_open = False

    def open_choice_campaign_window(self, widget):

        self.choice_campaign_window = toga.Window(
            title='Выбор кампании'
        )

        main_box = Box(style=Pack(direction=COLUMN))

        campaigns_box = Box(style=Pack(direction=ROW, flex=0))

        campaign_kvc_btn = Button(
            text=self.KVC.name,
            on_press=self.KVC.open_create_profile_campaign_window
        )

        campaigns_box.add(campaign_kvc_btn)

        main_box.add(campaigns_box)

        self.choice_campaign_window.content = main_box
        self.choice_campaign_window.show()


    class KVC:
        name = 'КВЦ'

        @classmethod
        def open_create_profile_campaign_window(cls, widget):
            create_profile_campaign_window = toga.Window(title='КВЦ')
            main_box = Box(style=Pack(direction=COLUMN))

            region_box = Box(style=Pack(direction=COLUMN, flex=0))
            regions = cls.request_list_regions()
            region_selection = Selection(items=regions, accessor="name")
            region_box.add(region_selection)

            personal_account_box = Box(style=Pack(direction=ROW, flex=0))
            personal_account_label = Label(text='Лицевой счет:', style=Pack(flex=0))
            personal_account_txt_input = TextInput(style=Pack(flex=1))
            personal_account_box.add(personal_account_label, personal_account_txt_input)

            add_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))
            add_campaign_btn = Button(text='Добавить кампанию')
            add_campaign_btn_box.add(add_campaign_btn)

            main_box.add(region_box, personal_account_box, add_campaign_btn_box)

            create_profile_campaign_window.content = main_box
            create_profile_campaign_window.show()

        @staticmethod
        def request_list_regions():
            response = requests.post('https://send.kvc-nn.ru/api/ControlIndications/GetActiveCtrRegions')
            regions_json = response.json()
            return regions_json


def main():
    return MeterReadingTransmitter()
