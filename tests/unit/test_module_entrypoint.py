"""Tests for running the package as a module."""

import runpy
from unittest.mock import patch

import pytest


def test_package_module_entrypoint_calls_main() -> None:
    with patch("ged_editor.main.main", return_value=0) as main:
        with pytest.raises(SystemExit) as exit_info:
            runpy.run_module("ged_editor", run_name="__main__")

    assert exit_info.value.code == 0
    main.assert_called_once_with()
