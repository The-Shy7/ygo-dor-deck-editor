import traceback
import re
from os import path

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QListWidgetItem

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