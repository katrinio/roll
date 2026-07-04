from roll.messages.cli import EN as CLI_EN
from roll.messages.cli import RU as CLI_RU
from roll.messages.doctor import RU as DOCTOR_RU
from roll.messages.normalize import RU as NORMALIZE_RU
from roll.messages.cli import detect_locale


RU = {**CLI_RU, **DOCTOR_RU, **NORMALIZE_RU}
EN = {**CLI_EN, **DOCTOR_RU, **NORMALIZE_RU}


def text(key: str, **kwargs) -> str:
    value = EN[key] if detect_locale() == "en" else RU[key]
    return value.format(**kwargs) if kwargs else value
