def test_generate():
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    generate(CalendarConfig(year=2020))
    generate(CalendarConfig(year=2021))
    generate(CalendarConfig(year=2022))
    generate(CalendarConfig(year=2023))
    generate(CalendarConfig(year=2024))
    generate(CalendarConfig(year=2025))


def test_longest_list() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import weekdays

    assert len(weekdays(CalendarConfig(year=2020))) == 37
    assert len(weekdays(CalendarConfig(year=2021))) == 37
    assert len(weekdays(CalendarConfig(year=2022))) == 37
    assert len(weekdays(CalendarConfig(year=2023))) == 37
    assert len(weekdays(CalendarConfig(year=2024))) == 37
    assert len(weekdays(CalendarConfig(year=2025))) == 36


def test_generate_is_silent(capsys) -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    generate(CalendarConfig(year=2026))

    captured = capsys.readouterr()
    assert captured.out == ""
