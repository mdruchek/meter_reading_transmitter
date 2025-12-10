"""
An application for transmitting meter readings
"""

import os
from pydantic import ValidationError

import toga
from toga import Box, Button, Label, TextInput, Selection
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.validators import ContainsDigit, NotContains

from .models import ProfileModel, CampaignModel
from .campaigns import CAMPAIGN_REGISTRY, CampaignInterface, KVCCampaign
from .config import PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS, PERSONAL_ACCOUNT_TXT_INPUT_BACKGROUND_COLOR
from .settings_storage import Settings


class MeterReadingTransmitter(toga.App):
    def __init__(self, **kwargs):
        super().__init__(formal_name="Передача показаний счетчиков", **kwargs)

        self.campaign_registry = CAMPAIGN_REGISTRY
        self.current_campaign = None
        self.settings_campaigns_for_add: list[CampaignModel] = []


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
                    id=f'{profile.profile_name}_profile',
                    style=Pack(flex=1),
                    text=profile.profile_name,
                    on_press=self.show_form_sending_data
                )

                profile_edit_btn = Button(
                    id=f'{profile.profile_name}_profile_edit',
                    text="Редактировать",
                )

                def profile_del(widget):
                    profile_btn_id = widget.id
                    profile_name_for_del = profile_btn_id[: profile_btn_id.rfind("_profile")]
                    Settings.delete_setting(key='profile_name', value=profile_name_for_del)
                    self.show_profiles_view(widget)

                profile_del_btn = Button(
                    id=f'{profile.profile_name}_profile_del',
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

    def show_form_sending_data(self, widget):
        self.header_box.clear()
        label_header = Label(text='Передача показаний')
        self.header_box.add(label_header)

        self.body_box.clear()
        campaigns_box = Box(
            style=Pack(
                flex=1,
                direction=COLUMN,
            )
        )
        profile_btn_id = widget.id
        profile_name_for_sending = profile_btn_id[: profile_btn_id.rfind("_profile")]
        profiles = Settings.load_settings()
        profile = next((p for p in profiles if p.profile_name == profile_name_for_sending), None)
        campaigns = profile.campaigns
        
        for campaign in campaigns:
            campaign_box = Box(
                style=Pack(
                    flex=0,
                    direction=COLUMN,
                )
            )
        
            campaign_lbl_box = Box(
                style=Pack(
                    direction=ROW
                )
            )

            campaign_lbl = Label(
                text = campaign.title
            )

            campaign_lbl_box.add(campaign_lbl)
            self.current_campaign = self.campaign_registry.get(campaign.key)
            abonent_data = self.current_campaign.get_abonent_data(campaign)
            campaign_box.add(campaign_lbl)
            campaigns_box.add(campaign_box)

        self.body_box.add(campaigns_box)

        self.footer_box.clear()
        sending_btn_box = Box(
            style=Pack(
                flex=0,
                direction=ROW,
            )
        )

        return_btn = Button(
            style=Pack(
                flex=1
            ),
            text='Назад',
            on_press=self.show_profiles_view
        )

        sending_btn = Button(
            style=Pack(
                flex=1
            ),
            text='Передать показания',
            on_press=...
        )

        sending_btn_box.add(return_btn, sending_btn)
        self.footer_box.add(sending_btn_box)
            
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

        profile_name_txt_input = TextInput(
            style=Pack(flex=1),
        )

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
                campaigns: list[CampaignModel] = self.settings_campaigns_for_add

                profile_for_add_raw: dict[str, str | list[object]] = {
                    "profile_name": profile_name,
                    "campaigns": campaigns,
                }
                try:
                    profile = ProfileModel(**profile_for_add_raw)
                    settings_upload = Settings.load_settings()
                    settings_upload.append(profile)
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
                on_press=lambda widget, key=campaign_key: select_campaign(widget, key),
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

        def _on_change(widget):
            del personal_account_txt_input.style.background_color
            if not widget.is_valid:
                personal_account_txt_input.style.background_color = PERSONAL_ACCOUNT_TXT_INPUT_BACKGROUND_COLOR

        personal_account_txt_input = TextInput(
            style=Pack(flex=1),
            validators=[
                ContainsDigit(count=PERSONAL_ACCOUNT_TXT_INPUT_NUMBER_DIGITS, allow_empty=False),
                NotContains(substring='-')
            ],
            on_change=_on_change
        )

        personal_account_box.add(personal_account_label, personal_account_txt_input)

        if region_box:
            self.body_box.add(region_box)

        self.body_box.add(personal_account_box)

        self.footer_box.clear()
        add_campaign_btn_box = Box(style=Pack(direction=COLUMN, flex=0))

        def on_add_campaign(widget):
            region_name = None
            region_id = None

            if self.current_campaign.region_required:
                region_row = region_selection.value
                region_name = region_row.name
                region_id = region_row.id

            personal_account = personal_account_txt_input.value.strip()

            campaign_obj_or_err = self.current_campaign.make_campaign_profile(
                _region_id=region_id,
                _region_name=region_name,
                _personal_account=personal_account,
            )

            if isinstance(campaign_obj_or_err, str):
                error_message = campaign_obj_or_err
                personal_account_txt_input.value = None
                personal_account_txt_input.placeholder = error_message
                personal_account_txt_input.style.background_color = PERSONAL_ACCOUNT_TXT_INPUT_BACKGROUND_COLOR
                return

            self.settings_campaigns_for_add.append(campaign_obj_or_err.model_dump())

            campaign_box = Box(style=Pack(flex=0, direction=COLUMN))

            campaign_label = Label(
                text=f'Добавлена кампания "{campaign_obj_or_err.title}"'
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
