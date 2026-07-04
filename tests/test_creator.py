def test_render_canvas_is_sized_to_content() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import render
    from calgen.utils.generator import generate

    config = CalendarConfig(year=2026)
    table = generate(config)

    drawing = render(config)

    expected_cols = max(len(row.fields) for row in table.rows)
    assert drawing.width == expected_cols * config.base_row_width
    assert drawing.height == len(table.rows) * config.base_row_height


def test_render_is_silent(capsys) -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import render

    render(CalendarConfig(year=2026))

    assert capsys.readouterr().out == ""


def test_render_saves_svg(tmp_path) -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import render

    out = tmp_path / "cal.svg"
    render(CalendarConfig(year=2026)).save_svg(str(out))

    assert out.exists() and out.stat().st_size > 0


def test_sunday_number_is_bold_and_colored() -> None:
    import datetime

    import drawsvg as draw

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    config = CalendarConfig()
    # 2026-01-04 is a Sunday (weekday 6).
    field = CalField(
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 4),
        weekday=6,
        this_month=True,
    )
    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(field, config))
    svg = d.as_svg()

    assert 'font-weight="bold"' in svg
    assert 'fill="black"' in svg  # text uses fill, not the ignored text_color attr


def test_cell_fill_does_not_hide_text() -> None:
    import datetime

    import drawsvg as draw

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    config = CalendarConfig()
    # Sunday has an opaque fill (#ddd); its number must still be visible.
    field = CalField(
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 4),
        weekday=6,
        this_month=True,
    )
    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(field, config))
    svg = d.as_svg()

    # The filled <rect> must be painted before the <text>, otherwise an opaque
    # cell fill would cover the number. SVG paints in document order.
    assert svg.index("<rect") < svg.index("<text"), "cell fill must not cover text"


def test_empty_note_cells_get_weekend_fill() -> None:
    import drawsvg as draw

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    config = CalendarConfig()
    # An empty note-row cell in the Sunday column must show the Sunday fill,
    # so weekends read as "day off" through the whole column, not just the dates.
    field = CalField(type=CalFieldType.nothing, weekday=6)
    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(field, config))

    assert f'fill="{config.style_sunday.fill_color}"' in d.as_svg()


def _spillover_sunday_svg(shade_other_months: bool) -> str:
    import datetime

    import drawsvg as draw

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    config = CalendarConfig(shade_other_months=shade_other_months)
    # A Sunday belonging to an adjacent month (spillover cell).
    field = CalField(
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 4),
        weekday=6,
        this_month=False,
    )
    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(field, config))
    return d.as_svg()


def test_spillover_cell_keeps_column_fill_when_enabled() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()
    svg = _spillover_sunday_svg(shade_other_months=True)
    # Column fill preserved (no hole in the band), but the number is dimmed.
    assert f'fill="{config.style_sunday.fill_color}"' in svg
    assert f'fill="{config.style_not_this_month.text_color}"' in svg


def test_spillover_cell_unshaded_when_disabled() -> None:
    from calgen.config.calendar import CalendarConfig

    config = CalendarConfig()
    svg = _spillover_sunday_svg(shade_other_months=False)
    # No weekend fill; falls back to the flat not-this-month style.
    assert f'fill="{config.style_sunday.fill_color}"' not in svg


HATCH_REF = "url(#calgen-other-month-hatch)"


def _cell_svg(config, **field_kwargs) -> str:
    import drawsvg as draw

    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField

    d = draw.Drawing(config.base_row_width, config.base_row_height)
    d.append(draw_field(CalField(**field_kwargs), config))
    return d.as_svg()


def test_other_month_cell_is_hatched() -> None:
    import datetime

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import CalFieldType

    svg = _cell_svg(
        CalendarConfig(),
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 31),
        weekday=2,
        this_month=False,
    )
    assert HATCH_REF in svg


def test_other_month_note_cell_is_hatched() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import CalFieldType

    # A note-row (nothing) cell sitting under an other-month day: the hatch must
    # continue down the writing rows so it is clearly not for this month.
    svg = _cell_svg(
        CalendarConfig(),
        type=CalFieldType.nothing,
        weekday=2,
        this_month=False,
    )
    assert HATCH_REF in svg


def test_this_month_note_cell_is_not_hatched() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import CalFieldType

    svg = _cell_svg(
        CalendarConfig(),
        type=CalFieldType.nothing,
        weekday=2,
        this_month=True,
    )
    assert HATCH_REF not in svg


def test_this_month_cell_is_not_hatched() -> None:
    import datetime

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import CalFieldType

    svg = _cell_svg(
        CalendarConfig(),
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 15),
        weekday=3,
        this_month=True,
    )
    assert HATCH_REF not in svg


def test_hatch_can_be_disabled() -> None:
    import datetime

    from calgen.config.calendar import CalendarConfig
    from calgen.utils.generator import CalFieldType

    svg = _cell_svg(
        CalendarConfig(hatch_other_months=False),
        type=CalFieldType.date,
        date=datetime.date(2026, 1, 31),
        weekday=2,
        this_month=False,
    )
    assert HATCH_REF not in svg
