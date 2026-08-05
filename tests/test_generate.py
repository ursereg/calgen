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


def test_weekdays_length_matches_existing_years() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import weekdays

    # Unchanged from before the rewrite: verifies the new column-count logic
    # reproduces the exact same widths for plain Jan-Dec spans.
    assert len(weekdays(CalendarConfig(year=2020))) == 37
    assert len(weekdays(CalendarConfig(year=2025))) == 36


def test_generate_spans_a_year_boundary() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026, start_month=11, months=4)
    table = generate(config)

    # Header row + 4 month rows, each followed by config.month_notes rows.
    rows_per_month = 1 + len(config.month_notes)
    assert len(table.rows) == 1 + 4 * rows_per_month

    date_rows = [row for row in table.rows if row.type.value == "dates"]
    assert len(date_rows) == 4

    # Month order must be Nov 2026, Dec 2026, Jan 2027, Feb 2027 - verified by
    # the first this-month date cell's (year, month) in each row.
    expected = [(2026, 11), (2026, 12), (2027, 1), (2027, 2)]
    for row, (year, month) in zip(date_rows, expected):
        this_month_dates = [field.date for field in row.fields[1:] if field.this_month]
        assert this_month_dates, f"row for {year}-{month} has no this-month dates"
        assert all(d.year == year and d.month == month for d in this_month_dates)


def test_generate_has_no_fabricated_or_duplicate_dates() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    # February is the shortest month in this span - the old padding branch
    # used to fabricate low day numbers here. Every date cell in a row must
    # now be part of one unbroken consecutive run, so no duplicates.
    config = CalendarConfig(year=2026, start_month=11, months=4)
    table = generate(config)

    date_rows = [row for row in table.rows if row.type.value == "dates"]
    for row in date_rows:
        dates = [field.date for field in row.fields[1:]]
        assert len(dates) == len(set(dates)), "duplicate date in a single month row"
        for earlier, later in zip(dates, dates[1:]):
            assert (later - earlier).days == 1, "date cells must be consecutive"


def test_month_label_shows_year_for_custom_span() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026, start_month=8, months=12)
    table = generate(config)

    date_rows = [row for row in table.rows if row.type.value == "dates"]
    labels = [row.fields[0].label for row in date_rows]
    assert labels[0] == "Aug 26"
    assert labels[4] == "Dec 26"
    assert labels[5] == "Jan 27"
    assert labels[-1] == "Jul 27"


def test_month_label_is_plain_for_default_span() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026)
    table = generate(config)

    date_rows = [row for row in table.rows if row.type.value == "dates"]
    assert date_rows[0].fields[0].label == "Jan"
    assert date_rows[-1].fields[0].label == "Dec"


def test_corner_label_shows_span_for_custom_span() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026, start_month=8, months=12)
    table = generate(config)

    assert table.rows[0].fields[0].label == "2026/27"


def test_corner_label_is_plain_year_for_default_span() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026)
    table = generate(config)

    assert table.rows[0].fields[0].label == "2026"


def test_holiday_dates_cover_the_full_span_plus_spillover() -> None:
    import datetime

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import holiday_dates

    # Aug 2026 - Jul 2027: Polish holidays in both years must be present,
    # including a holiday that only exists in the trailing year (2027).
    config = CalendarConfig(year=2026, start_month=8, months=12, holidays_country="PL")
    dates = holiday_dates(config)
    assert datetime.date(2026, 12, 25) in dates  # Christmas Day 2026
    assert datetime.date(2027, 5, 1) in dates  # Labour Day 2027
