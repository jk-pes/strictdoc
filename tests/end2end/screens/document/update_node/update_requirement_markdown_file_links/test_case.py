import os
import subprocess
import sys
import tempfile
from pathlib import Path

from strictdoc import environment
from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test_markdown_file_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_root = Path(temporary_directory) / "input"
            input_root.mkdir()
            nested_root = input_root / "nested"
            nested_root.mkdir()
            source = input_root / "source.md"
            source.write_text(
                "# Source\n\n"
                "## Navigation\n\n"
                "**UID**: NAV\n\n"
                '<./other.md>\n\n<a href="./other.md">Other</a>\n',
                encoding="utf8",
            )
            (input_root / "other.md").write_text(
                "# Other\n\n<./source.md>\n",
                encoding="utf8",
            )
            (nested_root / "target.markdown").write_text(
                "# Target\n\n"
                "**UID**: TARGET\n\n"
                '<../source.md>\n\n<a href="../source.md">Source</a>\n',
                encoding="utf8",
            )

            with SDocTestServer(input_path=str(input_root)) as test_server:
                self.open(test_server.get_host_and_port())
                project_index = Screen_ProjectIndex(self)
                project_index.do_click_on_the_document_with_title("Source")
                source_url = self.get_current_url()
                self._check_navigation(source_url, "./other.html", "Other")

                document_screen = Screen_Document(self)
                requirement = document_screen.get_node_by_anchor("NAV")
                form = requirement.do_open_form_edit_requirement()
                statement = (
                    "<./nested/target.markdown?view=1#TARGET>\n\n"
                    '<a href="./nested/target.markdown?view=1#TARGET">'
                    "Target</a>\n\n"
                    "<./other.md>\n\n"
                    '<a href="./other.md">Other</a>'
                )
                form.do_fill_in_field_statement(statement)
                form.do_form_submit()
                self._check_navigation(
                    source_url,
                    "./nested/target.html?view=1#TARGET",
                    "Target",
                )
                self._check_navigation(source_url, "./other.html", "Other")
                assert statement in source.read_text(encoding="utf8")

                self.refresh_page()
                self._check_navigation(
                    source_url,
                    "./nested/target.html?view=1#TARGET",
                    "Target",
                )

            output_root = Path(temporary_directory) / "output"
            subprocess.run(
                [
                    sys.executable,
                    os.path.join(
                        environment.path_to_strictdoc, "strictdoc/cli/main.py"
                    ),
                    "export",
                    ".",
                    "--output-dir",
                    str(output_root),
                ],
                cwd=input_root,
                check=True,
            )
            exported_source = next((output_root / "html").rglob("source.html"))
            source_url = exported_source.as_uri()
            self.open(source_url)
            self._check_navigation(
                source_url, "./nested/target.html?view=1#TARGET", "Target"
            )
            self._check_navigation(source_url, "./other.html", "Other")

    def _check_navigation(self, source_url: str, href: str, title: str) -> None:
        for index_ in (1, 2):
            self.click(f'(//sdoc-node//a[@href="{href}"])[{index_}]')
            Screen_Document(self).assert_header_document_title(title)
            return_href = (
                "../source.html" if title == "Target" else "./source.html"
            )
            self.click(f'//sdoc-node//a[@href="{return_href}"]')
            Screen_Document(self).assert_header_document_title("Source")
            self.assert_url(source_url)
