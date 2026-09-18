import pytest

from strictdoc.backend.markdown.markdown_to_html_fragment_writer import (
    MarkdownToHtmlFragmentWriter,
)


def test_01_writes_markdown_to_html_fragment():
    markdown_input = "This is **bold** text."

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == "<p>This is <strong>bold</strong> text.</p>\n"


def test_02_writes_escaped_anchor_link():
    html_link = MarkdownToHtmlFragmentWriter.write_anchor_link(
        'A & B "Title"',
        'https://example.com?q=1&x="2"',
    )

    assert (
        html_link == '<a href="https://example.com?q=1&amp;x=&quot;2&quot;">'
        "🔗&nbsp;A &amp; B &quot;Title&quot;"
        "</a>"
    )


def test_03_write_with_validation_returns_html_without_error():
    html_output, error = MarkdownToHtmlFragmentWriter.write_with_validation(
        "Hello **Markdown**."
    )

    assert error is None
    assert html_output == "<p>Hello <strong>Markdown</strong>.</p>\n"


def test_04_writes_markdown_table_to_html_table():
    markdown_input = "| Col A | Col B |\n| --- | --- |\n| A1 | B1 |\n"

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert "<table>" in html_output
    assert "<th>Col A</th>" in html_output
    assert "<th>Col B</th>" in html_output
    assert "<td>A1</td>" in html_output
    assert "<td>B1</td>" in html_output


def test_05_writes_mermaid_fence_as_mermaid_pre_block():
    markdown_input = "```mermaid\ngraph TD\n  A-->B\n```\n"

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == (
        '<pre class="mermaid">graph TD\n  A--&gt;B\n</pre>\n'
    )


def test_05a_writes_plantuml_fence_as_plantuml_pre_block():
    markdown_input = "```plantuml\n@startuml\nAlice -> Bob\n@enduml\n```\n"

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == (
        '<pre class="plantuml">@startuml\nAlice -&gt; Bob\n@enduml\n</pre>\n'
    )


def test_06_writes_recognized_language_fence_as_highlighted_code_block():
    markdown_input = "```python\nprint(1)\n```\n"

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == (
        '<pre class="code">\n'
        '<span class="nb">print</span><span class="p">(</span>'
        '<span class="mi">1</span><span class="p">)</span>\n'
        "</pre>\n"
    )


def test_06a_writes_unrecognized_language_fence_as_plain_code_block():
    markdown_input = "```notalang\nsome text\n```\n"

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == (
        '<pre><code class="language-notalang">some text\n</code></pre>\n'
    )


def test_07_renders_anchor_link_as_raw_html_not_escaped():
    markdown_input = MarkdownToHtmlFragmentWriter.write_anchor_link(
        "Title",
        "foo.bar",
    )

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert html_output == '<p><a href="foo.bar">🔗\u00a0Title</a></p>\n'


def test_08_renders_inline_math_formula():
    markdown_input = "The mass is $m_d = 120\\,kg$."

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert (
        html_output
        == '<p>The mass is <span class="math notranslate nohighlight">\\( m_d = 120\\,kg \\)</span>.</p>\n'
    )


def test_09_renders_display_math_formula():
    markdown_input = "The formula $$E = mc^2$$."

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert (
        html_output
        == '<p>The formula <div class="math notranslate nohighlight">\\[ E = mc^2 \\]</div>.</p>\n'
    )


def test_10_renders_two_inline_math_formulas_in_one_paragraph():
    markdown_input = (
        "The dry mass $m_d = 120\\,kg$ and propellant mass $m_p = 30\\,kg$."
    )

    html_output = MarkdownToHtmlFragmentWriter().write(markdown_input)

    assert (
        '<span class="math notranslate nohighlight">\\( m_d = 120\\,kg \\)</span>'
        in html_output
    )
    assert (
        '<span class="math notranslate nohighlight">\\( m_p = 30\\,kg \\)</span>'
        in html_output
    )


@pytest.mark.parametrize(
    ("markdown_input", "expected"),
    [
        (
            "<./other.md>",
            '<p><a href="./other.html">./other.md</a></p>\n',
        ),
        (
            "<../nested/other.markdown?view=1&mode=2#section>",
            (
                '<p><a href="../nested/other.html?view=1&amp;mode=2#section">'
                "../nested/other.markdown?view=1&amp;mode=2#section</a></p>\n"
            ),
        ),
        (
            "[Other](<./other file.md#section>)",
            '<p><a href="./other%20file.html#section">Other</a></p>\n',
        ),
        (
            '<a href="./other.md">Other</a>',
            '<p><a href="./other.html">Other</a></p>\n',
        ),
        (
            "<a class='nav' href='../other.MD?x=1&amp;y=2#section'>Other</a>",
            (
                "<p><a class='nav' href='../other.html?x=1&amp;y=2#section'>"
                "Other</a></p>\n"
            ),
        ),
        (
            "<a href=other.md>Other</a>",
            "<p><a href=other.html>Other</a></p>\n",
        ),
        (
            (
                '<div>\n<A\nHREF="./other.md" title="A &quot;quote&quot;">'
                "Other</A>\n</div>\n"
            ),
            (
                '<div>\n<A\nHREF="./other.html" title="A &quot;quote&quot;">'
                "Other</A>\n</div>\n"
            ),
        ),
        (
            "[Other][reference]\n\n[reference]: other.md\n",
            '<p><a href="other.html">Other</a></p>\n',
        ),
        (
            '<a href="other.md?x=1&copy=2" title="&notit;">Other</a>',
            '<p><a href="other.html?x=1&copy=2" title="&notit;">Other</a></p>\n',
        ),
        (
            """<a title=' href="example.md"' href="other.md">Other</a>""",
            """<p><a title=' href="example.md"' href="other.html">Other</a></p>\n""",
        ),
        (
            '<a href="other.md&#35;section">Other</a>',
            '<p><a href="other.html&#35;section">Other</a></p>\n',
        ),
        (
            '<a href="Bob&#x27;s.md">Other</a>',
            '<p><a href="Bob&#x27;s.html">Other</a></p>\n',
        ),
        (
            '<a href="other&#46;md&#63;x=1&copy=2">Other</a>',
            '<p><a href="other.html&#63;x=1&copy=2">Other</a></p>\n',
        ),
    ],
)
def test_relative_markdown_links(markdown_input: str, expected: str) -> None:
    assert MarkdownToHtmlFragmentWriter().write(markdown_input) == expected
    assert MarkdownToHtmlFragmentWriter.write_with_validation(
        markdown_input
    ) == (expected, None)


@pytest.mark.parametrize(
    "destination",
    [
        "https://example.com/other.md",
        "http://example.com/other.markdown#section",
        "//example.com/other.md",
        "/other.md",
        "#other.md",
        "?file=other.md",
        "mailto:other.md",
        "javascript:other.md",
        "data:text/html,other.md",
        r"..\other.md",
        "other.pdf",
        "other.md.png",
        "other.html",
        "https&colon;//example.com/other.md",
        "&#47;&#47;example.com/other.md",
    ],
)
def test_non_relative_markdown_destinations_are_unchanged(
    destination: str,
) -> None:
    markdown_input = f'<a href="{destination}">Other</a>'
    assert MarkdownToHtmlFragmentWriter().write(markdown_input) == (
        f"<p>{markdown_input}</p>\n"
    )


@pytest.mark.parametrize(
    ("markdown_input", "expected"),
    [
        ("`<./other.md>`", "<p><code>&lt;./other.md&gt;</code></p>\n"),
        (
            '```\n<a href="./other.md">Other</a>\n<./other.md>\n```',
            (
                "<pre><code>&lt;a href=&quot;./other.md&quot;&gt;Other&lt;/a&gt;\n"
                "&lt;./other.md&gt;\n</code></pre>\n"
            ),
        ),
        (
            "    <./other.md>\n",
            "<pre><code>&lt;./other.md&gt;\n</code></pre>\n",
        ),
        (r"\<./other.md>", "<p>&lt;./other.md&gt;</p>\n"),
        (
            "![Image](./other.md)",
            '<p><img src="./other.md" alt="Image"></p>\n',
        ),
        ("<a>link text</a>", "<p><a>link text</a></p>\n"),
        (
            '<a href="other.html"><./other.md></a>',
            '<p><a href="other.html">&lt;./other.md&gt;</a></p>\n',
        ),
        (
            '<!-- <a href="./other.md">Other</a> -->',
            '<!-- <a href="./other.md">Other</a> -->',
        ),
    ],
)
def test_code_and_non_link_content_are_unchanged(
    markdown_input: str, expected: str
) -> None:
    assert MarkdownToHtmlFragmentWriter().write(markdown_input) == expected
