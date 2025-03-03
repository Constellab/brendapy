# -*- coding: utf-8 -*-
"""
Module for parsing the BRENDA ENZYME information from flat file.
The following information is available:

    AC    activating compound
    AP    application
    CF    cofactor
    CL    cloned
    CR    crystallization
    EN    engineering
    EXP    expression
    GI    general information on enzyme
    GS    general stability
    IC50    IC-50 Value
    ID    EC-class
    IN    inhibitors
    KKM    Kcat/KM-Value substrate in {...}
    KI    Ki-value    inhibitor in {...}
    KM    KM-value    substrate in {...}
    LO    localization
    ME    metals/ions
    MW    molecular weight
    NSP    natural substrates/products    reversibilty information in {...}
    OS    oxygen stability
    OSS    organic solvent stability
    PHO    pH-optimum
    PHR    pH-range
    PHS    pH stability
    PI    isoelectric point
    PM    posttranslation modification
    PR    protein
    PU    purification
    RE    reaction catalyzed
    RF    references
    REN    renatured
    RN    accepted name (IUPAC)
    RT    reaction type
    SA    specific activity
    SN    synonyms
    SP    substrates/products    reversibilty information in {...}
    SS    storage stability
    ST    source/tissue
    SU    subunits
    SY    systematic name
    TN    turnover number    substrate in {...}
    TO    temperature optimum
    TR    temperature range
    TS    temperature stability
"""
import os
import re
import logging
from collections import OrderedDict, defaultdict
from pprint import pprint

from brendapy import utils
from brendapy.taxonomy import Taxonomy
from brendapy.tissues import get_bto
from brendapy.substances import get_substances

# TAXONOMY = Taxonomy()

deprecated_id_re = re.compile("EC\s+(\d+\.\d+\.\d+\.\d+)")


class BrendaParser(object):
    """ Parser for BRENDA information.

    The parser reads the BRENDA flat file into the
    parts for the ec numbers. Via the BrendaParser the
    information for the ec numbers can be accesses.
    """

    BRENDA_KEYS = [
        "AC", "AP", "CF", "CL", "CR", "EN", "EXP", "GI", "GS", "IC50",
        "ID", "IN", "KKM", "KI", "KM", "LO", "ME", "MW", "NSP", "OS",
        "OSS", "PHO", "PHR", "PHS", "PI", "PM", "PR", "PU", "RE", "RF",
        "REN", "RN", "RT", "SA", "SN", "SP", "SS", "ST", "SU", "SY", "TN",
        "TO", "TR", "TS"
    ]

    # Gencovery: replace PATTERN_ORGANISM
    # PATTERN_RF = re.compile(r"^<(\d+?)> (.+) {Pubmed:\s*(\d*)\s*}")
    # PATTERN_ALL = re.compile(r"^#([,\d\s]+?)#(.+)<([,\d\s]+)>")
    # PATTERN_VALUE = re.compile(r"^([\d\.]+)\s+\{(.+)\}")

    PATTERN_RF = re.compile(r"^<(\d+?)> (.+) {Pubmed:\s*(\d*)\s*}")
    PATTERN_ALL = re.compile(r"^#([,\d\s]+?)#(.+)<([,\d\s]+)>")
    PATTERN_VALUE = re.compile(r"^([\d\.\-]+)\s+\{(.+)\}")

    UNITS = {
        "KM": "mM",
        "KI": "mM",
        "TN": "1/s",
        "IC50": "mM",
        "KKM": "1/mM/s",
        "SA": "µmol/min/mg"
    }
    CHEBI = None

    def __init__(self, brenda_file):
        """ Initialize parser and parse BRENDA file.

        :param brenda_file: BRENDA text file
        """
        self.brenda_file = brenda_file
        self.ec_text = BrendaParser.parse_entry_strings(self.brenda_file)
        self.ec_data = OrderedDict()  # only parse on demand

    def keys(self):
        """ Available ec keys.

        Information for these EC numbers is available in the
        parser object.

        :return: list of ec numbers
        """
        return self.ec_text.keys()

    @staticmethod
    def parse_entry_strings(filename):
        """ Reads the string entries from BRENDA file.

        :param filename: BRENDA database download
        :return: dict (ec, brenda_info)
        """
        logging.info(f"`parse_entry_strings` from `{filename}`")
        ec_data = OrderedDict()

        in_entry = False
        data_lines = []

        # read BRENDA file
        with open(filename, 'r', encoding="utf-8") as bf:
            for line in bf.readlines():
                if line.startswith("*") or len(line) == 0:
                    continue

                # start of entry
                if line.startswith("ID\t"):
                    in_entry = True
                    ec = BrendaParser._get_ec_from_line(line)
                    data_lines = [line]
                # in entry
                if in_entry:
                    data_lines.append(line)
                # end of entry
                if in_entry and line.startswith("///"):
                    in_entry = False
                    entry = "".join(data_lines)
                    entry.replace('\xef\xbf\xbd', " ")
                    # store entry
                    ec_data[ec] = entry
                    data_lines = []

        return ec_data

    @utils.timeit
    def parse_info_dicts(self):
        """ Parses all info dicts.

        This takes around ~15s and prepares all proteins.
        """
        d = OrderedDict()
        for ec, ec_string in self.ec_text.items():
            d[ec] = BrendaParser._parse_info_dict(ec, ec_string)
        return d

    @staticmethod
    def _parse_info_dict(ec, ec_str):
        """
        :return:
        """
        def parse_bid_item(line):
            tokens = line.split("\t")
            bid = tokens[0].strip()
            item = "\t".join(tokens[1:])
            return bid, item

        # parse entries from lines
        bid_sets = defaultdict(set)  # sets to remove duplicate entries
        in_item = False

        for line in ec_str.split("\n"):
            if not in_item:
                if len(line) > 0 and not line.startswith("\t"):
                    bid, item = parse_bid_item(line)
                    if bid in BrendaParser.BRENDA_KEYS:
                        in_item = True
                    else:
                        in_item = False
                        item = None

            elif in_item:
                # entries longer than one line
                if line.startswith("\t"):
                    item += " " + line.strip()

                # write entries if next entry begins
                elif len(line) > 0 and not line.startswith("\t"):
                    # store old entry
                    bid_sets[bid].add(item)
                    in_item = False

                    # create new entry
                    bid, item = parse_bid_item(line)
                    if bid in BrendaParser.BRENDA_KEYS:
                        in_item = True
                    else:
                        # logging.error(f"{ec}_{bid}: BRENDA key not supported in line: `{line}`")
                        item = None

                # store last entry
                elif len(line) == 0:
                    bid_sets[bid].add(item)
                    in_item = False

        # transfer the unique entries into results
        results = defaultdict(OrderedDict)
        for key, items in bid_sets.items():
            for item in sorted(items):  # sorting for reproducible order (in unittests)
                BrendaParser._store_item(results=results, bid=key, item=item, ec=ec)

        return results

    @classmethod
    def _store_item(cls, results, bid, item, ec=None):
        """ Store parsed item for bid.

        :param bid:
        :param item:
        :return:
        """

        if not cls.CHEBI:
            cls.CHEBI = get_substances()

        if bid == "ID":
            results[bid] = item
        elif bid in {"RN", "RE", "RT", "SN"}:
            if isinstance(results[bid], OrderedDict):
                results[bid] = {item}
            else:
                results[bid].add(item)
        elif bid == "RF":
            match = BrendaParser.PATTERN_RF.match(item)
            if match:
                rid, info, pubmed = match.group(1), match.group(2), match.group(3)
                rid = int(rid)  # integer keys for all references
                results[bid][rid] = {
                    'info': info,
                }
                if pubmed and len(pubmed) > 0:
                    pubmed = int(pubmed)  # integer keys for all pubmeds
                    results[bid][rid]['pubmed'] = pubmed
            else:
                # logging.error(f"Reference could not be parsed: `{item}`")
                pass
        # everything else
        else:
            match = BrendaParser.PATTERN_ALL.match(item)
            if match:
                ids, data_all, refs = match.group(1), match.group(2), match.group(3)
                ids = ids.replace(' ', ",")  # fix the missing comma in ids
                ids = [int(token) for token in ids.split(',')]
                refs = refs.replace(' ', ",")  # fix the missing comma in refs

                # get additional information
                comment = None

                tokens = data_all.split('(#')
                if len(tokens) == 1:
                    data = tokens[0]
                elif len(tokens) == 2:
                    data = tokens[0].strip()
                    comment = "(#" + tokens[1].strip()
                    comment = comment[1:-1]
                else:
                    # logging.error(f"comment could not be parsed: '{data_all}'")
                    pass

                # check data
                if len(data) == 0:
                    # logging.warning(f"{ec}_{bid}: empty information not stored: '{data_all}'")
                    pass
                elif data == "more":
                    # logging.info(f"{ec}_{bid}: 'more' data not stored: {data_all}")
                    return

                # store info as dict
                info = {
                    'data': data.strip(),
                    'refs': [int(token) for token in refs.split(',')]
                }
                if comment:
                    info['comment'] = comment

                if bid in BrendaParser.UNITS:
                    info["units"] = BrendaParser.UNITS[bid]
                    if data.startswith("-999"):
                        # parse value
                        # logging.info(f"{ec}_{bid}: '-999' values not parsed: {data}")
                        pass
                    else:
                        match_s = BrendaParser.PATTERN_VALUE.match(info["data"])
                        if match_s:
                            # info['value'] = float(match_s.group(1))
                            info['value'] = match_s.group(1)

                            substrate = match_s.group(2)

                            info['substrate'] = substrate
                            if substrate in cls.CHEBI:
                                info['chebi'] = cls.CHEBI[substrate]
                            else:
                                # logging.info(f"Substrate could not be found in CHEBI: '{substrate}'")
                                pass
                        else:
                            # trying the simple patterns without substrate
                            try:
                                # info['value'] = float(info["data"])
                                info['value'] = info["data"]
                            except:
                                # logging.error(f"data could not be converted to float: {info['data']}")
                                pass

                for pid in ids:
                    if bid == "PR":
                        results[bid][pid] = info
                    else:
                        if pid in results[bid]:
                            results[bid][pid].append(info)
                        else:
                            results[bid][pid] = [info]
            else:
                if bid == "SY" and item[0] != '#':
                    # logging.info(f"{ec}_{bid}: generic synonyms are not stored: {item}")
                    pass
                else:
                    # logging.error(f"{ec}_{bid}: could not be parsed: `{item}`")
                    pass

    @staticmethod
    def _get_ec_from_line(line):
        ec = line.strip().split("\t")[1].strip()
        ec = ec.split(" ")[0]
        if utils.is_ec_number(ec):
            return ec
        else:
            return None

    def get_proteins(self, ec):
        """ Parses all BRENDA proteins for given EC number.

        :param ec:
        :return: OrderedDict of BRENDA proteins
        """
        # process text data for ec if not already existing
        if ec not in self.ec_data:
            self.ec_data[ec] = BrendaParser._parse_info_dict(ec, ec_str=self.ec_text[ec])

        ec_data = self.ec_data[ec]
        proteins = {}

        is_deprecated_ec = not ec_data['PR']
        if is_deprecated_ec:
            pass
        else:
            for key in ec_data['PR'].keys():
                proteins[key] = BrendaProtein(ec=ec, key=key, data=ec_data)

        return proteins

    def get_all_proteins(self, ec):
        """ Parses all BRENDA proteins for given EC number.

        :param ec:
        :return: OrderedDict of BRENDA proteins
        """
        # process text data for ec if not already existing
        if ec not in self.ec_data:
            self.ec_data[ec] = BrendaParser._parse_info_dict(ec, ec_str=self.ec_text[ec])

        ec_data = self.ec_data[ec]
        deprecated_ec = {}
        proteins = {}

        def is_deprecated(_id):
            return ("transferred" in _id) or ("deleted" in _id)

        _id = ec_data['ID']
        if is_deprecated(_id):
            deprecated_ec = {
                "old_ec": ec,
                "new_ec": [],
                "data": {
                    'ID': str(_id),
                    'RN': str(ec_data.get("RN", "")),
                    "reason": "",
                }
            }

            new_ec = deprecated_id_re.findall(_id)
            for n_ec in new_ec:
                deprecated_ec["new_ec"].append(n_ec)

            if "transferred" in _id:
                deprecated_ec["data"]["reason"] = "transferred"

            if "deleted" in _id:
                deprecated_ec["data"]["reason"] = "deleted"

        else:
            for key in ec_data['PR'].keys():
                proteins[key] = BrendaProtein(ec=ec, key=key, data=ec_data)

        return proteins, deprecated_ec


class BrendaProtein(object):
    """ Stores BRENDA information for a protein entry.

    Every protein belongs to a single EC number. For a single
    EC number multiple proteins exist corresponding to different
    species (and sometimes different isoforms).

    This class provides helper properties which allows to access
    the data based on the BRENDA keys in the flat file.
    """
    # Gencovery: replace PATTERN_ORGANISM
    # PATTERN_ORGANISM = re.compile(r"^(\w+)\s([\w\.]+)")
    PATTERN_ORGANISM = re.compile(r"^([a-zA-Z0-9\-]+)\s([\w\.]+)")
    PATTERN_UNIPROT = re.compile(
        r"([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?")
    BTO = None

    def __init__(self, ec, key, data):
        """ Construct protein object.

        :param ec: EC number
        :param key: integer protein key (BRENDA key for protein)
        :param data: data dictionary for the complete ec number
        """
        # BTO
        cls = type(self)
        if not cls.BTO:
            cls.BTO = get_bto()

        protein_info = data['PR'][key]['data']

        # organism
        match_organism = BrendaProtein.PATTERN_ORGANISM.match(protein_info)
        if match_organism:
            organism = f"{match_organism.group(1)} {match_organism.group(2)}"
        else:
            organism = protein_info
            # logging.warning(f"Organism could not be parsed from: '{protein_info}'")

        # taxonomy
        t = Taxonomy()
        taxonomy = t.get_taxonomy_id(organism)

        # uniprot
        uniprot = None
        for token in protein_info.split(" "):
            match_uniprot = BrendaProtein.PATTERN_UNIPROT.match(token)
            if match_uniprot:
                uniprot = token
                break

        self.data = OrderedDict([
            ('protein_id', key),
            ('ec', ec),
            ('organism', organism),
            ('taxonomy', taxonomy),
            ('uniprot', uniprot),
        ])
        reference_ids = set(data['PR'][key]['refs'])

        # add all fields
        for bid in BrendaParser.BRENDA_KEYS:

            if bid in {"ID", "RN", "RE", "RT", "SN"}:
                # ec number, ec sets (ec data set for all proteins)
                self.data[bid] = data[bid]
                continue
            elif bid in {"PR", "RF"}:
                # not set as local protein fields
                continue
            else:
                info = data[bid].get(key, None)
                if info:
                    self.data[bid] = info
                    # for the list items collect additional references
                    if isinstance(info, (list, )):
                        for item in info:
                            # collect additional references
                            reference_ids.update(item['refs'])

        self.data['references'] = {ref_id: data['RF'].get(ref_id, {}) for ref_id in reference_ids}

        # map tissues on Brenda Tissue Ontology
        tissues = set()
        cls = type(self)
        if self.ST:
            for item in self.ST:
                tissue = item['data']
                bto = cls.BTO.get(tissue, None)
                if bto:
                    item['bto'] = bto
                    tissues.add(bto)
                else:
                    # logging.error(f"Source/Tissue not found in Brenda Tissue Ontology (BTO): '{tissue}'")
                    pass
        self.data["tissues"] = tissues

    @property
    def protein_id(self):
        """"BRENDA Protein id.

        This is the integer used in the BRENDA flatfile to
        map to individual protein entries.

        :return: int protein id
        """
        return self.data['protein_id']

    @property
    def ec(self):
        return self.data['ec']

    @property
    def organism(self):
        return self.data['organism']

    @property
    def taxonomy(self):
        """ NCBI Taxonomy id

        :return: NCBI taxonomy id, None if organism could not be mapped
        """
        return self.data['taxonomy']

    @property
    def uniprot(self):
        """ UniProt/SwissProt id.

        :return: uniprot id, None if no information available for protein entry
        """
        return self.data['uniprot']

    @property
    def tissues(self):
        """ BRENDA Tissue Ontology (BTO) tissue ids
        :return: set of bto terms, empty set if no bto terms exist
        """
        return self.data['tissues']

    @property
    def references(self):
        return self.data['references']

    def __str__(self):
        """String representation. """
        from pprint import pformat
        return pformat(self.data)

    @property
    def AC(self):
        """activating compound
        :return: list, None if no data exists
        """
        return self.data.get("AC", None)

    @property
    def AP(self):
        """application"""
        return self.data.get("AP", None)

    @property
    def CF(self):
        """cofactor"""
        return self.data.get("CF", None)

    @property
    def CL(self):
        """cloned"""
        return self.data.get("CL", None)

    @property
    def CR(self):
        """crystallization"""
        return self.data.get("CR", None)

    @property
    def EN(self):
        """engineering"""
        return self.data.get("EN", None)

    @property
    def EXP(self):
        """expression"""
        return self.data.get("EXP", None)

    @property
    def GI(self):
        """general information on enzyme"""
        return self.data.get("GI", None)

    @property
    def GS(self):
        """general stability"""
        return self.data.get("GS", None)

    @property
    def IC50(self):
        """IC-50 Value"""
        return self.data.get("IC50", None)

    @property
    def ID(self):
        """EC-class"""
        return self.data.get("ID", None)

    @property
    def IN(self):
        """inhibitors"""
        return self.data.get("IN", None)

    @property
    def KKM(self):
        """Kcat/KM-Value substrate in {...}"""
        return self.data.get("KKM", None)

    @property
    def KI(self):
        """Ki-value inhibitor in {...}"""
        return self.data.get("KI", None)

    @property
    def KM(self):
        """KM-value substrate in {...}"""
        return self.data.get("KM", None)

    @property
    def LO(self):
        """localization"""
        return self.data.get("LO", None)

    @property
    def ME(self):
        """metals/ions"""
        return self.data.get("ME", None)

    @property
    def MW(self):
        """molecular weight"""
        return self.data.get("MW", None)

    @property
    def NSP(self):
        """natural substrates/products reversibilty information in {...}"""
        return self.data.get("NSP", None)

    @property
    def OS(self):
        """oxygen stability"""
        return self.data.get("OS", None)

    @property
    def OSS(self):
        """organic solvent stability"""
        return self.data.get("OSS", None)

    @property
    def PHO(self):
        """pH-optimum"""
        return self.data.get("PHO", None)

    @property
    def PHR(self):
        """pH-range"""
        return self.data.get("PHR", None)

    @property
    def PHS(self):
        """pH stability"""
        return self.data.get("PHS", None)

    @property
    def PI(self):
        """isoelectric point"""
        return self.data.get("PI", None)

    @property
    def PM(self):
        """posttranslation modification"""
        return self.data.get("PM", None)

    @property
    def PU(self):
        """purification"""
        return self.data.get("PU", None)

    @property
    def RE(self):
        """reaction catalyzed"""
        return self.data.get("RE", None)

    @property
    def REN(self):
        """renatured"""
        return self.data.get("REN", None)

    @property
    def RN(self):
        """accepted name (IUPAC)"""
        return self.data.get("RN", None)

    @property
    def RT(self):
        """reaction type"""
        return self.data.get("RT", None)

    @property
    def SA(self):
        """specific activity"""
        return self.data.get("SA", None)

    @property
    def SN(self):
        """synonyms"""
        return self.data.get("SN", None)

    @property
    def SP(self):
        """substrates/products    reversibilty information in {...}"""
        return self.data.get("SP", None)

    @property
    def SS(self):
        """storage stability"""
        return self.data.get("SS", None)

    @property
    def SS(self):
        """storage stability"""
        return self.data.get("SS", None)

    @property
    def ST(self):
        """source/tissue"""
        return self.data.get("ST", None)

    @property
    def SU(self):
        """subunits"""
        return self.data.get("SU", None)

    @property
    def SY(self):
        """systematic name"""
        return self.data.get("SY", None)

    @property
    def TN(self):
        """turnover number    substrate in {...}"""
        return self.data.get("TN", None)

    @property
    def TO(self):
        """temperature optimum"""
        return self.data.get("TO", None)

    @property
    def TR(self):
        """temperature range"""
        return self.data.get("TR", None)

    @property
    def TS(self):
        """temperature stability"""
        return self.data.get("TS", None)
