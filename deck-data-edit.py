import traceback
from os import path

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
    # implement

