# TODO

* import and export of data
* user persistence of last database used

## Storage

* configurable location for file storage, especially to store the database file.
* Add media support to database models
  * https://github.com/pylover/sqlalchemy-media
  * low priority, current view object does not support media.  Semi-major recode to switch to web engine

## GUI

* Rewrite `./tritki/gui/spelledit.py` to use a spelling library that supports Windows 64, and Python 3.7+ (currently uses pyenchant which supports Windows 32, and Python 3.6)
  * Now that whoosh is being used, wire spell edit to that?
* Rewrite gui and app objects so that gui only interacts with methods directly on the app object.  This will suck.
  * app object grow an all articles method, rewrite model to call that, drop all sqlalchemy specific code
  * add search facilities to the app object, rewire gui to use that instead of the index directly

## History

* Nearly everything (but not everything - the database is in fact already versioned)