def test_default_config() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()

    assert isinstance(config, CalendarConfig)
    assert config.year == 2026


def test_bw_theme_defaults() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()

    assert config.style_workday.fill_color == "none"
    assert config.style_workday.fill_opacity == 1.0
    assert config.style_saturday.fill_color == "#eee"
    assert config.style_sunday.fill_color == "#ddd"
    assert config.style_sunday.font_weight == "bold"
    assert config.style_headers.font_weight == "bold"
    assert config.style_not_this_month.text_color == "#bbb"


def test_configuration_base_is_gone() -> None:
    import calgen.config.calendar as mod

    assert not hasattr(mod, "ConfigurationBase")
