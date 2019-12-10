import zipfile as zip
import xml.etree.ElementTree as ET


class FileType:
    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier


COMBINE_SBML = FileType("SBML", "")
COMBINE_ENZYMEML = FileType("EnzymeML", "")
COMBINE_XML = FileType("XML", "")
COMBINE_CSV = FileType("CSV", "")
COMBINE_OMEX_MANIFEST = FileType("OMEX - Manifest", "")

NS_OMEX = "http://identifiers.org/combine.specifications/omex-manifest"


class OMEXManifest:
    def __init__(self, *args):
        if len(args) == 1:
            root = args[0].getroot()
            ns = {"omex": NS_OMEX}
            masters = root.findall("omex:content@[master='true']", ns)
            if len(masters) > 1:
                self.master = []
                for master in masters:
                    self.master.append(OMEXManifest.__read_content(master))
            elif len(masters) == 1:
                self.master = OMEXManifest.__read_content(masters[0])
            else:
                self.master = None

            content = root.findall("omex:content", ns)
            self.content = []
            for c in content:
                if not ("master" in c.attrib and c.attrib["master"] == "true"):
                    self.content.append(OMEXManifest.__read_content(c))
        else:
            self.master = None
            self.content = []

    def getmaster(self):
        return self.master

    def addcontent(self, location, form):
        self.content.append((location, form))

    def removecontent(self, location):
        for c in range(0, len(self.content)):
            if self.content[c][0] == location:
                del self.content[location]
                return True
        return False

    def addmaster(self, location, form):
        if type(self.master) == list:
            self.master.append((location, form))
        elif self.master is None:
            self.master = (location, form)
        else:
            master = self.master
            self.master = [master, (location, form)]

    def removemaster(self, location):
        if type(self.master) == list:
            found = False
            for m in self.master:
                if m[0] == location:
                    self.master.remove(m)
                    found = True
                    break
            if found and len(found) == 1:
                self.master = self.master[0]

            return found
        elif self.master is None:
            return False
        else:
            if self.master[0] == location:
                self.master = None
                return True
            else:
                return False

    def hasmaster(self, location):
        if type(self.master) == list:
            for m in self.master:
                if m[0] == location:
                    return True
            return False
        elif self.master is not None:
            return self.master[0] == location
        else:
            return False

    def has(self, location):
        if self.hasmaster(location):
            return True

        for c in self.content:
            if c[0] == location:
                return True
        return False

    @staticmethod
    def __read_content(content):
        return content.attrib["location"], content.attrib["format"]

    @staticmethod
    def from_string(string):
        tree = ET.fromstring(string)
        return OMEXManifest(tree)


class CombineFile:
    class File:
        def __init__(self, name, filetype, obj):
            if issubclass(type(filetype), FileType):
                raise ValueError("clazz is not a FileType.")

            self.name = name
            self.type = filetype
            self.content = obj

    class Folder:
        def __init__(self, name):
            self.name = name
            self.content = []

        def add(self, obj):
            self.content.append(obj)

    def __init__(self):
        self.manifest = OMEXManifest()
        self.files = []

    def update(self, cont=None, path=""):
        if cont is None:
            cont = self.files

        for f in cont:
            if type(f) == CombineFile.File:
                pass
            elif type(f) == CombineFile.Folder:
                self.update(f.content, "%s/%s" % (path, f.name))

    def create_folder(self, name):
        folder = CombineFile.Folder(name)
        self.files.append(folder)

    @staticmethod
    def load_from_file(self, name):
        return 1
