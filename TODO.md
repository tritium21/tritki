# TODO

* import and export of data
  * also export rendered html suitable for uploading
* Global state manager (in progress)
  * store list of known wikis
  * store last accessed wiki (currently does, in the jankiest way possible)
  * this is where a file menu starts making sense
* Implement and `importlib.resources` based Loader for `Jinja2`
  * https://jinja.palletsprojects.com/en/2.10.x/api/#loaders

## Storage

* configurable location for file storage, especially to store the database file.
* Add media support to database models
  * https://github.com/pylover/sqlalchemy-media

## GUI

* Rewrite gui and app objects so that gui only interacts with methods directly on the app object.  This will suck.
  * add search facilities to the app object, rewire gui to use that instead of the index directly
* Autosave edits.
  * Maybe not?

# Abandoned

* History - just not worth it for this project.