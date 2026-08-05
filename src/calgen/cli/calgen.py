"""Command line interface for generating printable calendars."""

from typing import Any, Optional, Tuple

import click
import drawsvg as draw

from calgen.config.calendar import CalendarConfig
from calgen.config.loader import load_config
from calgen.utils.creator import paginate_svg, render


def save_calendar(
    drawing: draw.Drawing,
    base_path: str,
    formats: Tuple[str, ...],
    configuration: CalendarConfig,
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
            if configuration.paper:
                svg = paginate_svg(
                    drawing,
                    configuration.paper,
                    configuration.margin_mm,
                    configuration.landscape,
                )
            else:
                svg = drawing.as_svg()
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=target)


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
    "--note-rows",
    type=int,
    default=None,
    help="Number of blank note rows per month (shorthand for repeating --note "
    "with empty labels). Cannot be combined with --note.",
)
@click.option(
    "--holidays-country",
    default=None,
    help="Mark public holidays for a country code, e.g. PL for Poland.",
)
@click.option(
    "--paper",
    default=None,
    help="PDF paper size (A0, A1, A5, A4, A3, A2, letter, legal). Omit to fit content.",
)
@click.option(
    "--margin",
    "margin_mm",
    type=float,
    default=None,
    help="PDF page margin in millimetres (default 10).",
)
@click.option(
    "--landscape/--portrait",
    "landscape",
    default=None,
    help="PDF orientation (default landscape).",
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
    note_rows: Optional[int],
    holidays_country: Optional[str],
    paper: Optional[str],
    margin_mm: Optional[float],
    landscape: Optional[bool],
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
    if notes and note_rows is not None:
        raise click.ClickException("Pass either --note and --note-rows, not both.")
    if notes:
        overrides["month_notes"] = list(notes)
    elif note_rows is not None:
        overrides["month_notes"] = [""] * note_rows
    if holidays_country is not None:
        overrides["holidays_country"] = holidays_country
    if paper is not None:
        overrides["paper"] = paper
    if margin_mm is not None:
        overrides["margin_mm"] = margin_mm
    if landscape is not None:
        overrides["landscape"] = landscape
    if overrides:
        config = config.model_copy(update=overrides)

    drawing = render(config)
    save_calendar(drawing, output, formats, config)
    click.echo(f"Wrote {', '.join(f'{output}.{f}' for f in formats)}")
