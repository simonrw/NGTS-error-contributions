# -*- coding: utf-8 -*-

import tables
from srw.TablesParser import TablesParser
import os
import re

SpecTypes = {
        1: "O",
        2: "B",
        3: "A",
        4: "F",
        5: "G",
        6: "K",
        7: "M",
        8: "C",
        9: "DA",
        }

SpecClass = {
        1: "Supergiant",
        2: "Bright giant",
        3: "Giant",
        4: "Subgiant",
        5: "Main sequence",
        6: "White Dwarf",
        7: "T Tauri",
        }


class BesanconParser(TablesParser):
    '''
    Parser class for the Besancon
    data set
    '''
    def __init__(self):
        '''
        Create the database object and
        initialise
        '''
        super(BesanconParser, self).__init__(os.path.join(
            os.path.dirname(__file__),
            "BesanconDatabase.h5")
            )

    def get_coordinates(self, field_id):
        table = self.getTable('/fields', 'field{:d}'.format(field_id))
        header = table.attrs.header
        line = header.split('\n')[8]

        match = re.search(r'\(l\s*=\s*(?P<l>[0-9.]+);'
        '\s*b\s*=\s*(?P<b>[-0-9.]+)'
        '.*Solid angle\s+(?P<angle>[0-9.]+)', line)
        if match:
            return [float(match.group(key)) for key in ['l', 'b', 'angle']]
        else:
            raise RuntimeError("Cannot parse header information")







