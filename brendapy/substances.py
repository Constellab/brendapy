# -*- coding: utf-8 -*-
import os
import json
from brendapy.settings import Settings
from pronto import Ontology


def get_substances():
    print("Loading chebi information. This may take a while ...")

    settings = Settings()
    if not os.path.exists(settings.CHEBI_JSON_DATA):
        onto = Ontology(settings.CHEBI_OBO_DATA)
        data = {}
        for term in onto.terms():
            if not term.name:
                continue
            data[term.name] = term.id

        with open(settings.CHEBI_JSON_DATA, "w", encoding="utf-8") as fp:
            json.dump(data, fp)

        return data
    else:
        with open(settings.CHEBI_JSON_DATA, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return data
