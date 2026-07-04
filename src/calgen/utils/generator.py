"""Generate calendar structure based on configuration."""

import calendar
import datetime
from enum import Enum
from typing import List, Optional, Set

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


def holiday_dates(configuration: CalendarConfig) -> Set[datetime.date]:
    """Public-holiday dates for the year: the country set plus any extra dates."""
    dates: Set[datetime.date] = set(configuration.extra_holidays)
    if configuration.holidays_country:
        import holidays

        # Include adjacent years so spillover days that cross the year boundary
        # (late December / early January cells) are also recognised.
        years = [configuration.year - 1, configuration.year, configuration.year + 1]
        dates.update(
            holidays.country_holidays(configuration.holidays_country, years=years)
        )
    return dates


def weekdays(configuration: CalendarConfig) -> List[int]:
    """
    Get list of weekdays for whole year if months are arranged one below
    each other.

    """
    cal = calendar.Calendar(firstweekday=configuration.first_week_day)
    longest_list: List[int] = []
    current_month = 0
    for row in cal.yeardatescalendar(year=configuration.year, width=1):
        for month in row:
            current_month += 1
            current_list = []
            for week in month:
                for day in week:
                    if day.month > current_month or (
                        current_month == 12 and day.month == 1
                    ):
                        continue
                    current_list.append(weekday(day))
            if len(current_list) > len(longest_list):
                longest_list = current_list
    return longest_list


def generate(configuration: CalendarConfig) -> CalTable:
    all_weekdays = weekdays(configuration)
    holidays_set = holiday_dates(configuration)
    table = CalTable()
    first_row = CalRow(type=CalRowType.weekdays)
    first_row.fields.append(
        CalField(type=CalFieldType.label, label=str(configuration.year))
    )
    for item in all_weekdays:
        first_row.fields.append(
            CalField(type=CalFieldType.label, label=calendar.day_abbr[item])
        )
    table.rows.append(first_row)

    cal = calendar.Calendar(firstweekday=configuration.first_week_day)

    current_month = 0
    for row in cal.yeardatescalendar(year=configuration.year, width=1):
        for month in row:
            current_row = CalRow(type=CalRowType.dates)
            current_month = current_month + 1
            current_row.fields.append(
                CalField(
                    type=CalFieldType.label, label=calendar.month_abbr[current_month]
                )
            )
            for week in month:
                for day in week:
                    if day.month != current_month:
                        current_row.fields.append(
                            CalField(
                                type=CalFieldType.date,
                                date=day,
                                this_month=False,
                                weekday=weekday(day),
                                is_holiday=day in holidays_set,
                            )
                        )
                        continue
                    current_row.fields.append(
                        CalField(
                            type=CalFieldType.date,
                            date=day,
                            this_month=True,
                            weekday=weekday(day),
                            is_holiday=day in holidays_set,
                        )
                    )
            if len(all_weekdays) > len(current_row.fields):
                # Need to add some fields,
                for ii in range(len(all_weekdays) - len(current_row.fields) + 1):
                    day = datetime.date(
                        year=configuration.year, month=current_month, day=ii + 1
                    )
                    current_row.fields.append(
                        CalField(
                            type=CalFieldType.date,
                            date=day,
                            this_month=False,
                            weekday=weekday(day),
                            is_holiday=day in holidays_set,
                        )
                    )
            elif len(all_weekdays) < len(current_row.fields):
                current_row.fields = current_row.fields[: len(all_weekdays) + 1]
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
