# -*- coding: utf-8 -*-
"""
Paths to main resources and resource management.

Due to the size limits of git and pypi the large resources
cannot be managed/included in git and pypi.
These resources have to be loaded from online resources on
first import.

The source data structure:
---+ BRENDAPY_DATA_DIR
   |---+ brenda/
   |   |--- brenda_download.txt
   |---+ ncbi/
   |   |---+ taxdump/
   |   |--- ...(unzipped *.dmp files) ...
   |---+ bto
   |   |--- bto.owl
   |---+ chebi
   |   |--- chebi.obo

"""
import os


class Settings:

    BRENDA_FILE = None
    TAXONOMY_DIR = None
    TAXONOMY_DATA = None
    BTO_DATA = None
    CHEBI_OBO_DATA = None
    CHEBI_JSON_DATA = None

    def __init__(self):
        if self.BRENDA_FILE is None:
            raise Exception("The variable BRENDAPY_DATA_DIR is not set")

        # self.BRENDA_FILE = os.path.join(self.BRENDAPY_DATA_DIR, "brenda", "brenda_download.txt")
        # self.TAXONOMY_DIR = os.path.join(self.BRENDAPY_DATA_DIR, "ncbi", "taxdump")
        # self.TAXONOMY_DATA = os.path.join(self.TAXONOMY_DIR, "taxonomy.json")
        # self.BTO_DATA = os.path.join(self.BRENDAPY_DATA_DIR, "bto", "bto.owl")
        # self.CHEBI_OBO_DATA = os.path.join(self.BRENDAPY_DATA_DIR, "chebi", "chebi.obo")
        # self.CHEBI_JSON_DATA = os.path.join(self.BRENDAPY_DATA_DIR, "chebi", "chebi.json")

    @classmethod
    def initialize_data_dir(cls, *, brenda_file=None, taxonomy_dir=None, bto_file=None, chebi_file=None):
        assert isinstance(brenda_file, str) and len(brenda_file) != 0, "brenda_file is required"
        assert isinstance(taxonomy_dir, str) and len(taxonomy_dir) != 0, "taxonomy_dir is required"
        assert isinstance(bto_file, str) and len(bto_file) != 0, "bto_file is required"
        assert isinstance(chebi_file, str) and len(chebi_file) != 0, "chebi_file is required"

        cls.BRENDA_FILE = brenda_file
        cls.TAXONOMY_DIR = taxonomy_dir
        cls.BTO_DATA = bto_file
        cls.CHEBI_OBO_DATA = chebi_file

        cls.TAXONOMY_DATA = os.path.join(cls.TAXONOMY_DIR, "taxonomy.json")
        cls.CHEBI_JSON_DATA = os.path.join(os.path.dirname(cls.CHEBI_OBO_DATA), "chebi.json")
