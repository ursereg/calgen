import calendar
from typing import List

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
    style_headers: CellStyle = CellStyle(fill_color="#f0f0f0", font_weight="bold")
    style_not_this_month: CellStyle = CellStyle(text_color="#bbb")
    style_nothing: CellStyle = CellStyle()
    style_workday: CellStyle = CellStyle()
    style_saturday: CellStyle = CellStyle(fill_color="#eee")
    style_sunday: CellStyle = CellStyle(fill_color="#ddd", font_weight="bold")
