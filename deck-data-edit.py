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

    def action_button_set_deck(self):
        print("I was pressed")
        current = self.deck_list.currentItem()
        self.statusbar.clearMessage()
        
        if current is not None and self.deck_data is not None:
            try:
                leader, rank = self.lineedit_leader.text(), self.lineedit_leader_rank.text()

                deck_data = []

                if rank.isnumeric():
                    rank = int(rank)
                else:
                    self.statusbar.showMessage("Rank is not numeric")
                    return

                if leader.isnumeric():
                    leaderdata = (int(leader) & 0xFFF) | ((rank & 0xF) << 12)
                else:
                    match = match_partly(leader)

                    if isinstance(match, tuple) and match[0] is None:
                        self.statusbar.showMessage("No matching card found: '{0}'".format(leader))
                        return
                    elif isinstance(match, tuple):
                        index, card = match
                        leaderdata = (int(index) & 0xFFF) | ((rank & 0xF) << 12)
                    else:
                        if len(match) > 5:
                            self.statusbar.showMessage("Too many matches found ({0} matches)".format(len(match)))
                        else:
                            self.statusbar.showMessage("More than 1 match found: {0}".format(
                                ", ".join("{0} ({1})".format(x[1], x[0]) for x in match)))
                        return

                deck_data.append(leaderdata)
                cards = []
                
                for i in range(40):
                    textedit, indexlabel, cardname = self.card_slots[i][0:3]
                    card = textedit.text()
                    
                    if card.isnumeric():
                        card = int(card) & 0xFFF
                        deck_data.append(card)
                    else:
                        match = match_partly(card)

                        if isinstance(match, tuple) and match[0] is None:
                            self.statusbar.showMessage("No matching card found: '{0}'".format(card))
                            return
                        elif isinstance(match, tuple):
                            index, card = match

                            deck_data.append(index)
                        else:
                            if len(match) > 5:
                                self.statusbar.showMessage("Too many matches found ({0} matches)".format(len(match)))
                            else:
                                self.statusbar.showMessage("More than 1 match found: {0}".format(
                                    ", ".join("{0} ({1})".format(x[1], x[0]) for x in match)))
                            return

                if current.is_starter:
                    current.setText("[Starter] {0:>7} [rank:{1:>2}] {2}".format(leaderdata&0xFFF,
                                                                                rank, get_name(leaderdata & 0xFFF)))
                else:

                    current.setText("[CPU] {0:>7} [rank:{1:>2}] {2}".format(leaderdata&0xFFF,
                                                                            rank, get_name(leaderdata & 0xFFF)))

                self.leader_label.setText(get_name(leaderdata & 0xFFF))
                self.lineedit_leader.setText(str(leaderdata & 0xFFF))
                print(len(deck_data))
                
                for i in range(40):
                    card = deck_data[1+i]
                    textedit, indexlabel, cardname = self.card_slots[i][0:3]
                    textedit.setText(str(card))
                    cardname.setText(get_name(card))

                print(type(self.deck_data))
                struct.pack_into("H"*41, self.deck_data, current.number*41*2, *deck_data)
            except:
                traceback.print_exc()

    def button_load_decks(self):
        try:
            # implement
        except:
            # implement

    def action_listwidget_change_item(self, current, previous):
        try:
            if current is not None:
                print(current, current.number, current.deck_offset)
                leader = struct.unpack_from("H", self.deck_data, current.number*41*2)[0]
                rank = leader >> 12
                leader_card = leader & 0xFFF
                self.lineedit_leader.setText(str(leader_card))
                self.lineedit_leader_rank.setText(str(rank))
                self.leader_label.setText(get_name(leader_card))

                for i in range(40):
                    card = struct.unpack_from("H", self.deck_data, current.number*41*2 + 2 + i*2)[0] & 0xFFF
                    textedit, indexlabel, cardname = self.card_slots[i][0:3]
                    textedit.setText(str(card))
                    cardname.setText(get_name(card))
        except:
            traceback.print_exc()
            raise

    def button_save_decks(self):
        if self.deck_data is not None:
            filepath, chosentype = QFileDialog.getSaveFileName(
                self, "Save File",
                self.default_path,
                "PS2 iso (*.iso);;All files (*)")
            print(filepath, "saved")
            
            if filepath:
                with open(filepath, "r+b") as f:
                    f.seek(STARTER_DECK_OFFSET)
                    f.write(self.deck_data[0:17*41*2])
                    f.seek(CPU_DECK_OFFSET)
                    f.write(self.deck_data[17*41*2:17*41*2+24*41*2])
                    
                self.default_path = filepath
                set_default_path(filepath)
        else:
            pass # no level loaded, do nothing