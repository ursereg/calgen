def test_default_config() -> None:

    from calgen.config.calendar import ConfigurationBase

    base = ConfigurationBase()

    assert isinstance(base, ConfigurationBase)
    assert base.year == 2024
