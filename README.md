# calgen

Generate printable **linear year calendars** as SVG or PDF. Each month is one
horizontal row with days aligned into weekday columns, plus optional blank
note rows under each month for annotations. The default theme is tuned for
black-and-white printers: light fills, thin gridlines, and weekends marked so
Saturday and Sunday stay distinct in monochrome.

## Install and run

The quickest way is [uv](https://docs.astral.sh/uv/) — it fetches, builds, and
runs in one step, no environment to manage.

Run it once without installing anything:

```sh
uvx --from git+https://github.com/ursereg/calgen.git calgen --year 2026 --format pdf
```

Install it as a persistent command (like pipx):

```sh
uv tool install git+https://github.com/ursereg/calgen.git
calgen --year 2026 --format pdf
```

From a local checkout, point `--from` at the current directory:

```sh
uvx --from . calgen --year 2026
```

Or install into an environment with plain pip:

```sh
pip install .
```

## Usage

Generate a calendar for the current defaults (SVG):

```sh
calgen --output calendar --format svg
```

A specific year, both SVG and PDF:

```sh
calgen --year 2026 --output calendar --format svg --format pdf
```

Note rows under each month:

```sh
calgen --note "Tasks" --note "Notes"
```

Mark public holidays for a country (uses the `holidays` library, which handles
movable feasts like Easter Monday). For example, Poland:

```sh
calgen --holidays-country PL
```

Every weekday column is shaded as a continuous band, getting darker with the
"day off" level: working day < Saturday < Sunday < holiday. Days from an
adjacent month keep their column shade but are dimmed and overlaid with a
diagonal hatch, so it is obvious which cells belong to this month (the ones to
write in). Set `shade_other_months` to `false` to leave those cells blank, or
`hatch_other_months` to `false` to drop the hatch.

### Printing (paper size and margins)

By default the PDF page is sized to the calendar itself. To print on standard
paper, pick a paper size — the calendar is scaled to fit inside a margin and
centred (printers cannot print to the very edge, so a margin is required):

```sh
calgen --holidays-country PL --paper A3 --margin 10 --format pdf
```

`--paper` accepts A0, A1, A5, A4, A3, A2, letter, legal. `--margin` is in millimetres
(default 10). Orientation defaults to landscape; use `--portrait` to flip it.
The linear layout is very wide, so A3 landscape is the most legible.

### Multi-year spans and note rows

By default the calendar covers January-December of `--year`. To start
somewhere else (e.g. a school year), set `start_month` and `months` in the
config file:

```yaml
year: 2026
start_month: 8   # August
months: 12       # runs through July 2027
```

Month and corner labels automatically include the year (`Aug 26`, `2026/27`)
whenever the span isn't a plain calendar year, so adjacent years aren't
ambiguous.

Note rows (blank rows under each month for annotations) are set via
`month_notes` in the config file, or `--note-rows N` on the command line for
N unlabelled rows (shorthand for N repeats of `--note ""`; cannot be combined
with `--note`).

`--paper` now also accepts `A0` and `A1` for wall-sized prints. A tall,
many-row calendar like a 12-month/8-rows-per-month span reads best as
`--portrait` at A0 or A1, since the linear layout becomes taller than it is
wide.

### Config file

Any setting can live in a YAML file; command-line flags override it. Config is
optional — omit `--config` to use built-in defaults.

Any setting can live in a YAML file; command-line flags override it. Config is
optional — omit `--config` to use built-in defaults.

```yaml
year: 2026
first_week_day: 0        # 0 = Monday ... 6 = Sunday
month_notes: ["Tasks", "Notes"]
holidays_country: PL     # mark a country's public holidays (omit to disable)
extra_holidays:          # your own extra days off, marked like holidays
  - 2026-06-15
shade_other_months: true # fill spillover cells to match their column
hatch_other_months: true # hatch spillover cells so they read as "not this month"
paper: A3                # PDF paper size (omit to size the page to the calendar)
margin_mm: 10            # PDF page margin
landscape: true          # PDF orientation
style_saturday:
  fill_color: "#e6e6e6"
style_sunday:
  fill_color: "#d5d5d5"
  font_weight: bold
style_holiday:
  fill_color: "#c4c4c4"
  font_weight: bold
```

```sh
calgen --config calendar.yaml --output calendar --format pdf
```

## Development

With uv (recommended) — `uv.lock` pins exact versions for a reproducible setup:

```sh
uv sync --extra dev
uv run pytest
uv run calgen --year 2026        # run the CLI from the source tree
```

Or with plain pip:

```sh
pip install -e ".[dev]"
pytest
```

## License

This is [MIT](LICENSE.md) licensed.
