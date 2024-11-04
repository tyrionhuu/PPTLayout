from pptx.util import Length


def unit_conversion(value: Length | None, unit: str) -> int | float:
    if value is None:
        raise ValueError("Value cannot be None")

    if unit == "cm":
        return value.cm
    elif unit == "inches" or unit == "in" or unit == "inch":
        return value.inches
    elif unit == "pt":
        return value.pt
    elif unit == "emu":
        return value.emu
    else:
        raise ValueError(f"Invalid measurement unit: {unit}")
