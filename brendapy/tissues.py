# -*- coding: utf-8 -*-
import json
from brendapy.settings import BTO_DATA

def get_bto():
    with open(BTO_DATA, "r") as fin:
        BTO = json.load(fin)
    return BTO

# if __name__ == "__main__":
#     print("Loading tissue information")
#     print(BTO["liver"])
