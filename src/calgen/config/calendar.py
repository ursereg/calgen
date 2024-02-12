import calendar
from typing import List

from pydantic import BaseModel


class CellStyle(BaseModel):
    fill_color: str = "none"
    stroke_color: str = "black"
    stroke_width: float = 1
    text_color: str = "black"
    text_size: str = "26px"
    fill_opacity: float = 0.5


class ConfigurationBase(BaseModel):
    year: int = 2024
    first_week_day: int = calendar.MONDAY
    month_notes: List[str] = ["JG", "MM", "GKo", ""]
    base_row_width: float = 100
    base_row_height: float = 50
    style_top_row: CellStyle = CellStyle()
    style_headers: CellStyle = CellStyle()
    style_not_this_month: CellStyle = CellStyle()
    style_nothing: CellStyle = CellStyle(stroke_color="#aaa")
    style_workday: CellStyle = CellStyle(fill_color="#555")
    style_saturday: CellStyle = CellStyle(fill_color="#333")
    style_sunday: CellStyle = CellStyle(fill_color="#111")
