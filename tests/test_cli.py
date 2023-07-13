import pytest

from condact.cli import get_parsed_args

VALIDATE_GET_PARSED_ARGS_TEST_CASES = (
    (["--plugin", "foo", "activate"], ("foo", "activate", False, None, None)),
    (["-p", "baz", "activate"], ("baz", "activate", False, None, None)),
    (["activate"], (None, "activate", False, None, None)),
    (["activate", "test_env"], (None, "activate", False, None, "test_env")),
    (["reactivate"], (None, "reactivate", False, None, None)),
    (["reactivate", "--dev"], (None, "reactivate", True, None, None)),
    (["deactivate"], (None, "deactivate", False, None, None)),
    (["deactivate", "--dev"], (None, "deactivate", True, None, None)),
    (["activate", "--dev", "test_env"], (None, "activate", True, None, "test_env")),
    (
        ["activate", "--dev", "--stack", "test_env"],
        (None, "activate", True, True, "test_env"),
    ),
    (["activate", "--dev", "--no-stack", "base"], (None, "activate", True, False, "base")),
    (["activate", "--stack", "base"], (None, "activate", False, True, "base")),
    (["activate", "--no-stack", "test_env"], (None, "activate", False, False, "test_env")),
)

@pytest.mark.parametrize("a, expected", VALIDATE_GET_PARSED_ARGS_TEST_CASES)
def test_get_parsed_args(a: list, expected: tuple):
    """Test that the correct Namespace is returned for the given arguments"""
    ns = get_parsed_args(a)

    assert ns.plugin == expected[0]
    assert ns.command == expected[1]
    assert ns.dev == expected[2]
    assert getattr(ns, "stack", None) == expected[3]
    assert getattr(ns, "env", None) == expected[4]


VALIDATE_GET_PARSED_ARGS_ERROR_TEST_CASES = (
    (["katherine"], "invalid choice: 'katherine'"),
    (["--dev", "reactivate"], "unrecognized arguments"),
)

@pytest.mark.parametrize("a, expected", VALIDATE_GET_PARSED_ARGS_ERROR_TEST_CASES)
def test_get_parsed_args_error(a: list, expected: tuple, capsys):
    """Test that incorrect CLI arguments raise a SystemExit with the correct error message"""
    with pytest.raises(SystemExit):
        get_parsed_args(a)
    captured = capsys.readouterr()
    assert expected in captured.err


def test_get_parsed_args_help_flag(capsys):
    """Test that the help flag raises a SystemExit with the correct help message"""
    with pytest.raises(SystemExit):
        get_parsed_args(["-h"])
    captured = capsys.readouterr()
    assert "Process conda activate, deactivate, and reactivate" in captured.out