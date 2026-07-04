import calendar
import datetime
from typing import List, Optional

from pydantic import BaseModel


class CellStyle(BaseModel):
    fill_color: str = "none"
    stroke_color: str = "#999"
    stroke_width: float = 1
    text_color: str = "black"
    text_size: str = "26px"
    fill_opacity: float = 1.0
    font_weight: str = "normal"


class CalendarConfig(BaseModel):
    year: int = 2026
    first_week_day: int = calendar.MONDAY
    month_notes: List[str] = ["", "", ""]
    base_row_width: float = 100
    base_row_height: float = 50
    # A light-to-dark grayscale ramp so day-off level reads at a glance and
    # prints cleanly in black and white: working < Saturday < Sunday < holiday.
    style_headers: CellStyle = CellStyle(fill_color="#f0f0f0", font_weight="bold")
    style_workday: CellStyle = CellStyle(fill_color="#f7f7f7")
    style_saturday: CellStyle = CellStyle(fill_color="#e6e6e6")
    style_sunday: CellStyle = CellStyle(fill_color="#d5d5d5", font_weight="bold")
    style_holiday: CellStyle = CellStyle(fill_color="#c4c4c4", font_weight="bold")
    # Applied to the *number* of days belonging to an adjacent month; the cell
    # keeps its column fill (unless shade_other_months is off).
    style_not_this_month: CellStyle = CellStyle(text_color="#999")

    # Fill other-month (spillover) cells to match their column so the vertical
    # bands stay continuous. Turn off to leave those cells blank instead.
    shade_other_months: bool = True
    # Overlay a diagonal hatch on other-month cells so it is obvious which cells
    # belong to this month (the ones to write in) and which do not.
    hatch_other_months: bool = True

    holidays_country: Optional[str] = None
    extra_holidays: List[datetime.date] = []

    # PDF page layout. paper=None sizes the page to the calendar itself; a paper
    # name (A4, A3, ...) makes a real page with the calendar scaled to fit inside
    # margin_mm and centred. Printers cannot print to the edge, so keep a margin.
    paper: Optional[str] = None
    margin_mm: float = 10.0
    landscape: bool = True
