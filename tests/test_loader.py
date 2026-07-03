import pytest


def test_load_config_reads_yaml(tmp_path) -> None:
    from calgen.config.loader import load_config

    cfg_file = tmp_path / "cal.yaml"
    cfg_file.write_text(
        "year: 2030\n"
        "month_notes: [work, home]\n"
        "style_saturday:\n"
        "  fill_color: '#ccc'\n"
    )

    config = load_config(cfg_file)

    assert config.year == 2030
    assert config.month_notes == ["work", "home"]
    assert config.style_saturday.fill_color == "#ccc"
    # Untouched fields keep their defaults.
    assert config.style_sunday.font_weight == "bold"


def test_load_config_missing_file(tmp_path) -> None:
    from calgen.config.loader import load_config

    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nope.yaml")


def test_load_config_invalid_schema(tmp_path) -> None:
    from calgen.config.loader import load_config

    cfg_file = tmp_path / "bad.yaml"
    cfg_file.write_text("year: not-a-number\n")

    with pytest.raises(ValueError):
        load_config(cfg_file)
