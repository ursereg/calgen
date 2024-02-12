"""Generate calendar structure based on configuration."""

# type: ignore
import calendar
import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from ..config.calendar import ConfigurationBase


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


def weekdays(configuration: ConfigurationBase) -> List[int]:
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
            for week in month:  # type: ignore
                for day in week:
                    if day.month > current_month or (
                        current_month == 12 and day.month == 1
                    ):
                        continue
                    current_list.append(weekday(day))
            if len(current_list) > len(longest_list):
                longest_list = current_list
    return longest_list


def generate(configuration: ConfigurationBase) -> CalTable:
    all_weekdays = weekdays(configuration)
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
    print()

    current_month = 0
    print(configuration.year)
    print("     ", end="")
    for item in all_weekdays:
        print(f"{calendar.day_abbr[item]:5}", end="")
    print()
    for row in cal.yeardatescalendar(year=configuration.year, width=1):
        for month in row:
            current_row = CalRow(type=CalRowType.dates)
            current_month = current_month + 1
            print(calendar.month_abbr[current_month], end="")
            current_row.fields.append(
                CalField(
                    type=CalFieldType.label, label=calendar.month_abbr[current_month]
                )
            )
            for week in month:  # type: ignore
                for day in week:
                    if day.month != current_month:
                        current_row.fields.append(
                            CalField(
                                type=CalFieldType.date,
                                date=day,
                                this_month=False,
                                weekday=weekday(day),
                            )
                        )
                        # print("     ", end="")
                        print(f"{day.day:5}", end="")
                        continue
                    current_row.fields.append(
                        CalField(
                            type=CalFieldType.date,
                            date=day,
                            this_month=True,
                            weekday=weekday(day),
                        )
                    )
                    print(f"{day.day:5}", end="")
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
                        )
                    )
                    print(f"{ii+1:5}", end="")
            elif len(all_weekdays) < len(current_row.fields):
                current_row.fields = current_row.fields[: len(all_weekdays) + 1]
            table.rows.append(current_row)
            print()
            for label in configuration.month_notes:
                row = CalRow(type=CalRowType.nothing)
                row.fields.append(CalField(type=CalFieldType.label, label=label))
                for _ in all_weekdays:
                    row.fields.append(CalField(type=CalFieldType.nothing, label=label))
                table.rows.append(row)
                print()
    return table
