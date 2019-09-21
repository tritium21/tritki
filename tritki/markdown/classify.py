import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree


class ClassifyTreeprocessor(Treeprocessor):
    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, root):
        links = root.findall('.//a')
        for link in links:
            if 'class' in link.attrib:
                continue
            link.set('class', self.config['link_class'])
        return root


class ClassifyExtension(markdown.Extension):
    def __init__(self, **kwargs):
        self.config = {
            'link_class': ['external', 'Class name for links'],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        ext = ClassifyTreeprocessor(md, config=self.getConfigs())
        md.treeprocessors.add('classify', ext, '_end')