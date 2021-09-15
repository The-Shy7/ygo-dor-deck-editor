import traceback
import re
from os import path

from PyQt5.QtCore import QSize, QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog,
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QGridLayout, QMenuBar, QMenu, QAction, QApplication, QStatusBar, QListWidget,
                             QLineEdit, QTextEdit, QListWidgetItem)
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

STARTER_DECK_OFFSET = 0x2A0A70
CPU_DECK_OFFSET = 0x2A1316
CARDS = {}

try:
    with open("cardlist.txt", "r") as f:
        for i, card in enumerate(f):
            trimmed_card = card.strip()
            assert trimmed_card != ""
            CARDS[i] = trimmed_card
except:
    traceback.print_exc()
    CARDS = None # can't show card names

def get_name(card_id):
    if CARDS is None:
        return "---"
    elif card_id not in CARDS:
        return "id_out_of_bounds"
    else:
        return CARDS[card_id]

def match_name(name):
    lowername = name.lower()
    
    if CARDS is not None:
        for i, card in CARDS.items():
            if card.lower() == lowername:
                return i, card

        return None, None
    else:
        return None, None

def match_partly(name):
    lowername = name.lower()
    
    if CARDS is not None:
        pattern = ".*{0}.*".format(lowername)
        matches = []

        for i, card in CARDS.items():
            match = re.match(pattern, card.lower())
            
            if match is not None:
                matches.append((i, card))
        
        if len(matches) == 0:
            return None, None
        elif len(matches) == 1:
            return matches[0]
        else:
            return matches
    else:
        return None, None

class YugiohDeckEntry(QListWidgetItem):
    def __init__(self, starter, number, offset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_starter = starter
        self.number = number
        self.deck_offset = offset

def set_default_path(path):
    print("WRITING", path)
    
    try:
        with open("default_path2.cfg", "wb") as f:
            f.write(bytes(path, encoding="utf-8"))
    except Exception as error:
        print("couldn't write path")
        traceback.print_exc()
        pass

def get_default_path():
    print("READING")
    
    try:
        with open("default_path2.cfg", "rb") as f:
            path = str(f.read(), encoding="utf-8")
        return path
    except:
        return None

class DeckEditorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.stringfile = None
        self.reset_in_process = False
        path = get_default_path()
        
        if path is None:
            self.default_path = ""
        else:
            self.default_path = path

        self.deck_list.currentItemChanged.connect(self.action_listwidget_change_item)
        self.button_set_deck.pressed.connect(self.action_button_set_deck)
        self.deck_data = None
        
    def reset(self):
        self.reset_in_process = True
        self.deck_list.clearSelection()
        self.deck_list.clear()

        self.reset_in_process = False