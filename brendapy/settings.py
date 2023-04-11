# -*- coding: utf-8 -*-
"""
Paths to main resources and resource management.

Due to the size limits of git and pypi the large resources
cannot be managed/included in git and pypi.
These resources have to be loaded from online resources on
first import.

"""
import os


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH = os.getenv("BIOTA_BIODATA_DIR") or os.getenv("RESOURCES_PATH") or "/data/gws_biota/biodata/"
if not RESOURCES_PATH:
    raise Exception("Environment variable BIOTA_BIODATA_DIR is not set")

BRENDA_FILE = os.path.join(RESOURCES_PATH, "brenda", "brenda_download.txt")
TAXONOMY_DIR = os.path.join(RESOURCES_PATH, "ncbi", "taxdump")
TAXONOMY_DATA = os.path.join(TAXONOMY_DIR, "taxonomy.json")
BTO_DATA = os.path.join(RESOURCES_PATH, "bto", "bto.owl")
CHEBI_OBO_DATA = os.path.join(RESOURCES_PATH, "chebi", "chebi.obo")
CHEBI_JSON_DATA = os.path.join(RESOURCES_PATH, "chebi", "chebi.json")
