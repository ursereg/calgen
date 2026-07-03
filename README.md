# calgen

Generate printable **linear year calendars** as SVG or PDF. Each month is one
horizontal row with days aligned into weekday columns, plus optional blank
note rows under each month for annotations. The default theme is tuned for
black-and-white printers: light fills, thin gridlines, and weekends marked so
Saturday and Sunday stay distinct in monochrome.

## Install

```sh
pip install -e ".[dev]"
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

### Config file

Any setting can live in a YAML file; command-line flags override it. Config is
optional — omit `--config` to use built-in defaults.

```yaml
year: 2026
first_week_day: 0        # 0 = Monday ... 6 = Sunday
month_notes: ["Tasks", "Notes"]
style_saturday:
  fill_color: "#eee"
style_sunday:
  fill_color: "#ddd"
  font_weight: bold
```

```sh
calgen --config calendar.yaml --output calendar --format pdf
```

## Development

```sh
pip install -e ".[dev]"
pytest
```

## License

This is [MIT](LICENSE.md) licensed.
