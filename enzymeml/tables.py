
class Table:
    def __init__(self):
        pass


class ColumnDependentTable:
    class Entry:
        def __init__(self, dependent):
            self.dependent = dependent
            self.values = dict()

        def set(self, col, value):
            self.values[col] = value

        def __getitem__(self, item):
            if item in self.values:
                return self.values[item]
            else:
                return None

    def __init__(self, dependent):
        self.dependent = dict()
        self.columns = list()
        self.columns.append(dependent)

    def add(self, dependentvalue, col, value):
        if col not in self.columns:
            raise RuntimeError("Unknown Column (%s) is not initialized." % col)
        if dependentvalue not in self.dependent:
            self.dependent[dependentvalue] = ColumnDependentTable.Entry(dependentvalue)
            self.dependent[dependentvalue].set(self.columns[0], dependentvalue)
        dependent = self.dependent[dependentvalue]
        dependent.set(col, value)

    def init_column(self, name):
        self.columns.append(name)

    def ncolumns(self):
        return len(self.columns)

    def nrows(self):
        return len(self.dependent.keys())

    def keys(self):
        return sorted(self.dependent.keys())

    def as_columns(self):
        cols = list()

        for scol in self.columns:
            col = list()
            for k in self.keys():
                col.append(self.dependent[k][scol])

            cols.append(col)

        return cols

    # Return a row of the items
    def __getitem__(self, item):
        li = list()

        dep = self.dependent[item]

        for col in self.columns:
            li.append(dep[col])

        return li

    def __len__(self):
        return len(self.dependent) * self.columns

