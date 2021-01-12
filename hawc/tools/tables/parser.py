from html.parser import HTMLParser


class HtmlDocxParser(HTMLParser):
    def feed(self, data, block):
        self.block = block
        super().feed(data)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_data(self, data):
        self.block.add_run(data)

    def handle_endtag(self, tag):
        pass
