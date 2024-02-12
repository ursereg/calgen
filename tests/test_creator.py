def test_draw_svg() -> None:
    import drawsvg as draw

    d = draw.Drawing(1000, 1000)
    d.save_svg("test.svg")


def test_draw_field() -> None:
    import drawsvg as draw

    from calgen.config.calendar import ConfigurationBase
    from calgen.utils.creator import draw_field
    from calgen.utils.generator import CalField, CalFieldType

    d = draw.Drawing(1000, 1000)
    d.append(draw_field(CalField(type=CalFieldType.nothing), ConfigurationBase()))

    d.save_svg("field.svg")


def test_draw_row() -> None:
    import drawsvg as draw

    from calgen.config.calendar import ConfigurationBase
    from calgen.utils.creator import draw_row
    from calgen.utils.generator import CalField, CalFieldType, CalRow, CalRowType

    d = draw.Drawing(1000, 1000)
    row = CalRow(
        type=CalRowType.nothing,
        fields=[
            CalField(type=CalFieldType.nothing),
            CalField(type=CalFieldType.date),
            CalField(type=CalFieldType.label),
        ],
    )

    d.append(draw_row(row, ConfigurationBase()))

    d.save_svg("row.svg")


def test_draw_table() -> None:
    import drawsvg as draw

    from calgen.config.calendar import ConfigurationBase
    from calgen.utils.creator import draw_table
    from calgen.utils.generator import generate

    d = draw.Drawing(1000, 1000)
    configuration = ConfigurationBase(year=2024)
    d.append(
        draw_table(generate(configuration=configuration), configuration=configuration)
    )
    d.save_svg("table.svg")
