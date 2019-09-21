import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.smarty import SmartyExtension

from tritki.markdown.wikilink import WikiLinkExtension
from tritki.markdown.smartsymbols import SmartSymbolsExtension
from tritki.markdown.classify import ClassifyExtension


class Converter:
    def __init__(self, app):
        self.app = app
        self.markdown = markdown.Markdown(
            extensions=[
                ClassifyExtension(),
                WikiLinkExtension(
                    build_url=self.build_url,
                    html_class=self.html_class,
                ),
                TocExtension(
                    baselevel=2,
                ),
                SaneListExtension(),
                SmartyExtension(),
                SmartSymbolsExtension(),
            ],
            output_format='html5',
        )

    def build_url(self, target):
        if self.app.exists(target):
            return f"view:///{target}"
        return f"edit:///{target}"

    def html_class(self, target):
        if self.app.exists(target):
            return "wiki"
        return "wiki noexist"

    def convert(self, content):
        return self.markdown.convert(content)