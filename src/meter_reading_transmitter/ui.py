"""
An application for transmitting meter readings
"""

import os

import toga
from toga import Box, Button, Label, TextInput, Selection
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .models import ProfileModel, CampaignModel
from .campaigns import CAMPAIGN_REGISTRY, CampaignInterface
from .settings_storage import Settings


class MeterReadingTransmitter(toga.App):
    def __init__(self, **kwargs):
        super().__init__(formal_name="Передача показаний счетчиков", **kwargs)
        
        self.campaign_registry = CAMPAIGN_REGISTRY
        self.current_campaign = None
        self.settings_campaigns_for_add: list[dict] = []
        
        
        self.view_box = Box(style=Pack(direction=COLUMN))
        self.header_box = Box(style=Pack(direction=COLUMN, margin=5))
        self.body_box = Box(style=Pack(direction=COLUMN, margin=5, flex=1))
        self.footer_box = Box(style=Pack(direction=COLUMN, margin=5))

        self.view_box.add(self.header_box, self.body_box, self.footer_box)

        self.campaigns_box = Box(style=Pack(flex=1, direction=COLUMN))

    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.view_box
        self.show_profiles_view(widget=None)
        self.main_window.show()

    def show_profiles_view(self, widget):
        self.header_box.clear()
        header_label = Label(text="Профили", style=Pack(flex=1))
        self.header_box.add(header_label)

        self.body_box.clear()
        profiles = Settings.load_settings()

        profiles_box = Box(style=Pack(direction=COLUMN, flex=1))
        
        if profiles:
            for profile in profiles:
                profile_box = Box(style=Pack(flex=0, direction=ROW))

                profile_btn = Button(
                    id=f'{profile["profile_name"]}_profile',
                    style=Pack(flex=1),
                    text=profile.profile_name,
                )

                profile_edit_btn = Button(
                    id=f'{profile["profile_name"]}_profile_edit',
                    text="Редактировать",
                )

                def profile_del(widget):
                    profile_btn_id = widget.id
                    profile_name_for_del = profile_btn_id[: profile_btn_id.rfind("_profile")]
                    Settings.delete_setting(key='profile_name', value=profile_name_for_del)
                    self.show_profiles_view(widget)

                profile_del_btn = Button(
                    id=f'{profile["profile_name"]}_profile_del',
                    text="Удалить",
                    on_press=profile_del,
                )

                profile_box.add(profile_btn, profile_edit_btn, profile_del_btn)
                profiles_box.add(profile_box)

        self.body_box.add(profiles_box)

        self.footer_box.clear()
        create_profile_btn_box = Box(style=Pack(direction=COLUMN, flex=0))
        create_profile_btn = Button(
            id="create_profile_btn",
            text="Создать профиль",
            on_press=self.show_create_profile_view,
        )
        create_profile_btn_box.add(create_profile_btn)
        self.footer_box.add(create_profile_btn_box)

    def show_create_profile_view(self, widget):
        if widget is not None and widget.id == "create_profile_btn":
            self.settings_campaigns_for_add.clear()
            self.campaigns_box.clear()

        self.header_box.clear()
        header_label = Label(text="Создание нового профиля")
        self.header_box.add(header_label)

        self.body_box.clear()
        name_profile_box = Box(style=Pack(direction=ROW, flex=0))
        name_profile_label = Label(style=Pack(flex=0), text="Имя профиля")
        profile_name_txt_input = TextInput(style=Pack(flex=1))
        name_profile_box.add(name_profile_label, profile_name_txt_input)
        self.body_box.add(name_profile_box, self.campaigns_box)

        self.footer_box.clear()
        choose_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        choose_campaign_btn = Button(
            style=Pack(flex=1),
            text="Выбрать кампанию",
            on_press=self.show_choice_campaign_view,
        )

        choose_campaign_btn_box.add(choose_campaign_btn)

        create_profile_box = Box(style=Pack(direction=ROW, flex=0))

        return_btn = Button(
            text="Назад", style=Pack(flex=1), on_press=self.show_profiles_view
        )

        def create_profile(widget):
            profile_name = profile_name_txt_input.value
            if self.settings_campaigns_for_add:
                campaigns: list[CampaignModels] = self.settings_campaigns_for_add
                
                profile_for_add_raw: dict[str, str | list[object] = {
                    "profile_name": profile_name,
                    "campaigns": campaigns,
                }
                try:
                    profile = ProfileModel(**profile_for_add_raw)
                    settings_upload = Settings.load_settings()
                    settings_upload.append(settings_for_add)
                    Settings.save_settings(settings_upload)

                    self.settings_campaigns_for_add.clear()
                    self.show_profiles_view(widget)
                
                except ValidationError as e:
                    print("Bad profile in settings.json:", e)

        create_profile_btn = Button(
            style=Pack(flex=1),
            text="Создать",
            on_press=create_profile,
        )

        create_profile_box.add(return_btn, create_profile_btn)
        self.footer_box.add(choose_campaign_btn_box, create_profile_box)

    def show_choice_campaign_view(self, widget):
        self.header_box.clear()
        header_label = Label(text="Выбор кампании")
        self.header_box.add(header_label)

        self.body_box.clear()
        campaigns_box = Box(style=Pack(direction=ROW, flex=1))

        def select_campaign(widget, key):
            self.current_campaign = self.campaign_registry.get(key)
            self.show_campaigns_settings_view(widget=widget)

        for campaign_key, campaign_obj in self.campaign_registry.items():
            campaign_btn = Button(
                style=Pack(flex=0),
                text=campaign_obj.title,
                on_press=lambda widget: select_campaign(widget, campaign_key),
            )
            campaigns_box.add(campaign_btn)

        self.body_box.add(campaigns_box)

        self.footer_box.clear()
        return_btn_box = Box(style=Pack(direction=ROW, flex=0))
        return_btn = Button(
            style=Pack(flex=1),
            text="Назад",
            on_press=self.show_create_profile_view,
        )
        return_btn_box.add(return_btn)
        self.footer_box.add(return_btn_box)

    def show_campaigns_settings_view(self, widget):
        self.header_box.clear()
        head_label = Label(text="Данные кампании")
        self.header_box.add(head_label)

        self.body_box.clear()

        if self.current_campaign.region_required:
            region_box = Box(style=Pack(direction=COLUMN, flex=0))
            regions = self.current_campaign.get_active_regions()
            region_selection = Selection(items=regions, accessor="name")
            region_box.add(region_selection)
            self.body_box.add(region_box)
            region_box.add(region_selection)
        else:
            region_box = None

        personal_account_box = Box(style=Pack(direction=ROW, flex=1))
        personal_account_label = Label(text="Лицевой счет:", style=Pack(flex=0))
        personal_account_txt_input = TextInput(style=Pack(flex=1))
        personal_account_box.add(personal_account_label, personal_account_txt_input)
        self.body_box.add(region_box, personal_account_box)

        self.footer_box.clear()
        add_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        def on_add_campaign(widget):
            region_name = None
            region_id = None

            if self.current_campaign.region_required:
                region_row = region_selection.value
                region_name = region_row.name
                region_id = region_row.id

            personal_account = personal_account_txt_input.value

            campaign = self.current_campaign.make_campaign_profile(
                region_id=region_id,
                region_name=region_name,
                personal_account=personal_account,
            )

            self.settings_campaigns_for_add.append(campaign.model_dump())

            campaign_box = Box(style=Pack(flex=0, direction=COLUMN))

            campaign_label = Label(
                text=f'Добавлена кампания "{campaign.title}"'
            )

            campaign_box.add(campaign_label)
            self.campaigns_box.add(campaign_box)

            self.show_create_profile_view(widget)

        add_campaign_btn = Button(
            style=Pack(flex=1),
            text="Добавить кампанию",
            on_press=on_add_campaign,
        )

        add_campaign_btn_box.add(add_campaign_btn)

        return_btn_box = Box(style=Pack(direction=ROW, flex=0))
        return_btn = Button(
            style=Pack(flex=1),
            text="Назад",
            on_press=self.show_choice_campaign_view,
        )
        return_btn_box.add(return_btn)

        self.footer_box.add(add_campaign_btn_box, return_btn_box)
