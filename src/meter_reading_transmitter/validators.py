from toga.validators import Validator

class NotEmptyValidator(Validator):
    def validate(self, value: str) -> str | None:
        text = (value or "").strip()
        if text:
            self.widget.style.update(border_color=None)
            return None
        else:
            self.widget.style.update(border_color="#cc6666")
            self.widget.placeholder = "Обязательное поле"
            return "Обязательное поле"