import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import security_check


class ValidateGitignoreTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.gitignore = Path(temporary_directory.name) / ".gitignore"
        patcher = patch.object(security_check, "GITIGNORE_FILE", self.gitignore)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_accepts_directory_rules_with_or_without_trailing_slashes(self):
        for suffix in ("", "/"):
            with self.subTest(suffix=suffix):
                self.gitignore.write_text(
                    f".env\n.venv{suffix}\n__pycache__{suffix}\n",
                    encoding="utf-8",
                )
                output = io.StringIO()

                with redirect_stdout(output):
                    security_check.validate_gitignore()

                self.assertIn("[PASS]", output.getvalue())

    def test_rejects_missing_rules_and_env_directory_rule(self):
        for content in (
            ".venv/\n__pycache__/\n",
            ".env/\n.venv/\n__pycache__/\n",
            ".env\n__pycache__/\n",
            ".env\n.venv/\n",
        ):
            with self.subTest(content=content):
                self.gitignore.write_text(content, encoding="utf-8")

                with self.assertRaisesRegex(
                    ValueError, "Missing .gitignore entries"
                ):
                    security_check.validate_gitignore()


if __name__ == "__main__":
    unittest.main()
