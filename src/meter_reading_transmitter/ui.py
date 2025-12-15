"""
An application for transmitting meter readings
"""
# -*- coding: utf-8 -*-
# ✅ УНИВЕРСАЛЬНЫЙ ФИКС Toga 0.5.3 CSS (dict ↔ str)
try:
    import toga_gtk.widgets.base as base


    def fixed_get_font_css(font):
        css = base.get_font_css(font)
        if isinstance(css, dict):
            return css  # apply_css ожидает dict
        elif isinstance(css, str) and css and not css.startswith(('*', '.', '#')):
            return {'font': css.lstrip(':')}  # str → dict
        return css


    def fixed_apply_css(self, name, css):
        if isinstance(css, str):
            css = {'font': css}  # str → dict
        self._style_provider.load_from_data(f"* {{ {' '.join(f'{k}: {v};' for k, v in css.items())} }}".encode())


    base.WidgetImpl.get_font_css = fixed_get_font_css
    base.WidgetImpl.apply_css = fixed_apply_css
    print("✅ Toga CSS full fix applied")
except Exception as e:
    print(f"CSS fix skipped: {e}")


import asyncio

from pydantic import ValidationError

import requests
import toga
from toga import Box, Button, Label, TextInput, Selection, ErrorDialog
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.validators import ContainsDigit, NotContains

from .models import ProfileModel, CampaignModel, SubscriberDataModel
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

    def show_profile_edit(self, widget):
        profile_btn_id = widget.id
        profile_name_for_edit = profile_btn_id[: profile_btn_id.rfind("_profile")]

        self.header_box.clear()
        header_lbl = Label(text=f'Редактированме профиля {profile_name_for_edit}')
        self.header_box.add(header_lbl)

        profiles = Settings.load_settings()
        
        if profiles:
            profile: ProfileModel = next(profile for profile in profiles if profile.profile_name == profile_name_for_edit)

        self.body_box.clear()
        profile_box = Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
            )
        )

        profile_name_box = Box(
            style=Pack(
                direction=ROW,
                flex=0
            )
        )

        profile_name_lbl = Label(text='Имя прошиля:')
        
        profile_name_txtinp = TextInput(
            style=Pack(
                flex=1
            ),
            value=profile.profile_name
        )

        profile_name_box.add(profile_name_lbl, profile_name_txtinp)

        profile_campaigns = profile.campaigns
        campaigns_box = Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
            )
        )

        for campaign_index, campaign in enumerate(profile_campaigns):
            campaign_box = Box(
                style=Pack(
                    direction=ROW,
                    flex=1
                )
            )

            def remove_campaign_from_profile(wigget, _campaign_index):
                profile_campaigns.pop(_campaign_index)
                campaign_box.insert(0, Label(style=Pack(color='#8B0000'), text='Удалён'))

            campaign_name = campaign.title
            personal_account = campaign.personal_account
            campaign_lbl = Label(text=f'Кампания {campaign_name}. Лицевой счет {personal_account}')

            campaign_delete_btn = Button(
                text='Удалить',
                on_press=lambda widget, _campaign_index=campaign_index:  remove_campaign_from_profile(widget, _campaign_index)
            )

            campaign_box.add(campaign_lbl, campaign_delete_btn)
            campaigns_box.add(campaign_box)

        profile_box.add(profile_name_box, campaigns_box)
        self.body_box.add(profile_box)

        self.footer_box.clear()
        
        save_btn_dox = Box(
            style=Pack(
                direction=ROW,
                flex=0
            )
        )

        return_btn = Button(
            style=Pack(
                flex=1
            ),
            text='отмена',
            on_press=self.show_profiles_view
        )

        def saved_profile(widget):
            profile_index = profiles.index(profile)
            profiles.pop(profile_index)

            profile_edited = ProfileModel(
                profile_name=profile_name_txtinp.value,
                campaigns=profile_campaigns
            )

            profiles.insert(profile_index, profile_edited)
            Settings.save_settings(profiles)
            self.show_profiles_view(widget)


        save_btn = Button(
            style=Pack(
                flex=1
            ),
            text='Сохранить',
            on_press=saved_profile
        )

        save_btn_dox.add(return_btn, save_btn)
        self.footer_box.add(save_btn_dox)

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
                    on_press=self.show_profile_edit,
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

    async def show_form_sending_data(self, widget):
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

        async def fetch_subscriber_data(campaign, current_campaign):
            loop = asyncio.get_running_loop()
            try:
                # если get_subscriber_data блокирующий, уводим в executor
                subscriber_data_model = await loop.run_in_executor(
                    None,
                    current_campaign.get_subscriber_data,
                    campaign,
                )
                return subscriber_data_model
            except requests.exceptions.Timeout as e:
                return e
            except requests.exceptions.ConnectionError as e:
                return e
            except requests.exceptions.HTTPError as e:
                return e

        tasks = []
        for campaign in campaigns:
            current_campaign = self.campaign_registry.get(campaign.key)
            tasks.append(fetch_subscriber_data(campaign, current_campaign))

        results = await asyncio.gather(*tasks, return_exceptions=False)

        for campaign, result in zip(campaigns, results):
            campaign_box = Box(style=Pack(flex=0, direction=COLUMN))
            campaign_lbl_box = Box(style=Pack(direction=ROW))
            campaign_lbl = Label(text=campaign.title)
            campaign_lbl_box.add(campaign_lbl)

            subscriber_data_box = Box(style=Pack(flex=0, direction=ROW))

            if isinstance(result, Exception):
                # показываем причину ошибки для конкретной кампании
                if isinstance(result, requests.exceptions.Timeout):
                    msg = 'Сервер не отвечает. Попробуйте позже.'
                elif isinstance(result, requests.exceptions.ConnectionError):
                    msg = 'Ошибка сети. Проверьте подключение.'
                elif isinstance(result, requests.exceptions.HTTPError):
                    msg = 'Ошибка на стороне сервера.'
                else:
                    msg = f'Неизвестная ошибка: {type(result).__name__}'
                error_lbl = Label(text=msg)
                subscriber_data_box.add(error_lbl)
            else:
                subscriber_data_model = result
                subscriber_address = (
                    f'Адрес: {subscriber_data_model.address} '
                    f'Лицевой счёт: {subscriber_data_model.personal_account}'
                )

                subscriber_data_lbl = Label(text=subscriber_address)
                subscriber_data_box.add(subscriber_data_lbl)

                counters_data_box = Box(style=Pack(direction=COLUMN, flex=1))
                for counter in subscriber_data_model.counters:
                    counter_data_box = Box(style=Pack(direction=ROW, flex=1))
                    sending_counter_data_box = Box(style=Pack(direction=ROW, flex=1))

                    sending_data_lbl = Label(text='Показания:')
                    sending_data_txtinp = TextInput(style=Pack(flex=1))

                    counter_number_lbl = Label(text=f'Номер счетчика: {counter.number}')
                    counter_value_last_lbl = Label(text=f'Последние показания: {counter.value_last}')
                    counter_checking_date_lbl = Label(text=f'Дата поверки: {counter.checking_data}')

                    sending_counter_data_box.add(sending_data_lbl, sending_data_txtinp)
                    counter_data_box.add(
                        sending_counter_data_box,
                        counter_number_lbl,
                        counter_value_last_lbl,
                        counter_checking_date_lbl,
                    )
                    counters_data_box.add(counter_data_box)

            campaign_box.add(campaign_lbl_box, subscriber_data_box)
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

            self.settings_campaigns_for_add.append(campaign_obj_or_err)

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
