from __future__ import annotations

from io import StringIO
import unittest
from contextlib import redirect_stdout

import typer

from roll.app import root_commands


class RootCommandTests(unittest.TestCase):
    def test_update_prints_package_manager_guidance(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            with self.assertRaises(typer.Exit) as exc:
                root_commands.update()

        self.assertEqual(exc.exception.exit_code, 1)
        self.assertIn("does not self-update", output.getvalue())
