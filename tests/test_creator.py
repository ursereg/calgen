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
