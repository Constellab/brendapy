# -*- coding: utf-8 -*-
"""
Paths to main resources and resource management.

Due to the size limits of git and pypi the large resources
cannot be managed/included in git and pypi.
These resources have to be loaded from online resources on
first import.

"""
import os
import logging
from zipfile import ZipFile


import requests
import shutil

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH = os.getenv("RESOURCES_PATH") or "/data/biota/biodata/"
if not RESOURCES_PATH:
    raise Exception("Environment variabe BIOTA_BIODATA_DIR is not set")
BRENDA_FILE = os.path.join(RESOURCES_PATH, "brenda", "brenda", "brenda_download.txt")
TAXONOMY_DATA = os.path.join(RESOURCES_PATH, "brenda", "taxonomy", "taxonomy.json")
TAXONOMY_ZIP = os.path.join(RESOURCES_PATH, "brenda", "taxonomy", "taxdump.zip")
BTO_DATA = os.path.join(RESOURCES_PATH, "brenda", "bto", "bto.json")
CHEBI_DATA = os.path.join(RESOURCES_PATH, "brenda", "chebi", "chebi.json")