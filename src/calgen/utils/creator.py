"""Create actual calendar drawing based on what was generated."""

import drawsvg as draw

from calgen.config.calendar import CalendarConfig, CellStyle
from calgen.utils import generator


def _hatch_pattern() -> draw.Pattern:
    """A diagonal hatch, shared across cells, marking days of an adjacent month."""
    pattern = draw.Pattern(
        6, 6, id="calgen-other-month-hatch", patternUnits="userSpaceOnUse"
    )
    pattern.append(draw.Line(0, 6, 6, 0, stroke="#9a9a9a", stroke_width=0.75))
    return pattern


HATCH = _hatch_pattern()


def column_style(field: generator.CalField, configuration: CalendarConfig) -> CellStyle:
    """The fill a cell gets from its column: holiday, weekend, or working day.

    Shared by date cells and empty note cells so each weekday column reads as one
    continuous vertical band.
    """
    if field.is_holiday:
        return configuration.style_holiday
    if field.weekday == 6:
        return configuration.style_sunday
    if field.weekday == 5:
        return configuration.style_saturday
    return configuration.style_workday


def render(configuration: CalendarConfig) -> draw.Drawing:
    table = generator.generate(configuration)
    columns = max(len(row.fields) for row in table.rows)
    width = columns * configuration.base_row_width
    height = len(table.rows) * configuration.base_row_height
    drawing = draw.Drawing(width, height)
    drawing.append(draw_table(table, configuration))
    return drawing


# Portrait paper sizes in millimetres.
PAPER_SIZES_MM = {
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),
    "letter": (216, 279),
    "legal": (216, 356),
}
MM_TO_PT = 72 / 25.4


def paginate_svg(
    drawing: draw.Drawing, paper: str, margin_mm: float, landscape: bool
) -> str:
    """Wrap a rendered drawing in a fixed paper page, scaled to fit the margin box.

    Returns an SVG string sized in millimetres so it prints at true paper size.
    """
    if paper not in PAPER_SIZES_MM:
        raise ValueError(
            f"Unknown paper size {paper!r}; choose from "
            f"{', '.join(sorted(PAPER_SIZES_MM))}."
        )
    page_mm = PAPER_SIZES_MM[paper]
    width_mm, height_mm = (page_mm[1], page_mm[0]) if landscape else page_mm
    width_pt, height_pt = width_mm * MM_TO_PT, height_mm * MM_TO_PT

    margin_pt = margin_mm * MM_TO_PT
    scale = min(
        (width_pt - 2 * margin_pt) / drawing.width,
        (height_pt - 2 * margin_pt) / drawing.height,
    )
    offset_x = (width_pt - drawing.width * scale) / 2
    offset_y = (height_pt - drawing.height * scale) / 2

    full = drawing.as_svg()
    head, body = full.split("</defs>", 1)
    defs = head.split("<defs>", 1)[1] if "<defs>" in head else ""
    body = body.rsplit("</svg>", 1)[0]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width_mm}mm" height="{height_mm}mm" '
        f'viewBox="0 0 {width_pt} {height_pt}">\n'
        f"<defs>{defs}</defs>\n"
        f'<g transform="translate({offset_x},{offset_y}) scale({scale})">'
        f"{body}</g>\n"
        "</svg>\n"
    )


def draw_table(
    table: generator.CalTable,
    configuration: CalendarConfig,
) -> draw.DrawingParentElement:
    group = draw.Group()
    for index, item in enumerate(table.rows):
        offset = index * configuration.base_row_height
        sub_group = draw.Group(transform=f"translate(0,{offset})")
        sub_group.append(draw_row(item, configuration))
        group.append(sub_group)
    return group


def draw_row(
    row: generator.CalRow, configuration: CalendarConfig
) -> draw.DrawingParentElement:
    group = draw.Group()
    for index, item in enumerate(row.fields):
        offset = index * configuration.base_row_width
        sub_group = draw.Group(transform=f"translate({offset})")
        sub_group.append(draw_field(item, configuration))
        group.append(sub_group)
    return group


def draw_field(
    field: generator.CalField, configuration: CalendarConfig
) -> draw.DrawingParentElement:
    group = draw.Group()
    is_label = field.type == generator.CalFieldType.label and field.label is not None
    # Labels always belong to the calendar; only dated/note cells can be an
    # other-month cell (leading/trailing days and the note cells beneath them).
    other_month = not is_label and not field.this_month

    data = None
    if is_label:
        style = configuration.style_headers
        data = field.label
    elif other_month and not configuration.shade_other_months:
        style = configuration.style_not_this_month
    else:
        style = column_style(field, configuration)
        if other_month:
            # Keep the column fill so the band stays continuous, but dim the
            # number to show the day belongs to an adjacent month.
            dim = configuration.style_not_this_month
            style = style.model_copy(
                update={"text_color": dim.text_color, "font_weight": dim.font_weight}
            )
    if field.type == generator.CalFieldType.date and field.date is not None:
        data = str(field.date.day)

    box = draw.Rectangle(
        style.stroke_width,
        style.stroke_width,
        configuration.base_row_width - style.stroke_width,
        configuration.base_row_height - style.stroke_width,
        stroke=style.stroke_color,
        stroke_width=style.stroke_width,
        fill=style.fill_color,
        fill_opacity=style.fill_opacity,
    )
    group.append(box)
    if other_month and configuration.hatch_other_months:
        group.append(
            draw.Rectangle(
                style.stroke_width,
                style.stroke_width,
                configuration.base_row_width - style.stroke_width,
                configuration.base_row_height - style.stroke_width,
                stroke="none",
                fill=HATCH,
            )
        )
    if data is not None:
        text = draw.Text(
            data,
            style.text_size,
            configuration.base_row_width / 2,
            configuration.base_row_height / 2,
            center=True,
            fill=style.text_color,
            font_weight=style.font_weight,
        )
        group.append(text)
    return group
