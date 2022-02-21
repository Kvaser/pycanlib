import pytest
from canlib import kvlclib


@pytest.mark.parametrize("fmt", kvlclib.writer_formats())
def test_writer_property_default(fmt, tmp_path):
    print(f"Looking at {fmt}")
    cnv = kvlclib.Converter(tmp_path / "dummy_file", fmt)
    for p in kvlclib.Property:
        if fmt.isPropertySupported(p):
            print(f"\t {p.name}:", end="")
            default = fmt.getPropertyDefault(p)
            if default is None:
                print(f" {default} - Skipping.")
                continue
            print(f" {default}")
            assert cnv.getProperty(p) == default
            if default is None:
                continue
            if default in [0, 4, 5, 6, 8, 9, 64]:
                cnv.setProperty(p, 1)
                assert cnv.getProperty(p) == 1
            elif default in [-1, 1, 31]:
                cnv.setProperty(p, 0)
                assert cnv.getProperty(p) == 0
            elif default in [b',', b'.']:
                cnv.setProperty(p, b';')
                assert cnv.getProperty(p) == b';'
            else:
                assert 0, f"Unknown property default value: {default}"


@pytest.mark.parametrize("fmt", kvlclib.reader_formats())
def test_reader_property_default(fmt, tmp_path):
    print(f"Looking at {fmt}")
    for p in kvlclib.Property:
        if fmt.isPropertySupported(p):
            print(f"\t {p.name}:", end="")
            default = fmt.getPropertyDefault(p)
            print(f" {default}")
