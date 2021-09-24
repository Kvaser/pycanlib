import os

from conftest import kvdeprecated

from canlib import kvamemolibxml


@kvdeprecated
def test_import_kvamemolibxml():
    xl = kvamemolibxml.kvaMemoLibXml()
    print(f"Python kvaMemoLibXml version: v{xl.getVersion()}")


@kvdeprecated
def test_xmlGetValidationError(datadir):
    xl = kvamemolibxml.kvaMemoLibXml()
    (status, text) = xl.xmlGetValidationError()
    print("Validation error status:%s, text:\n%s" % (status, text))
    assert status == kvamemolibxml.KvaXmlStatusOK
    assert text == ""

    filename = os.path.join(datadir, "test01.xml")
    with open(filename, 'r') as myfile:
        config_xml = myfile.read()
    xl.kvaXmlValidate(config_xml)
    (numErr, numWarn) = xl.xmlGetValidationStatusCount()
    assert numWarn == 0
    assert numErr == 1
    (status, text) = xl.xmlGetValidationError()
    print("First validation error:%d, text:\n%s" % (status, text))
    assert status == kvamemolibxml.ValidationError.EXPRESSION
    assert text == (
        "The trigger 'My_first_id_trigger' in"
        " 'My_first_id_trigger,My_first_dlc_trigger,AND,"
        "My_first_id_trigger,OR' is not defined.\n"
    )

    (status, text) = xl.xmlGetValidationError()
    assert status == kvamemolibxml.KvaXmlStatusOK
