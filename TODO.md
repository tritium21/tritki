# TODO

* import and export of data
  * also export rendered html suitable for uploading
* Global state manager (in progress)
  * store list of known wikis
  * store last accessed wiki (currently does, in the jankiest way possible)
  * this is where a file menu starts making sense

## Storage

* configurable location for file storage, especially to store the database file.
* Add media support to database models
  * https://github.com/pylover/sqlalchemy-media

## GUI

* Rewrite gui and app objects so that gui only interacts with methods directly on the app object.  This will suck.
  * app object grow an all articles method, rewrite model to call that, drop all sqlalchemy specific code
  * add search facilities to the app object, rewire gui to use that instead of the index directly
* Rewrite `./tritki/gui/alchemical.py` to not use QtSql
* Autosave edits.
  * Maybe not?

## History

* Nearly everything (but not everything - the database is in fact already versioned)