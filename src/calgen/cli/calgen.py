"""Command line interface for generating printable calendars."""

from typing import Any, Optional, Tuple

import click
import drawsvg as draw

from calgen.config.calendar import CalendarConfig
from calgen.config.loader import load_config
from calgen.utils.creator import render


def save_calendar(
    drawing: draw.Drawing, base_path: str, formats: Tuple[str, ...]
) -> None:
    for fmt in formats:
        target = f"{base_path}.{fmt}"
        if fmt == "svg":
            drawing.save_svg(target)
        elif fmt == "pdf":
            try:
                import cairosvg
            except (ImportError, OSError) as error:
                raise click.ClickException(
                    "PDF export needs cairo. Install the drawsvg extras "
                    "(`pip install 'drawsvg[all]'`) and the system cairo library. "
                    f"Original error: {error}"
                )
            cairosvg.svg2pdf(bytestring=drawing.as_svg().encode(), write_to=target)


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Optional YAML config file. Flags below override its values.",
)
@click.option("--year", type=int, default=None, help="Calendar year.")
@click.option(
    "--first-weekday",
    type=int,
    default=None,
    help="First day of week (0=Monday .. 6=Sunday).",
)
@click.option(
    "--note",
    "notes",
    multiple=True,
    help="Note-row label under each month; repeat for multiple rows.",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False),
    default="calendar",
    help="Output base path; the format extension is appended.",
)
@click.option(
    "--format",
    "formats",
    type=click.Choice(["svg", "pdf"]),
    multiple=True,
    default=("svg",),
    help="Output format(s); repeatable.",
)
def main(
    config_path: Optional[str],
    year: Optional[int],
    first_weekday: Optional[int],
    notes: Tuple[str, ...],
    output: str,
    formats: Tuple[str, ...],
) -> None:
    """Generate a printable linear year calendar."""
    try:
        config = load_config(config_path) if config_path else CalendarConfig()
    except ValueError as error:
        raise click.ClickException(str(error))

    overrides: dict[str, Any] = {}
    if year is not None:
        overrides["year"] = year
    if first_weekday is not None:
        overrides["first_week_day"] = first_weekday
    if notes:
        overrides["month_notes"] = list(notes)
    if overrides:
        config = config.model_copy(update=overrides)

    drawing = render(config)
    save_calendar(drawing, output, formats)
    click.echo(f"Wrote {', '.join(f'{output}.{f}' for f in formats)}")
