import os
from io import StringIO

from dsenv import load_env, parse_envfile


def test_parse_envfile_ignores_comments():
    buf = StringIO("# comment\nKEY=VALUE\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_export_prefix():
    buf = StringIO("export KEY=VALUE\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_quoted_value():
    buf = StringIO("KEY=\"VALUE\"\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_inline_comment_unquoted():
    buf = StringIO("KEY=VALUE # comment\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_inline_comment_quoted():
    buf = StringIO("KEY=\"VALUE # keep\"  # comment\n")
    assert parse_envfile(buf) == {"KEY": "VALUE # keep"}


def test_parse_envfile_empty_value():
    buf = StringIO("EMPTY=\n")
    assert parse_envfile(buf) == {"EMPTY": ""}


def test_parse_envfile_ignores_bad_lines():
    buf = StringIO("not_a_pair\n=novalue\nKEY=OK\n")
    assert parse_envfile(buf) == {"KEY": "OK"}


def test_load_env_respects_override(tmp_path):
    path = tmp_path / "sample.env"
    path.write_text("A=1\nB=2\n")

    missing = object()
    old_a = os.environ.get("A", missing)
    old_b = os.environ.get("B", missing)

    try:
        if old_a is not missing:
            del os.environ["A"]
        os.environ["B"] = "old"

        load_env(str(path), override=False)
        assert os.environ["A"] == "1"
        assert os.environ["B"] == "old"

        load_env(str(path), override=True)
        assert os.environ["B"] == "2"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a

        if old_b is missing:
            os.environ.pop("B", None)
        else:
            os.environ["B"] = old_b
