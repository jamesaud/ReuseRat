# create a subclass and override the handler methods
from html.parser import HTMLParser
from collections import defaultdict

class AdminHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.tags = defaultdict(lambda: 0)
        super(AdminHTMLParser, self).__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1

    def handle_endtag(self, tag):
        self.tags[tag] += 1


# instantiate the parser and fed it some HTML
