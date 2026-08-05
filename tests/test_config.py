import pytest


def test_default_config() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()

    assert isinstance(config, CalendarConfig)
    assert config.year == 2026


def _gray(color: str) -> int:
    # All theme fills are #rrggbb grayscale; return the shared channel value.
    assert color.startswith("#") and len(color) == 7
    return int(color[1:3], 16)


def test_bw_theme_is_a_dark_ramp() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()

    # Every column type has a fill (no bare-white working days), and the ramp
    # gets darker with the "day off" level: working < Saturday < Sunday < holiday.
    working = _gray(config.style_workday.fill_color)
    saturday = _gray(config.style_saturday.fill_color)
    sunday = _gray(config.style_sunday.fill_color)
    holiday = _gray(config.style_holiday.fill_color)
    assert working > saturday > sunday > holiday

    assert config.style_workday.fill_opacity == 1.0
    assert config.style_sunday.font_weight == "bold"
    assert config.style_holiday.font_weight == "bold"
    assert config.style_headers.font_weight == "bold"
    assert config.style_not_this_month.text_color != "black"
    assert config.shade_other_months is True
    assert config.hatch_other_months is True


def test_configuration_base_is_gone() -> None:
    import calgen.config.calendar as mod

    assert not hasattr(mod, "ConfigurationBase")


def test_default_span_is_calendar_year() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()
    assert config.start_month == 1
    assert config.months == 12


def test_span_can_start_mid_year() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig(start_month=8, months=12)
    assert config.start_month == 8
    assert config.months == 12


def test_start_month_out_of_range_is_rejected() -> None:
    import pydantic

    from calgen.config.calendar import CalendarConfig

    with pytest.raises(pydantic.ValidationError):
        CalendarConfig(start_month=13)
    with pytest.raises(pydantic.ValidationError):
        CalendarConfig(start_month=0)


def test_months_must_be_positive() -> None:
    import pydantic

    from calgen.config.calendar import CalendarConfig

    with pytest.raises(pydantic.ValidationError):
        CalendarConfig(months=0)
