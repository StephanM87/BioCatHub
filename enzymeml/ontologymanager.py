import xlrd
import libsbml as sbml

IDENTIFIERS_ORG = "https://identifiers.org/"

IDENTIFIER_UNIPROT = "uniprot"
IDENTIFIER_PROTEIN_DATA_BANK = "pdb"
IDENTIFIER_GENE_ONTOLOGY = "go"
IDENTIFIER_TAXONOMY = "taxonomy"
IDENTIFIER_UNIT_ONTOLOGY = "uo"
IDENTIFIER_CHEMICAL_ENTITIES = "chebi"
IDENTIFIER_DIGITAL_OBJECT_IDENTIFIER = "doi"
IDENTIFIER_SYSTEM_BIOLOGY_ONTOLOGY = "sbo"

SBO_SUBSTRATE = 15
SBO_ENZYME = 14
SBO_PRODUCT = 11
SBO_INHIBITOR = 20
SBO_ACTIVATOR = 21
SBO_MODIFIER = 19
SBO_NEUTRAL_PARTICIPANT = 594
SBO_INTERACTOR = 336
SBO_METABOLITE = 299


# An identifier class to manage the different ontology identifiers
class Identifier:
    def __init__(self, ident, tags):
        self.identifier = ident

        if type(tags) is not list:
            raise RuntimeError("The tags parameter is not a list.")
        self.tags = tags

    def to_uri(self, obj):
        pass

    def is_allowed_tag(self, tag):
        return tag.lower() in self.tags


class NumberIdentifier(Identifier):
    def to_uri(self, obj):
        return IDENTIFIERS_ORG + "%s:%07d" % (self.identifier.upper(), obj)


class StringIdentifier(Identifier):
    def to_uri(self, obj):
        return IDENTIFIERS_ORG + "%s:%s" % (self.identifier.upper(), obj)


ontology_list = {
    IDENTIFIER_UNIPROT: StringIdentifier(IDENTIFIER_UNIPROT, [""]),
    IDENTIFIER_CHEMICAL_ENTITIES: NumberIdentifier(IDENTIFIER_CHEMICAL_ENTITIES, ["species"]),
    IDENTIFIER_DIGITAL_OBJECT_IDENTIFIER: StringIdentifier(IDENTIFIER_DIGITAL_OBJECT_IDENTIFIER, [""]),
    IDENTIFIER_GENE_ONTOLOGY: NumberIdentifier(IDENTIFIER_GENE_ONTOLOGY, ["compartment"]),
    IDENTIFIER_PROTEIN_DATA_BANK: StringIdentifier(IDENTIFIER_PROTEIN_DATA_BANK, [""]),
    IDENTIFIER_TAXONOMY: NumberIdentifier(IDENTIFIER_TAXONOMY, ["model", "compartment", "species"]),
    IDENTIFIER_UNIT_ONTOLOGY: NumberIdentifier(IDENTIFIER_UNIT_ONTOLOGY, ["unitDefenition"]),
    IDENTIFIER_SYSTEM_BIOLOGY_ONTOLOGY: NumberIdentifier(IDENTIFIER_SYSTEM_BIOLOGY_ONTOLOGY, ["reaction"])
}


class ListFilter(sbml.ElementFilter):
    def __init__(self):
        sbml.ElementFilter.__init__(self)

    def filter(self, element):
        if element is None:
            return False



# This class is used to easily handle the different ontologies to improve working with EnzymeML.
# As an input file the excel sheet can work, but a database would work as well.
class OntologyManager:
    def __init__(self, loader=None, location=None):
        self.ontologies = dict()

        if loader is not None and issubclass(type(loader), OntologyLoader):
            self.ontology_loader = loader
        elif loader is not None:
            print("The loader type '%s' is not a subclass of '%s' and cannot be used." % (type(loader), OntologyLoader))

        if location is not None:
            self.load_file(location)

    def load(self, location):
        if self.ontology_loader is not None:
            self.ontology_loader.load(self, location)
        else:
            print("No ontology manager has been applied to load '%s' from." % location)

    def add(self, ontology, name, code):
        if "identifier" not in code:
            raise RuntimeError("At least the 'identifier' has to be given as the 'code' attribute.")

        if ontology not in self.ontologies:
            self.ontologies[ontology] = dict()

        onto = self.ontologies[ontology]

        if name not in onto:
            onto[name] = code

    def get(self, ontology, name):
        if ontology not in self.ontologies:
            return None
        onto = self.ontologies[ontology]
        if name in onto:
            return onto[name]
        else:
            return None

    def get_uri(self, ontology, name):
        onto = self.get(ontology, name)
        ident = ontology_list[ontology]

        return ident.to_uri(onto["identifier"])

    def annotate(self, model):
        pass


# The loader class for the Ontology Manger
class OntologyLoader:
    # This method is used to load the data into the manager
    def load(self, manager, location):
        pass


# This class is used to load the Excel ontology template
class ExcelOntologyLoader(OntologyLoader):
    def __init__(self):
        pass

    def load(self, manager, location):
        wb = xlrd.open_workbook(location)

        for sheet in wb.sheets():
            format = list()
            for cell in sheet.row_values(0):
                format.append(cell.lower())

            if "name" not in format or "identifier" not in format:
                print("Could not find 'name' or 'identifier' in the excel file sheet '%s'" % sheet.name)
                continue

            namepos = format.index("name")
            for i in range(1, sheet.nrows):
                row = sheet.row_values(i)
                name = row[namepos]

                obj = dict()
                for j in range(0, len(format)):
                    if j != namepos:
                        obj[format[j]] = row[j]

                manager.add(sheet.name, name, obj)
