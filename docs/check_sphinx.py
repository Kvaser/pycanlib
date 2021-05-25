import subprocess

import py


def test_linkcheck(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    subprocess.check_call(
        ["sphinx-build", "-b linkcheck", "-d", str(doctrees), "docs", str(htmldir)]
    )


def test_build_docs(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    subprocess.check_call(["sphinx-build", "-bhtml", "-d", str(doctrees), "docs", str(htmldir)])
