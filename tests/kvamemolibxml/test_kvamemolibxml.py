import os

from canlib import kvamemolibxml


def test_version():
    v = kvamemolibxml.dllversion()
    print(v)
    print(v.major, v.minor)


def test_ok_config(datadir):
    xml_fp = os.path.join(datadir, "logall.xml")
    with open(xml_fp, 'r') as f:
        xml_string = f.read()

    config = kvamemolibxml.load_xml(xml_string)
    assert config.xml == xml_string
    assert config == kvamemolibxml.load_xml_file(xml_fp)

    lif_fp = os.path.join(datadir, "logall.lif")
    with open(lif_fp, 'rb') as f:
        lif_bytes = f.read()

    config2 = kvamemolibxml.load_lif(lif_bytes)
    assert config2.lif == lif_bytes
    assert config2 == kvamemolibxml.load_lif_file(lif_fp)

    assert config == config2
    assert config.lif == config2.lif == lif_bytes

    errors, warnings = config.validate()
    assert not errors
    assert not warnings
    assert config2.validate() == (errors, warnings)


def test_err_config(datadir):
    config = kvamemolibxml.load_xml_file(os.path.join(datadir, "test01.xml"))
    errors, warnings = config.validate()
    assert not warnings
    assert len(errors) == 1
    error = errors[0]
    print(error)
    assert error.code is kvamemolibxml.ValidationError.EXPRESSION
    assert error.text


def test_xmlGetValidationError(datadir):
    (status, text) = kvamemolibxml.xmlGetValidationError()
    print("Validation error status:%d, text:\n%s" % (status, text))
    assert status == kvamemolibxml.KvaXmlStatusOK
    assert text == ""

    filename = os.path.join(datadir, "test01.xml")
    with open(filename, 'r') as myfile:
        config_xml = myfile.read()
    kvamemolibxml.kvaXmlValidate(config_xml)
    (numErr, numWarn) = kvamemolibxml.xmlGetValidationStatusCount()
    assert numWarn == 0
    assert numErr == 1
    (status, text) = kvamemolibxml.xmlGetValidationError()
    print("First validation error:%d, text:\n%s" % (status, text))
    assert status == kvamemolibxml.ValidationError.EXPRESSION
    assert text == (
        "The trigger 'My_first_id_trigger' in"
        " 'My_first_id_trigger,My_first_dlc_trigger,AND,"
        "My_first_id_trigger,OR' is not defined.\n"
    )

    (status, text) = kvamemolibxml.xmlGetValidationError()
    assert status == kvamemolibxml.KvaXmlStatusOK
