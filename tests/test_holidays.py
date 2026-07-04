import datetime


def test_no_holidays_by_default() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import holiday_dates

    assert holiday_dates(CalendarConfig(year=2026)) == set()


def test_polish_holidays_marked() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026, holidays_country="PL")
    table = generate(config)

    holiday_days = {
        field.date
        for row in table.rows
        for field in row.fields
        if field.is_holiday and field.this_month
    }

    # Fixed and movable Polish public holidays for 2026.
    assert datetime.date(2026, 1, 1) in holiday_days  # New Year
    assert datetime.date(2026, 5, 3) in holiday_days  # Constitution Day
    assert datetime.date(2026, 4, 6) in holiday_days  # Easter Monday (movable)
    # A plain working day is not a holiday.
    assert datetime.date(2026, 6, 15) not in holiday_days


def test_extra_holidays_marked() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import holiday_dates

    custom = datetime.date(2026, 6, 15)
    dates = holiday_dates(CalendarConfig(year=2026, extra_holidays=[custom]))

    assert custom in dates


def test_holiday_cell_uses_holiday_style() -> None:
    import drawsvg as draw

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    config = CalendarConfig()
    field = CalField(
        type=CalFieldType.date,
        date=datetime.date(2026, 5, 1),
        weekday=4,  # a Friday — proves holiday styling wins over the workday style
        this_month=True,
        is_holiday=True,
    )
    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(field, config))

    assert f'fill="{config.style_holiday.fill_color}"' in d.as_svg()
