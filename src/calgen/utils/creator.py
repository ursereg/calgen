"""Create actual calendar based on what was generated."""

import drawsvg as draw

from calgen.config.calendar import CellStyle, ConfigurationBase
from calgen.utils import generator


def draw_table(
    table: generator.CalTable,
    configuration: ConfigurationBase,
) -> draw.DrawingParentElement:
    group = draw.Group()
    for index, item in enumerate(table.rows):
        # print(index, item)
        offset = index * configuration.base_row_height
        sub_group = draw.Group(transform=f"translate(0,{offset})")
        sub_group.append(draw_row(item, configuration))
        group.append(sub_group)
    return group


def draw_row(
    row: generator.CalRow, configuration: ConfigurationBase
) -> draw.DrawingParentElement:
    group = draw.Group()
    for index, item in enumerate(row.fields):
        # print(index, item)
        offset = index * configuration.base_row_width
        sub_group = draw.Group(transform=f"translate({offset})")
        sub_group.append(draw_field(item, configuration))
        group.append(sub_group)
    return group


def draw_field(
    field: generator.CalField, configuration: ConfigurationBase
) -> draw.DrawingParentElement:
    group = draw.Group()
    style = CellStyle()
    # print(field.date)
    if field.type == generator.CalFieldType.date and field.date is not None:
        if not field.this_month:
            style = configuration.style_not_this_month
        else:
            if field.weekday == 6:
                # From zero, this is sunday
                style = configuration.style_sunday
            elif field.weekday == 5:
                # From zero, this is saturday
                style = configuration.style_saturday
            else:
                style = configuration.style_workday
        data = str(field.date.day)
    elif field.type == generator.CalFieldType.label and field.label is not None:
        data = field.label
        style = configuration.style_headers
    else:
        data = None
        style = configuration.style_nothing
    print(style)
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
    if data is not None:
        text = draw.Text(
            data,
            style.text_size,
            configuration.base_row_width / 2,
            configuration.base_row_height / 2,
            center=True,
            text_color=style.text_color,
        )
        group.append(text)
    # if field.type == generator.CalFieldType.date:
    # box.append_title("test")
    group.append(box)

    return group
