def test_generate():
    from calgen.config.calendar import ConfigurationBase
    from calgen.utils.generator import generate

    generate(ConfigurationBase(year=2020))
    generate(ConfigurationBase(year=2021))
    generate(ConfigurationBase(year=2022))
    generate(ConfigurationBase(year=2023))
    generate(ConfigurationBase(year=2024))
    generate(ConfigurationBase(year=2025))


def test_longest_list() -> None:
    from calgen.config.calendar import ConfigurationBase
    from calgen.utils.generator import weekdays

    assert len(weekdays(ConfigurationBase(year=2020))) == 37
    assert len(weekdays(ConfigurationBase(year=2021))) == 37
    assert len(weekdays(ConfigurationBase(year=2022))) == 37
    assert len(weekdays(ConfigurationBase(year=2023))) == 37
    assert len(weekdays(ConfigurationBase(year=2024))) == 37
    assert len(weekdays(ConfigurationBase(year=2025))) == 36
