from textwrap import dedent

import pytest


@pytest.fixture
def quill_html():
    html = dedent(
        """
            <h1>Header One</h1>
            <h2>Header Two</h2>
            <p>Paragraph text, with <strong>bold</strong>, <em>italics</em>, <a href="www.google.com">links</a>, and <strong><em>combinations</em></strong>.
            <ul>
                <li>Unordered List</li>
            </ul>
            <ol>
                <li>Ordered List</li>
            </ol>
            """
    )
    return html.replace("\n", "")
