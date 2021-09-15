# -*- coding: utf-8 -*-
import json
from brendapy.settings import CHEBI_DATA

def get_substances():
    with open(CHEBI_DATA, "r") as fin:
        CHEBI = json.load(fin)
    return CHEBI
    
# if __name__ == "__main__":
#     from pprint import pprint
#     print("Loading chebi information")
#     pprint(CHEBI["D-glucose"])
