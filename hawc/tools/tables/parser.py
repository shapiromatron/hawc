from html.parser import HTMLParser


class CellHTMLParser(HTMLParser):
    def feed(self, data, par):
        self.par = par
        super().feed(data)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_data(self, data):
        self.par.add_run(data)

    def handle_endtag(self, tag):
        pass
