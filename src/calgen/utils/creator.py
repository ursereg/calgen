"""Create actual calendar drawing based on what was generated."""

import drawsvg as draw

from calgen.config.calendar import CalendarConfig, CellStyle
from calgen.utils import generator


def render(configuration: CalendarConfig) -> draw.Drawing:
    table = generator.generate(configuration)
    columns = max(len(row.fields) for row in table.rows)
    width = columns * configuration.base_row_width
    height = len(table.rows) * configuration.base_row_height
    drawing = draw.Drawing(width, height)
    drawing.append(draw_table(table, configuration))
    return drawing


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
    style = CellStyle()
    data = None
    if field.type == generator.CalFieldType.date and field.date is not None:
        if not field.this_month:
            style = configuration.style_not_this_month
        elif field.weekday == 6:
            style = configuration.style_sunday
        elif field.weekday == 5:
            style = configuration.style_saturday
        else:
            style = configuration.style_workday
        data = str(field.date.day)
    elif field.type == generator.CalFieldType.label and field.label is not None:
        data = field.label
        style = configuration.style_headers
    else:
        style = configuration.style_nothing

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
