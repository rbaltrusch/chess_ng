# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 16:40:18 2022

@author: richa
"""
import datetime
import logging
import os
import sys


class Logger:
    """Logger context manager"""

    def __init__(self, folder: str, filename: str):
        self.folder = folder
        self.filename = filename
        self.logger: logging.Logger = None  # type: ignore

    def __enter__(self):
        self._init_folder()
        self._init_logger()
        return self.logger

    def __exit__(self, *_):
        self.logger.handlers.clear()
        logging.shutdown()

    def _init_logger(self):
        self.logger = logging.getLogger("game.log")
        self.logger.handlers.clear()

        now = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filepath = os.path.join(self.folder, f"{now}_game.log")
        file_handler = logging.FileHandler(filepath, mode="w")
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.propagate = False

    def _init_folder(self):
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
