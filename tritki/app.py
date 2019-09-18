import os
import pathlib

import tritki.models
import tritki.gui

DATABASE_NAME = 'tritki.db'

class App:
    def __init__(self, *, data_path=None, create=False, qt_args=None):
        self.data_path = None
        self.database_uri = None
        self.db = None
        self.triggers = set()
        tritki.gui.run_gui(qt_args)
        if data_path is not None:
            self.load(data_path, create=create)

    def load(self, data_path, *, create=False):
        data_path = pathlib.Path(data_path).resolve(strict=not create)
        if create:
            data_path.mkdir(parents=True)
        db_path = (data_path / DATABASE_NAME).resolve(strict=not create)
        self.database_uri = db_path.as_uri().replace('file:', 'sqlite:')
        self.db = tritki.models.DB(uri=self.database_uri)
        self.data_path = data_path

    def execute_trigger(self):
        for trigger in self.triggers:
            trigger(self)

    def register_trigger(self, func):
        if callable(func):
            self.triggers.add(func)