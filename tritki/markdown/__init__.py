import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.smarty import SmartyExtension

from tritki.markdown.wikilink import WikiLinkExtension
from tritki.markdown.smartsymbols import SmartSymbolsExtension

md = markdown.Markdown(
    extensions=[
        WikiLinkExtension(),
        TocExtension(
            baselevel=2,
        ),
        SaneListExtension(),
        SmartyExtension(),
        SmartSymbolsExtension(),
    ],
)
convert = md.convert