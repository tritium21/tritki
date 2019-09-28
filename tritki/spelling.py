import pathlib
import re
from importlib import resources

from whoosh.spelling import ListCorrector


class Spelling:
    TOKEN_PATTERN = re.compile(r'[\w\']+')

    def __init__(self):
        with resources.path('tritki.data', 'words.txt') as pth:
            with open(pth) as f:
                self.words = [w.strip() for w in f.readlines()]
        self.corrector = ListCorrector(self.words)

    def suggest(self, term):
        return list(self.corrector.suggest(term))

    def check(self, term):
        return term.lower() in self.words

    def tokenize(self, block):
        return [(block[x.start():x.end()], x.start()) for x in self.TOKEN_PATTERN.finditer(block)]