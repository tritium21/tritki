from functools import partial
import sys

from PyQt5 import QtWidgets, Qt, QtGui

class SpellTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, spelling_provider=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._sp = None
        self.highlighter = SpellingHighlighter(self.document())
        self.spelling_provider = spelling_provider

    @property
    def spelling_provider(self):
        return self._sp

    @spelling_provider.setter
    def spelling_provider(self, item):
        self._sp = item
        self.highlighter.spelling_provider = item

    def contextMenuEvent(self, event):
        pos = event.pos()
        menu = self.createStandardContextMenu(pos)
        spell_items = self._get_spelling_items(
            self._get_spelling_cursor(pos), menu)
        if spell_items:
            menu.insertSeparator(menu.actions()[0])
            for item in reversed(spell_items):
                menu.insertAction(menu.actions()[0], item)
        menu.exec_(event.globalPos())

    def _get_spelling_items(self, cursor, parent=None):
        if not cursor or not self.spelling_provider:
            return None
        text = cursor.selectedText()
        suggests = self.spelling_provider.suggest(text)
        spell_items = []
        for word in suggests:
            action = QtWidgets.QAction(word, parent)
            action.setData((cursor, word))
            action.triggered.connect(partial(self.cb_correct_word, action))
            spell_items.append(action)

        return spell_items

    def _get_spelling_cursor(self, pos):
        cursor = self.cursorForPosition(pos)
        misspelled_words = getattr(cursor.block().userData(), 'misspelled', [])

        # If the cursor is within a misspelling, select the word
        for (start, end) in misspelled_words:
            if start <= cursor.positionInBlock() <= end:
                block_pos = cursor.block().position()

                cursor.setPosition(block_pos + start, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(block_pos + end, QtGui.QTextCursor.KeepAnchor)
                break

        if cursor.hasSelection():
            return cursor
        else:
            return None

    def cb_correct_word(self, action):  # pylint: disable=no-self-use
        cursor, word = action.data()

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()

class SpellingHighlighter(QtGui.QSyntaxHighlighter):
    err_format = QtGui.QTextCharFormat()
    err_format.setUnderlineColor(QtGui.QColor(255, 0, 0))
    err_format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
    err_format.setForeground(QtGui.QBrush(QtGui.QColor(QtGui.QColor(255, 192, 192))))

    def __init__(self, *args, spelling_provider=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._sp = None
        self.spelling_provider = spelling_provider

    @property
    def spelling_provider(self):
        return self._sp

    @spelling_provider.setter
    def spelling_provider(self, item):
        if self._sp == item:
            return
        self._sp = item
        self.rehighlight()

    def highlightBlock(self, text):
        if not self.spelling_provider:
            return
        misspellings = []
        for (word, pos) in self.spelling_provider.tokenize(text):
            if not self.spelling_provider.check(word):
                self.setFormat(pos, len(word), self.err_format)
                misspellings.append((pos, pos + len(word)))
        data = QtGui.QTextBlockUserData()
        data.misspelled = misspellings
        self.setCurrentBlockUserData(data)

