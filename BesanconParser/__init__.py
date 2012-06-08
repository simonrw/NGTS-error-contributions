# -*- coding: utf-8 -*-

import tables
import os.path

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


class BesanconParser(object):
    '''
    Parser class for the Besancon
    data set
    '''
    filename = os.path.join(
            os.path.dirname(__file__),
            "BesanconDatabase.pytables"
            )

    def __init__(self):
        '''
        Create the database object and
        initialise
        '''
        super(BesanconParser, self).__init__()

        # Try and find the data path
        try:
            self.tab = tables.openFile(self.filename, 'r')
        except IOError:
            self.filename = os.path.expanduser(
                    os.path.join(
                        '~', 'work', 'NGTS', 'GalaxyData',
                        'BesanconDatabase.pytables'))
            self.tab = tables.openFile(self.filename, 'r')


    def close(self):
        '''
        Close the database object
        '''
        self.tab.close()

    def getNode(self, path, nodename=None):
        '''
        Returns a node of the database
        '''
        if nodename:
            return self.tab.getNode(path, nodename)
        else:
            return self.tab.getNode(path)

    def getTable(self, path, tablename):
        '''
        Returns a table object

        If the requested node is not a table then raise
        an exception
        '''
        node = self.getNode(path, tablename)

        if type(node) == tables.table.Table:
            return node
        else:
            raise RuntimeError("Requested node is not a table")

