# -*- coding: utf-8 -*-
from brendapy.settings import BTO_DATA
from pronto import Ontology


def get_bto():
    print("Loading tissue information")
    onto = Ontology(BTO_DATA)
    data = {}
    for term in onto.terms():
        if not term.name:
            continue
        data[term.name] = term.id

    return data

# if __name__ == "__main__":
#     print("Loading tissue information")
#     print(BTO["liver"])
