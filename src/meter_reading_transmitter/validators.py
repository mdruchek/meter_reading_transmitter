class Validators:
    def not_empty_validator(text: str) -> str | None:
        if (text or "").strip():
            return None
        else:
            return "Имя профиля обязательно"