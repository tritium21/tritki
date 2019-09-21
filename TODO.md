# TODO

# Search

* Wire in the search box on the gui
* Write the search template, code to handle showing search results and going back to previous state

# Storage

* configurable location for file storage, especially to store the database file.
* Add media support to database models
  * https://github.com/pylover/sqlalchemy-media

# GUI

* Rewrite `./tritki/gui/spelledit.py` to use a spelling library that supports Windows 64, and Python 3.7+ (currently uses pyenchant which supports Windows 32, and Python 3.6)
  * Now that whoosh is being used, wire spell edit to that?
* Wire up the 'New' button
* Wire up the bold, italic, blockquote, and paragraph buttons

# History

* Nearly everything (but not everything - the database is in fact already versioned)