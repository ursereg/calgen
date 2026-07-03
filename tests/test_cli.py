from click.testing import CliRunner


def test_cli_writes_svg(tmp_path) -> None:
    from calgen.cli.calgen import main

    out = tmp_path / "cal"
    result = CliRunner().invoke(
        main, ["--year", "2026", "--output", str(out), "--format", "svg"]
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "cal.svg").exists()


def test_cli_writes_svg_and_pdf(tmp_path) -> None:
    from calgen.cli.calgen import main

    out = tmp_path / "cal"
    result = CliRunner().invoke(
        main,
        [
            "--year",
            "2026",
            "--output",
            str(out),
            "--format",
            "svg",
            "--format",
            "pdf",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "cal.svg").exists()
    assert (tmp_path / "cal.pdf").exists()


def test_cli_uses_config_file_with_flag_override(tmp_path) -> None:
    from calgen.cli.calgen import main

    cfg = tmp_path / "cal.yaml"
    cfg.write_text("year: 2020\n")
    out = tmp_path / "cal"

    result = CliRunner().invoke(
        main,
        ["--config", str(cfg), "--year", "2031", "--output", str(out)],
    )

    assert result.exit_code == 0, result.output
    # 2031's year label must appear in the SVG, proving the flag overrode the file.
    assert "2031" in (tmp_path / "cal.svg").read_text()


def test_cli_rejects_unknown_format(tmp_path) -> None:
    from calgen.cli.calgen import main

    result = CliRunner().invoke(
        main, ["--output", str(tmp_path / "cal"), "--format", "gif"]
    )

    assert result.exit_code != 0


def test_cli_reports_bad_config(tmp_path) -> None:
    from calgen.cli.calgen import main

    cfg = tmp_path / "bad.yaml"
    cfg.write_text("year: not-a-number\n")
    out = tmp_path / "cal"

    result = CliRunner().invoke(
        main, ["--config", str(cfg), "--output", str(out)]
    )

    assert result.exit_code != 0
    # Readable click error, not a raw traceback.
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "Invalid configuration" in result.output
