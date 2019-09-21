import re

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree



class WikiLinkExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'html_class': [lambda x: None, 'Callable returns HTML class for target.'],
            'build_url': [lambda x: f"/{x}", 'Callable returns link for target.'],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md
        # append to end of inline patterns
        WIKILINK_RE = r'\[\[([\w0-9_ -]+\|?.*?)\]\]'
        wikilinkPattern = WikiLinksInlineProcessor(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)


class WikiLinksInlineProcessor(InlineProcessor):
    def __init__(self, pattern, config):
        super().__init__(pattern)
        self.config = config

    def handleMatch(self, m, data):
        if m.group(1).strip():
            target, _, text = m.group(1).partition('|')
            target = target.strip()
            text = text.strip()
            text = text or target

            url = self.config['build_url'](target)

            html_class = self.config['html_class'](target)

            a = etree.Element('a')
            a.text = text
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a, m.start(0), m.end(0)



