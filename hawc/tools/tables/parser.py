from html.parser import HTMLParser

import docx


def tag_wrapper(text, tag, *args):
    if len(args) == 0:
        return f"<{tag}>{text}</{tag}>"
    arg_tag = args[-1]
    text = f"<{arg_tag}>{text}</{arg_tag}>"
    return tag_wrapper(text, tag, *args[:-1])


def strip_tags(text, tag, *args):
    text = text.replace(f"<{tag}>", "").replace(f"</{tag}>", "")
    for arg_tag in args:
        text = text.replace(f"<{arg_tag}>", "").replace(f"</{arg_tag}>", "")
    return text


def ul_wrapper(texts):
    list_items = map(lambda text: tag_wrapper(text, "li"), texts)
    return f"<ul>{''.join(list_items)}</ul>"


def ol_wrapper(texts):
    list_items = map(lambda text: tag_wrapper(text, "li"), texts)
    return f"<ol>{''.join(list_items)}</ol>"


class QuillParser(HTMLParser):

    # Inline tags
    _inline_tags = ["strong", "em", "a"]
    # Inline tags to their font attribute
    _tag_font_attr = {"strong": "bold", "em": "italic"}
    # Cached inline tags
    _tags = set()

    # Paragraph tags
    _paragraph_tags = ["p", "h1", "h2", "li"]
    # Paragraph tags to their styles
    _tag_style = {
        "p": "Normal",
        "h1": "Heading 1",
        "h2": "Heading 2",
        "ol": "List Number",
        "ul": "List Bullet",
    }

    def feed(self, data, block):
        # block is either a _Body or _Cell object
        self._block = block
        super().feed(data)

    def add_hyperlink(self):
        # This gets access to the document.xml.rels file and gets a new relation id value
        part = self._paragraph.part
        r_id = part.relate_to(
            self._href, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True
        )

        # Create the w:hyperlink tag and add needed values
        hyperlink = docx.oxml.shared.OxmlElement("w:hyperlink")
        hyperlink.set(
            docx.oxml.shared.qn("r:id"), r_id,
        )
        hyperlink.append(self._inline._element)
        self._paragraph._p.append(hyperlink)

        # A workaround for the lack of a hyperlink style (doesn't go purple after using the link)
        self._inline.font.color.theme_color = docx.enum.dml.MSO_THEME_COLOR_INDEX.HYPERLINK
        self._inline.font.underline = True

    def handle_paragraph(self, tag):
        # We create a new paragraph and stylize it
        self._paragraph = self._block.add_paragraph()
        style = self._tag_style[self._list_type] if tag == "li" else self._tag_style[tag]
        self._paragraph.style = style
        # Then we create a new run for inline tags / data
        self._inline = self._paragraph.add_run()

    def handle_inline_start(self, tag, attrs):
        # A new inline tag means we have to create a new run
        self._inline = self._paragraph.add_run()
        if tag == "a":
            # We cache the href for hyperlink creation
            self._href = attrs[0][1]
        # We cache the tag so that we can later change the data font
        self._tags.add(tag)

    def handle_inline_end(self, tag):
        # A new run is created without the inline tag
        self._inline = self._paragraph.add_run()
        self._tags.remove(tag)

    def handle_starttag(self, tag, attrs):
        if tag == "ol" or tag == "ul":
            # We cache the list type to style list items
            self._list_type = tag
        elif tag in self._paragraph_tags:
            self.handle_paragraph(tag)
        elif tag in self._inline_tags:
            self.handle_inline_start(tag, attrs)

    def handle_data(self, data):
        self._inline.text += data
        # Apply the inline tag fonts/styles to the run with this data
        for tag in self._tags:
            if tag == "a":
                self.add_hyperlink()
            else:
                setattr(self._inline.font, self._tag_font_attr[tag], True)

    def handle_endtag(self, tag):
        if tag in self._inline_tags:
            self.handle_inline_end(tag)
