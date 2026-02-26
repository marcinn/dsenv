import os
from io import StringIO

import pytest

from dsenv import load_env, load_merged_envs, parse_envfile


def test_parse_envfile_ignores_comments():
    buf = StringIO("# comment\nKEY=VALUE\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_empty_input():
    buf = StringIO("")
    assert parse_envfile(buf) == {}


def test_parse_envfile_only_comments_and_blank_lines():
    buf = StringIO("\n# one\n   \n# two\n")
    assert parse_envfile(buf) == {}


def test_parse_envfile_export_prefix():
    buf = StringIO("export KEY=VALUE\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_export_prefix_does_not_truncate_export_in_value():
    buf = StringIO("export KEY=fooexportbar\n")
    assert parse_envfile(buf) == {"KEY": "fooexportbar"}


def test_parse_envfile_accepts_spaces_around_equals():
    buf = StringIO(" KEY = VALUE \n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_export_with_extra_spaces():
    buf = StringIO("export    KEY=VALUE\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_only_lowercase_export_is_special_keyword():
    buf = StringIO("EXPORT KEY=VALUE\nKEY2=OK\n")
    assert parse_envfile(buf) == {"KEY2": "OK"}


def test_parse_envfile_duplicate_keys_last_wins():
    buf = StringIO("A=1\nA=2\n")
    assert parse_envfile(buf) == {"A": "2"}


def test_parse_envfile_unquoted_hash_is_treated_as_comment():
    buf = StringIO("KEY=abc#def\n")
    assert parse_envfile(buf) == {"KEY": "abc"}


def test_parse_envfile_supports_crlf_lines():
    buf = StringIO("A=1\r\nB=2\r\n")
    assert parse_envfile(buf) == {"A": "1", "B": "2"}


def test_parse_envfile_quoted_value():
    buf = StringIO('KEY="VALUE"\n')
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_quoted_value_keeps_equals_and_hash():
    buf = StringIO('KEY="A=B#C"\n')
    assert parse_envfile(buf) == {"KEY": "A=B#C"}


def test_parse_envfile_quoted_value_with_inline_comment_without_space():
    buf = StringIO('KEY="VALUE"#comment\n')
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_inline_comment_unquoted():
    buf = StringIO("KEY=VALUE # comment\n")
    assert parse_envfile(buf) == {"KEY": "VALUE"}


def test_parse_envfile_inline_comment_quoted():
    buf = StringIO('KEY="VALUE # keep"  # comment\n')
    assert parse_envfile(buf) == {"KEY": "VALUE # keep"}


def test_parse_envfile_empty_value():
    buf = StringIO("EMPTY=\n")
    assert parse_envfile(buf) == {"EMPTY": ""}


def test_parse_envfile_ignores_bad_lines():
    buf = StringIO("not_a_pair\n=novalue\nKEY=OK\n")
    assert parse_envfile(buf) == {"KEY": "OK"}


def test_parse_envfile_export_without_assignment_is_ignored():
    buf = StringIO("export KEY\nKEY2=OK\n")
    assert parse_envfile(buf) == {"KEY2": "OK"}


def test_parse_envfile_unclosed_quote_keeps_opening_quote_in_value():
    buf = StringIO('KEY="VALUE\n')
    assert parse_envfile(buf) == {"KEY": '"VALUE'}


def test_parse_envfile_accepts_unicode_values():
    buf = StringIO("KEY=zażółć\n")
    assert parse_envfile(buf) == {"KEY": "zażółć"}


def test_load_env_respects_override_env(tmp_path):
    path = tmp_path / "sample.env"
    path.write_text("A=1\nB=2\n")

    missing = object()
    old_a = os.environ.get("A", missing)
    old_b = os.environ.get("B", missing)

    try:
        if old_a is not missing:
            del os.environ["A"]
        os.environ["B"] = "old"

        load_env(str(path), override_env=False)
        assert os.environ["A"] == "1"
        assert os.environ["B"] == "old"

        load_env(str(path), override_env=True)
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


def test_load_env_raises_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing.env"
    with pytest.raises(FileNotFoundError):
        load_env(str(missing_path))


def test_load_env_expands_user_home(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env_file = home / "test.env"
    env_file.write_text("A=1\n")

    missing = object()
    old_a = os.environ.get("A", missing)

    try:
        os.environ.pop("A", None)
        monkeypatch.setenv("HOME", str(home))
        load_env("~/test.env")
        assert os.environ["A"] == "1"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a


def test_load_merged_envs_merges_in_order_and_respects_existing_env(tmp_path):
    base = tmp_path / "base.env"
    local = tmp_path / "local.env"
    base.write_text("A=1\nB=2\n")
    local.write_text("B=22\nC=3\n")

    missing = object()
    old_a = os.environ.get("A", missing)
    old_b = os.environ.get("B", missing)
    old_c = os.environ.get("C", missing)

    try:
        os.environ.pop("A", None)
        os.environ["B"] = "cli"
        os.environ.pop("C", None)

        load_merged_envs(str(base), str(local), override_env=False)

        assert os.environ["A"] == "1"
        assert os.environ["B"] == "cli"
        assert os.environ["C"] == "3"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a

        if old_b is missing:
            os.environ.pop("B", None)
        else:
            os.environ["B"] = old_b

        if old_c is missing:
            os.environ.pop("C", None)
        else:
            os.environ["C"] = old_c


def test_load_merged_envs_override_env_true_overrides_with_later_files(tmp_path):
    base = tmp_path / "base.env"
    local = tmp_path / "local.env"
    base.write_text("B=2\n")
    local.write_text("B=22\n")

    missing = object()
    old_b = os.environ.get("B", missing)

    try:
        os.environ["B"] = "cli"

        load_merged_envs(str(base), str(local), override_env=True)

        assert os.environ["B"] == "22"
    finally:
        if old_b is missing:
            os.environ.pop("B", None)
        else:
            os.environ["B"] = old_b


def test_load_merged_envs_merges_three_files_last_value_wins(tmp_path):
    f1 = tmp_path / "1.env"
    f2 = tmp_path / "2.env"
    f3 = tmp_path / "3.env"
    f1.write_text("A=1\nB=1\n")
    f2.write_text("B=2\nC=2\n")
    f3.write_text("C=3\nD=3\n")

    old = {k: os.environ.get(k, None) for k in ("A", "B", "C", "D")}
    missing = object()
    presence = {k: (os.environ.get(k, missing)) for k in ("A", "B", "C", "D")}

    try:
        for key in ("A", "B", "C", "D"):
            os.environ.pop(key, None)
        load_merged_envs(str(f1), str(f2), str(f3), override_env=True)
        assert os.environ["A"] == "1"
        assert os.environ["B"] == "2"
        assert os.environ["C"] == "3"
        assert os.environ["D"] == "3"
    finally:
        for key in ("A", "B", "C", "D"):
            if presence[key] is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old[key]


def test_load_merged_envs_override_false_preserves_existing_per_key(tmp_path):
    f1 = tmp_path / "1.env"
    f2 = tmp_path / "2.env"
    f1.write_text("A=fileA\nB=fileB\n")
    f2.write_text("B=fileB2\nC=fileC\n")

    missing = object()
    old_a = os.environ.get("A", missing)
    old_b = os.environ.get("B", missing)
    old_c = os.environ.get("C", missing)

    try:
        os.environ["A"] = "envA"
        os.environ.pop("B", None)
        os.environ["C"] = "envC"
        load_merged_envs(str(f1), str(f2), override_env=False)
        assert os.environ["A"] == "envA"
        assert os.environ["B"] == "fileB2"
        assert os.environ["C"] == "envC"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a
        if old_b is missing:
            os.environ.pop("B", None)
        else:
            os.environ["B"] = old_b
        if old_c is missing:
            os.environ.pop("C", None)
        else:
            os.environ["C"] = old_c


def test_load_merged_envs_ignores_missing_and_empty_paths(tmp_path):
    existing = tmp_path / "one.env"
    existing.write_text("A=1\n")

    missing = object()
    old_a = os.environ.get("A", missing)

    try:
        os.environ.pop("A", None)
        load_merged_envs("", str(tmp_path / "missing.env"), str(existing))
        assert os.environ["A"] == "1"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a


def test_load_merged_envs_with_no_files_is_noop():
    missing = object()
    old_a = os.environ.get("A", missing)

    try:
        os.environ["A"] = "existing"
        load_merged_envs()
        assert os.environ["A"] == "existing"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a


def test_load_merged_envs_expands_user_home(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env_file = home / "test.env"
    env_file.write_text("A=1\n")

    missing = object()
    old_a = os.environ.get("A", missing)

    try:
        os.environ.pop("A", None)
        monkeypatch.setenv("HOME", str(home))
        load_merged_envs("~/test.env")
        assert os.environ["A"] == "1"
    finally:
        if old_a is missing:
            os.environ.pop("A", None)
        else:
            os.environ["A"] = old_a


def test_load_merged_envs_override_true_overrides_existing_with_three_files(tmp_path):
    f1 = tmp_path / "1.env"
    f2 = tmp_path / "2.env"
    f3 = tmp_path / "3.env"
    f1.write_text("A=1\nB=1\n")
    f2.write_text("B=2\nC=2\n")
    f3.write_text("A=3\nD=3\n")

    missing = object()
    old_vals = {k: os.environ.get(k, missing) for k in ("A", "B", "C", "D")}

    try:
        os.environ["A"] = "envA"
        os.environ["B"] = "envB"
        os.environ.pop("C", None)
        os.environ["D"] = "envD"

        load_merged_envs(str(f1), str(f2), str(f3), override_env=True)

        assert os.environ["A"] == "3"
        assert os.environ["B"] == "2"
        assert os.environ["C"] == "2"
        assert os.environ["D"] == "3"
    finally:
        for key, old_value in old_vals.items():
            if old_value is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value
