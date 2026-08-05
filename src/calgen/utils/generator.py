"""Generate calendar structure based on configuration."""

import calendar
import datetime
from enum import Enum
from typing import List, Optional, Set, Tuple

from pydantic import BaseModel

from ..config.calendar import CalendarConfig


class CalFieldType(str, Enum):
    label = ("label",)
    date = "date"
    nothing = "nothing"


class CalField(BaseModel):
    type: CalFieldType
    date: Optional[datetime.date] = None
    weekday: Optional[int] = None
    label: Optional[str] = None
    this_month: bool = True
    is_holiday: bool = False


class CalRowType(str, Enum):
    weekdays = ("weekdays",)
    dates = "dates"
    nothing = "nothing"


class CalRow(BaseModel):
    type: CalRowType
    fields: List[CalField] = []


class CalTable(BaseModel):
    rows: List[CalRow] = []


def weekday(day: datetime.date) -> int:
    return calendar.weekday(year=day.year, month=day.month, day=day.day)


def month_sequence(configuration: CalendarConfig) -> List[Tuple[int, int]]:
    """The ordered (year, month) pairs the calendar covers, rolling over years."""
    sequence = []
    year, month = configuration.year, configuration.start_month
    for _ in range(configuration.months):
        sequence.append((year, month))
        month += 1
        if month == 13:
            month = 1
            year += 1
    return sequence


def end_year(configuration: CalendarConfig) -> int:
    """The calendar year the span ends in (equals `year` for a plain Jan-Dec span)."""
    total_months = configuration.start_month - 1 + configuration.months - 1
    return configuration.year + total_months // 12


def _leading_days(year: int, month: int, first_week_day: int) -> int:
    """Days between `first_week_day` and day 1 of this month, in the same week."""
    first_weekday = weekday(datetime.date(year, month, 1))
    return (first_weekday - first_week_day) % 7


def _grid_start(year: int, month: int, first_week_day: int) -> datetime.date:
    """The first date shown for this month: the `first_week_day` on/before day 1."""
    first = datetime.date(year, month, 1)
    return first - datetime.timedelta(days=_leading_days(year, month, first_week_day))


def _columns_needed(year: int, month: int, first_week_day: int) -> int:
    """Leading days back to `first_week_day` plus the days in this month."""
    days_in_month = calendar.monthrange(year, month)[1]
    return _leading_days(year, month, first_week_day) + days_in_month


def _max_columns(configuration: CalendarConfig) -> int:
    return max(
        _columns_needed(year, month, configuration.first_week_day)
        for year, month in month_sequence(configuration)
    )


def weekdays(configuration: CalendarConfig) -> List[int]:
    """Weekday-number sequence for the header row, one widest month row wide."""
    columns = _max_columns(configuration)
    first = configuration.first_week_day
    return [(first + offset) % 7 for offset in range(columns)]


def holiday_dates(configuration: CalendarConfig) -> Set[datetime.date]:
    """Public-holiday dates for the span: the country set plus any extra dates."""
    dates: Set[datetime.date] = set(configuration.extra_holidays)
    if configuration.holidays_country:
        import holidays

        # Include a year of slack on each side so spillover days that cross
        # a span boundary (leading/trailing cells) are also recognised.
        years = list(range(configuration.year - 1, end_year(configuration) + 2))
        dates.update(
            holidays.country_holidays(configuration.holidays_country, years=years)
        )
    return dates


def _is_plain_span(configuration: CalendarConfig) -> bool:
    return configuration.start_month == 1 and configuration.months == 12


def _month_label(year: int, month: int, configuration: CalendarConfig) -> str:
    if _is_plain_span(configuration):
        return calendar.month_abbr[month]
    return f"{calendar.month_abbr[month]} {year % 100:02d}"


def _corner_label(configuration: CalendarConfig) -> str:
    if _is_plain_span(configuration):
        return str(configuration.year)
    return f"{configuration.year}/{end_year(configuration) % 100:02d}"


def generate(configuration: CalendarConfig) -> CalTable:
    holidays_set = holiday_dates(configuration)
    columns = _max_columns(configuration)
    table = CalTable()

    first_row = CalRow(type=CalRowType.weekdays)
    first_row.fields.append(
        CalField(type=CalFieldType.label, label=_corner_label(configuration))
    )
    for wd in weekdays(configuration):
        first_row.fields.append(
            CalField(type=CalFieldType.label, label=calendar.day_abbr[wd])
        )
    table.rows.append(first_row)

    for year, month in month_sequence(configuration):
        current_row = CalRow(type=CalRowType.dates)
        current_row.fields.append(
            CalField(
                type=CalFieldType.label, label=_month_label(year, month, configuration)
            )
        )
        grid_start = _grid_start(year, month, configuration.first_week_day)
        for offset in range(columns):
            day = grid_start + datetime.timedelta(days=offset)
            current_row.fields.append(
                CalField(
                    type=CalFieldType.date,
                    date=day,
                    this_month=(day.year == year and day.month == month),
                    weekday=weekday(day),
                    is_holiday=day in holidays_set,
                )
            )
        table.rows.append(current_row)

        # Note rows mirror the date row column-for-column so that the cells
        # under other-month days carry the same weekday and this_month flag,
        # letting the renderer hatch the whole other-month block.
        date_cells = current_row.fields[1:]
        for label in configuration.month_notes:
            note_row = CalRow(type=CalRowType.nothing)
            note_row.fields.append(CalField(type=CalFieldType.label, label=label))
            for date_cell in date_cells:
                note_row.fields.append(
                    CalField(
                        type=CalFieldType.nothing,
                        weekday=date_cell.weekday,
                        this_month=date_cell.this_month,
                    )
                )
            table.rows.append(note_row)
    return table
