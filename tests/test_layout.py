import pytest


def test_paginate_svg_sets_landscape_a4_page() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    svg = paginate_svg(render(CalendarConfig(year=2026)), "A4", 10.0, landscape=True)

    # A4 landscape is 297mm wide by 210mm tall, declared on the root <svg>.
    assert 'width="297mm"' in svg
    assert 'height="210mm"' in svg


def test_paginate_svg_preserves_defs() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    # The hatch pattern lives in <defs>; pagination must keep it or the paged
    # PDF would lose the other-month hatch.
    svg = paginate_svg(render(CalendarConfig(year=2026)), "A4", 10.0, landscape=True)

    assert "<pattern" in svg
    assert "url(#calgen-other-month-hatch)" in svg


def test_paginate_svg_portrait_swaps_dimensions() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    svg = paginate_svg(render(CalendarConfig(year=2026)), "A4", 10.0, landscape=False)

    assert 'width="210mm"' in svg
    assert 'height="297mm"' in svg


def test_paginate_svg_rejects_unknown_paper() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    with pytest.raises(ValueError):
        paginate_svg(render(CalendarConfig(year=2026)), "B7", 10.0, landscape=True)


def test_paginate_svg_sets_a0_portrait_page() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    svg = paginate_svg(render(CalendarConfig(year=2026)), "A0", 15.0, landscape=False)

    assert 'width="841mm"' in svg
    assert 'height="1189mm"' in svg


def test_paginate_svg_sets_a1_portrait_page() -> None:
    from calgen.config.calendar import CalendarConfig
    from calgen.utils.creator import paginate_svg, render

    svg = paginate_svg(render(CalendarConfig(year=2026)), "A1", 15.0, landscape=False)

    assert 'width="594mm"' in svg
    assert 'height="841mm"' in svg


def test_cli_paper_produces_a3_pdf(tmp_path) -> None:
    from click.testing import CliRunner

    from calgen.cli.calgen import main

    out = tmp_path / "cal"
    result = CliRunner().invoke(
        main,
        ["--year", "2026", "--paper", "A3", "--output", str(out), "--format", "pdf"],
    )

    assert result.exit_code == 0, result.output
    pdf = tmp_path / "cal.pdf"
    assert pdf.exists()

    from pypdf import PdfReader

    box = PdfReader(str(pdf)).pages[0].mediabox
    # A3 landscape: 420mm x 297mm.
    assert round(float(box.width) / 72 * 25.4) == 420
    assert round(float(box.height) / 72 * 25.4) == 297
