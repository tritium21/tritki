import sys

from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import (QFocusEvent, QSyntaxHighlighter, QTextBlockUserData,
                         QTextCharFormat, QTextCursor)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QMenu,
                             QPlainTextEdit)

class SpellTextEdit(QPlainTextEdit):
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
        popup_menu = self.createSpellcheckContextMenu(event.pos())
        popup_menu.exec_(event.globalPos())

    def createSpellcheckContextMenu(self, pos):
        menu = self.createStandardContextMenu(pos)
        spell_menu = self.createCorrectionsMenu(
            self.cursorForMisspelling(pos), menu)

        if spell_menu:
            menu.insertSeparator(menu.actions()[0])
            menu.insertMenu(menu.actions()[0], spell_menu)

        return menu

    def createCorrectionsMenu(self, cursor, parent=None):
        """Create and return a menu for correcting the selected word."""
        if not cursor or not self.spelling_provider:
            return None

        text = cursor.selectedText()
        suggests = self.spelling_provider.suggest(text)

        spell_menu = QMenu('Spelling Suggestions', parent)
        for word in suggests:
            action = QAction(word, spell_menu)
            action.setData((cursor, word))
            spell_menu.addAction(action)

        # Only return the menu if it's non-empty
        if spell_menu.actions():
            spell_menu.triggered.connect(self.cb_correct_word)
            return spell_menu

        return None

    def cursorForMisspelling(self, pos):
        """Return a cursor selecting the misspelled word at ``pos`` or ``None``

        This leverages the fact that QPlainTextEdit already has a system for
        processing its contents in limited-size blocks to keep things fast.
        """
        cursor = self.cursorForPosition(pos)
        misspelled_words = getattr(cursor.block().userData(), 'misspelled', [])

        # If the cursor is within a misspelling, select the word
        for (start, end) in misspelled_words:
            if start <= cursor.positionInBlock() <= end:
                block_pos = cursor.block().position()

                cursor.setPosition(block_pos + start, QTextCursor.MoveAnchor)
                cursor.setPosition(block_pos + end, QTextCursor.KeepAnchor)
                break

        if cursor.hasSelection():
            return cursor
        else:
            return None

    def cb_correct_word(self, action):  # pylint: disable=no-self-use
        """Event handler for 'Spelling Suggestions' entries."""
        cursor, word = action.data()

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()

class SpellingHighlighter(QSyntaxHighlighter):
    err_format = QTextCharFormat()
    err_format.setUnderlineColor(Qt.red)
    err_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

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
        """Overridden QSyntaxHighlighter method to apply the highlight"""
        if not self.spelling_provider:
            return

        # Build a list of all misspelled words and highlight them
        misspellings = []
        for (word, pos) in self.spelling_provider.tokenize(text):
            if not self.spelling_provider.check(word):
                self.setFormat(pos, len(word), self.err_format)
                misspellings.append((pos, pos + len(word)))

        # Store the list so the context menu can reuse this tokenization pass
        # (Block-relative values so editing other blocks won't invalidate them)
        data = QTextBlockUserData()
        data.misspelled = misspellings
        self.setCurrentBlockUserData(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    spellEdit = SpellTextEdit()
    spellEdit.show()

    sys.exit(app.exec_())
