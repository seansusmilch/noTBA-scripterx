from sqlitedict import SqliteDict
import json
from beautifultable import BeautifulTable
from os import get_terminal_size

class theSqliteDict(SqliteDict):
    # def __init__(self, path, tablename='unnamed', autocommit=True):
    #     self.db = SqliteDict(path, tablename=tablename, autocommit=autocommit)
        
    def _insert(self, obj:dict):
        """Inserts a new document

        Args:
            obj (dict): Dict to be inserted

        Returns:
            int: id/key of the newly inserted doc
        """
        k = self._new_key()
        print(k)
        self[k] = obj
        return k

    def _check_key(self, key):
        if isinstance(key, str):
            try:
                int(key)
            except ValueError:
                raise ValueError(f'Key is invalid. Make sure it is an int')

    def _set(self, key:str or int, value:dict):
        self._check_key
        self[str(key)] = value

    def _new_key(self):
        """Internal method for generating a key for the next doc

        Returns:
            int: id/key for next doc
        """
        keys = list(self.keys())
        if not keys:
            return 0
        keys.sort(key=int)
        print(keys)
        return int(keys[-1])+1

    def _all(self):
        """Get all docs in table

        Returns:
            iterable: iterable of values in table
        """
        values = []
        for doc_id, val in self.items():
            val = dict(val)
            val.update({'doc_id': doc_id})
            values.append(val)
        return values

    def __str__(self):
        out = {}
        for key, value in self.items():
            out.update({key:value})
        return json.dumps(out, indent=4, separators=(',', ': '))

    def _where(self, key, comp, val):
        """A simple query over the table.

        Args:
            key (str) : key of the value to be compared
            comp (str) : comparison operator (==)
            val (str) : value to be compared

        Returns:
            list: a list of matches
        """

        if not type(key)==str or not type(comp)==str:
            raise ValueError("Where should be tuple in the form of (str,str,any)")

        matches = []
        if comp == '==':
            for doc_id, value in self.items():
                value = dict(value)
                if value.get(key) == val:
                    matches.append((doc_id,value))
            return matches

        raise ValueError(f"Your comparison operator ({comp}) is either invalid or not implemented yet")

    def _contains(self, where=tuple):
        return bool(self._where(*where))

    def _remove(self, where:tuple):
        """Remove all docs that meet the conditions of <where>

        Args:
            where (tuple): parameter list for where method. see where method for more info
        """
        toremove = self._where(*where)
        print(toremove)
        for doc_id, _ in toremove:
            self.__delitem__(doc_id)

    def _remove(self, doc_id:str or int):
        self.__delitem__(doc_id)

    def _update(self, val, where:tuple):
        """Update values in docs that meet the conditions of <where>

        Args:
            val (dict): a dict of values to update
            where (tuple): parameter list for where method. see where method for more info
        """
        toupdate = self._where(*where)
        print(toupdate)
        for doc_id, value in toupdate:
            value = dict(value)
            value.update(val)
            self[doc_id] = value
    
    def _update(self, val:dict, doc_id:str):
        doc = dict(self[doc_id])
        doc.update(val)
        self[doc_id] = doc

    def _contains(self, doc_id):
        self._check_key(doc_id)
        return str(doc_id) in self

    def print_table(self):
        """Generates a nice table of the database
        """
        term_size = get_terminal_size().columns
        # term_size = 155

        tbl = BeautifulTable(
            maxwidth=term_size if term_size > 80 else 80, 
            default_alignment=BeautifulTable.ALIGN_LEFT
            )
        tbl.columns.header = ['id', 'series', 'last_title', 'checked_since', 'needs\ntitle', 'needs\nthumb']
        for val in self.values():
            values = list(val.values())
            row = values[0:4]

            # trims values to make it fit without making a new line in a cell
            # row[:] = (elem[:int(term_size/2.9 - 3)] + '...' if len(elem) > int(term_size/2.9 - 3) else elem for elem in row)

            row.append('Y' if val['needs_title'] else '')
            row.append('Y' if val['needs_thumb'] else '')

            tbl.rows.append(row)

        tbl.rows.sort('last_title')
        tbl.rows.sort('series')
        tbl.set_style(BeautifulTable.STYLE_COMPACT)
        print(tbl)


if __name__ == '__main__':
    from helpers import get_db
    db = get_db()
    # print(db)
    db.print_table()