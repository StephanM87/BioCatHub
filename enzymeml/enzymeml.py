import libsbml as sbml
import libcombine as combine
import enzymeml.enzymemlkey as key
import xml.etree.ElementTree as ET
from datetime import datetime as time
import enzymeml.ontologymanager as ontology
import traceback
import decimal
import os, shutil

DEBUG = True


def namespace():
    return "http://sbml.org/enzymeml/version1"


_interpreter_dict = {
    "protein": None,
    "species": None
}


class UnknownEnzymeMLKeyException(Exception):
    """
    This error occurs, if an unknown key is used to add something to an EnzymeML file
    ekey -  the processed enzymeml key
    """
    def __init__(self, ekey):
        super(UnknownEnzymeMLKeyException, self).__init__(
            "The enzymemlkey is not set right: Please inform the EnzymeML staff if this error occured while using"
            + " the 'enzymemlkey.py'. (%s)" % ekey
        )
        self.ekey = ekey


ET.register_namespace("enzymeml", namespace())


def _create_base_element(tag):
    return ET.Element("{%s}%s" % (namespace(), tag))


def _add_sub_element(parent, tag):
    return ET.SubElement(parent, "{%s}%s" % (namespace(), tag))


def _add_element(parent, tag, text):
    sub = _add_sub_element(parent, tag)
    sub.text = text
    return sub


# Returns units as well and treats them as a unique identifier
def get_element(model, sid):
    el = model.getElementBySId(sid)

    if el is not None:
        return el

    el = model.getUnitDefinition(sid)  # Not especially wanted by sbml

    if el is not None:
        return el

    el = __get_element_data(model, sid)

    if el is not None:
        return el

    el = __get_element_reaction(model, sid)

    return el


def __get_element_data(model, sid):
    lor = model.getListOfReactions()
    xmlnode = _read_annotation(lor)
    data = EnzymeMLData()
    data.from_xmlnode(xmlnode)
    el = data.get_element_by_sid(sid)

    return el


def __get_element_reaction(model, sid):
    for reac in model.getListOfReactions():
        xmlnode = _read_annotation(reac)
        r = EnzymeMLReaction(reac)
        r.from_xmlnode(xmlnode)
        el = r.get_element_by_sid(sid)
        if el is not None:
            return el

    return None


# handles the addition of one object or a list
def _add_to_cvt(cvt, obj):
    if type(obj) is list:
        for o in obj:
            cvt.addResource(o)
    else:
        cvt.addResource(obj)


def _get_id(tup, meta=False):
    ret = None
    if type(tup) is tuple:
        ret = tup[1 if meta else 0]
    else:
        ret = tup

    if type(ret) is int and not meta:
        ret = sbml.UnitKind_toString(ret)

    return ret


def _create_bqbiol_cvt(term):
    cvt = sbml.CVTerm()
    cvt.setQualifierType(sbml.BIOLOGICAL_QUALIFIER)
    cvt.setBiologicalQualifierType(term)
    return cvt


def _create_bqmodel_cvt(term):
    cvt = sbml.CVTerm()
    cvt.setQualifierType(sbml.MODEL_QUALIFIER)
    cvt.setBiologicalQualifierType(term)
    return cvt


# classes to handle EnzymeML
class EnzymeMLSpecies:
    def __init__(self):
        self.inchi = None
        self.smiles = None
        self.iupac = None

    def set_inchi(self, inchi):
        self.inchi = inchi

    def set_smiles(self, smiles):
        self.smiles = smiles

    def set_iupac(self, iupac):
        self.iupac = iupac
    
    def has_elements(self):
        return self.inchi is not None or self.iupac is not None or self.smiles is not None

    def to_element(self):
        el = _create_base_element("species")

        if self.inchi is not None:
            _add_element(el, "inchi", self.inchi)
        if self.smiles is not None:
            _add_element(el, "smiles", self.smiles)
        if self.iupac is not None:
            _add_element(el, "iupac", self.iupac)

        return el

    def to_xml_string(self):
        el = self.to_element()
        return ET.tostring(el, "utf-8").decode("utf-8")

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        if xmlnode.hasChild("inchi"):
            self.inchi = xmlnode.getChild("inchi").getChild(0).getCharacters()
        if xmlnode.hasChild("smiles"):
            self.smiles = xmlnode.getChild("smiles").getChild(0).getCharacters()
        if xmlnode.hasChild("iupac"):
            self.iupac = xmlnode.getChild("iupac").getChild(0).getCharacters()
        return self


class EnzymeMLProtein:
    def __init__(self):
        self.sequence = None

    def set_sequence(self, fasta):
        self.sequence = fasta

    def to_element(self):
        el = _create_base_element("protein")

        if self.sequence is not None:
            _add_element(el, "sequence", self.sequence)

        return el

    def to_xml_string(self):
        el = self.to_element()
        return ET.tostring(el, "utf-8").decode("utf-8")

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        self.sequence = xmlnode.getChild("sequence").getChild(0).getCharacters()
        return self


class EnzymeMLReplica:
    def __init__(self, measureid, replicaid, sid=None):
        self.measurement = measureid
        self.replica = replicaid
        self.id = sid

    def to_element(self):
        el = _create_base_element("replica")

        el.set("id", str(_get_id(self.id)))
        el.set("replica", str(_get_id(self.replica)))
        el.set("measurement", str(_get_id(self.measurement)))

        return el

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        self.measurement = xmlnode.getAttrValue("measurement")
        self.replica = xmlnode.getAttrValue("replica")
        self.id = xmlnode.getAttrValue("id")


class EnzymeMLReaction:
    __replica_ids = dict()

    # args: float, (float, sid), (float, sid), (float, sid)
    def __init__(self, parent, ph=None, temp=None, press=None, shake=None):
        self.ph = ph
        self.temperature = temp
        self.pressure = press
        self.shaking_frequency = shake
        self.replicas = []

        self.sbml_reaction = parent
        mid = _get_model_ident(parent)
        EnzymeMLReaction.__replica_ids[mid] = 0

    def set_ph(self, ph):
        self.ph = ph

    def set_temperature(self, temp, unit):
        self.temperature = (temp, unit)

    def set_pressure(self, press, unit):
        self.pressure = (press, unit)

    def set_shaking_frequency(self, shake, unit):
        self.shaking_frequency = (shake, unit)

    def add_replica(self, replica, sid=None):
        self.replicas.append(replica)
        moid = _get_model_ident(self.sbml_reaction)
        if sid is None:
            if replica.id is None:
                replica.id = "re%i" % EnzymeMLReaction.__replica_ids[moid]
                EnzymeMLReaction.__replica_ids[moid] += 1
        else:
            replica.id = sid

    def get_element_by_sid(self, sid):
        for rep in self.replicas:
            if sid == rep.id:
                return rep

        return None

    def get_parent(self):
        return self.sbml_reaction

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "conditions":
                self._from_cond(node)
            elif node.getName() == "replicas":
                self._from_replica(node)
            else:
                if DEBUG:
                    print("The xmlNode name of reaction enzymeml tag '%s' is not given." % node.getName())

    def _from_cond(self, xmlnode):
        length = xmlnode.getNumChildren()
        if length == 0:
            return self

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "ph":
                self.ph = float(node.getAttrValue("value"))
            elif node.getName() == "temperature":
                t1 = float(node.getAttrValue("value"))
                t2 = node.getAttrValue("unit")
                self.temperature = (t1, t2)
            elif node.getName() == "pressure":
                t1 = float(node.getAttrValue("value"))
                t2 = node.getAttrValue("unit")
                self.pressure = (t1, t2)
            elif node.getName() == "shakingFrequency":
                t1 = float(node.getAttrValue("value"))
                t2 = node.getAttrValue("unit")
                self.shaking_frequency = (t1, t2)
            else:
                if DEBUG:
                    print("The xmlNode name of reaction enzymeml tag '%s' is not given." % node.getName())

    def _from_replica(self, xmlnode):
        length = xmlnode.getNumChildren()
        if length == 0:
            return self

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "replica":
                r = EnzymeMLReplica(None, None)
                r.from_xmlnode(node)
                self.add_replica(r)

    def to_element(self):
        base = _create_base_element("reaction")
        cond = _add_element(base, "conditions", None)

        if self.ph is not None:
            sub = _add_element(cond, "ph", None)
            sub.set("value", str(self.ph))

        if self.temperature is not None:
            sub = _add_element(cond, "temperature", None)
            sub.set("value", str(self.temperature[0]))
            sub.set("unit", str(_get_id(self.temperature[1])))

        if self.pressure is not None:
            sub = _add_element(cond, "pressure", None)
            sub.set("value", str(self.pressure[0]))
            sub.set("unit", str(_get_id(self.pressure[1])))

        if self.shaking_frequency is not None:
            sub = _add_element(cond, "shakingFrequency", None)
            sub.set("value", str(self.shaking_frequency[0]))
            sub.set("unit", str(_get_id(self.shaking_frequency[1])))

        if len(self.replicas) > 0:
            replicas = _add_element(base, "replicas", None)
            for r in self.replicas:
                replicas.append(r.to_element())

        return base

    def to_xml_string(self):
        el = self.to_element()
        return ET.tostring(el, "utf-8").decode("utf-8")


class EnzymeMLData:
    def __init__(self):
        self.listOfFormats = EnzymeMLListOfFormats()
        self.listOfFiles = EnzymeMLListOfFiles()
        self.listOfMeasurements = EnzymeMLListOfMeasurements()

    def list_sids(self):
        sids = list()
        sids += self.listOfFormats.formats.keys()
        sids += self.listOfMeasurements.measurements.keys()
        sids += self.listOfFiles.files.keys()
        return sids

    def get_element_by_sid(self, sid):
        sid = _get_id(sid)
        if sid in self.listOfFormats.formats:
            # TODO implementation of replications could use an identification system
            return self.listOfFormats.formats[sid]
        elif sid in self.listOfFiles.files:
            return self.listOfFiles.files[sid]
        elif sid in self.listOfMeasurements.measurements:
            return self.listOfMeasurements.measurements[sid]
        else:
            return None

    def get_format_by_file(self, loc):
        for sid in self.listOfFiles.files:
            file = self.listOfFiles.files[sid]

    def to_element(self):
        el = ET.Element("{%s}data" % namespace())

        if not self.listOfFormats.is_empty():
            el.append(self.listOfFormats.to_element())
        if not self.listOfFiles.is_empty():
            el.append(self.listOfFiles.to_element())
        if not self.listOfMeasurements.is_empty():
            el.append(self.listOfMeasurements.to_element())

        return el

    def to_xml_string(self):
        el = self.to_element()
        return ET.tostring(el, "utf-8").decode("utf-8")

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "listOfFormats":
                self.listOfFormats.from_xmlnode(node)
            elif node.getName() == "listOfFiles":
                self.listOfFiles.from_xmlnode(node)
            elif node.getName() == "listOfMeasurements":
                self.listOfMeasurements.from_xmlnode(node)
            else:
                if DEBUG:
                    print("The xmlNode name of data enzymeml tag '%s' is not given." % node.getName())


class EnzymeMLColumnType:
    def __init__(self, name, species_relevant, unit_relevant):
        self.name = name
        self.has_species = species_relevant
        self.has_unit = unit_relevant


COLUMN_TYPE_TIME = "time"
COLUMN_TYPE_CONCENTRATION = "conc"
COLUMN_TYPE_EMPTY = "empty"


class EnzymeMLColumn:
    def __init__(self, ct, text=None):
        self.type = ct
        self.text = text

    def has_species(self):
        return False

    def has_unit(self):
        return False

    def has_text(self):
        return self.text is not None

    def to_element(self):
        el = ET.Element("{%s}column" % namespace(), {"type": self.type})
        if self.text is not None:
            el.text = str(self.text)
        return el


class EnzymeMLColumnUnitowner(EnzymeMLColumn):
    def __init__(self, ct, unit, text=None):
        super().__init__(ct, text)
        self.unit = unit

    def has_unit(self):
        return True

    def to_element(self):
        el = super().to_element()
        el.set("unit", str(_get_id(self.unit)))
        return el


class EnzymeMLColumnConcentration(EnzymeMLColumnUnitowner):
    def __init__(self, ct, unit, species, repl=None, text=None):
        super().__init__(ct, unit, text)
        self.species = species
        self.replica = repl

    def has_species(self):
        return True

    def to_element(self):
        el = super().to_element()
        el.set("species", str(_get_id(self.species)))
        el.set("replica", str(_get_id(self.replica)))
        return el


class EnzymeMLColumnEmpty(EnzymeMLColumn):
    def __init__(self, amount=None, text=None):
        super().__init__(COLUMN_TYPE_EMPTY, text)
        self.amount = amount

    def get_amount(self):
        return 1 if self.amount is None else self.amount

    def to_element(self):
        el = super().to_element()
        if self.amount is not None:
            el.set("amount", str(self.amount))
            return el
        else:
            return el


# Usage args:
# COLUMN_TYPE_TIME: unit, (text)
# COLUMN_TYPE_CONCENTRATION: species, unit, (replica id), (text)
# COLUMN_TYPE_EMPTY: (amount)
def create_column(ct, *args):
    if ct is COLUMN_TYPE_TIME:
        return EnzymeMLColumnUnitowner(ct, args[0], None if len(args) < 2 else args[1])
    elif ct is COLUMN_TYPE_CONCENTRATION:
        return EnzymeMLColumnConcentration(
            ct, args[1], args[0],
            None if len(args) < 3 else args[2], None if len(args) < 4 else args[3])
    elif ct is COLUMN_TYPE_EMPTY:
        return EnzymeMLColumnEmpty(None if len(args) < 1 else args[0],  None if len(args) < 2 else args[1])
    else:
        if DEBUG:
            print("Unknown column type %s added as an empty column." % ct)
        return EnzymeMLColumnEmpty(None, ct)


# This describes the different columns of the CSV file. Order of the elements is important
class EnzymeMLFormat:
    def __init__(self):
        self.columns = list()
        self.sid = None
        self._replica_id = dict()

    def add_column(self, column):
        if not issubclass(type(column), EnzymeMLColumn):
            raise ValueError("""The added column ('%s') is not of type EnzymeMLColumn. Please use create_column() to
                              create new columns.""" % str(type(column)))
        self.columns.append(column)
        if type(column) is EnzymeMLColumnConcentration and column.replica is None:
            if _get_id(column.species) not in self._replica_id:
                self._replica_id[_get_id(column.species)] = 0
            column.replica = "repl%i" % self._replica_id[_get_id(column.species)]
            self._replica_id[_get_id(column.species)] += 1
        return column

    def is_empty(self):
        return len(self.columns) == 0

    def validate(self):  # TODO validate if only one time and if they are given
        return self.sid is not None

    def to_element(self, sid):
        el = ET.Element("{%s}format" % namespace(), {"id": sid})

        for c in self.columns:
            e = c.to_element()
            el.append(e)

        return el

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return self

        for i in range(0, length):
            node = xmlnode.getChild(i)
            text = None
            if node.getName() == "column":
                t = node.getAttrValue("type")
                if (t is None or t == "") and DEBUG:
                    print("No type is given in the column in line %i." % node.getLine())
                    continue

                if t == COLUMN_TYPE_TIME:
                    un = node.getAttrValue("unit")

                    if node.getNumChildren() > 0:
                        text = node.getChild(0).getCharacters()

                    self.add_column(create_column(COLUMN_TYPE_TIME, un, text))
                elif t == COLUMN_TYPE_CONCENTRATION:
                    sp = node.getAttrValue("species")
                    un = node.getAttrValue("unit")
                    repl = node.getAttrValue("replica")

                    if node.getNumChildren() > 0:
                        text = node.getChild(0).getCharacters()

                    self.add_column(EnzymeMLColumnConcentration(COLUMN_TYPE_CONCENTRATION, un, sp, repl, text))
                elif t == COLUMN_TYPE_EMPTY:
                    a = node.getAttrValue("amount")
                    if a == "" or not a.isdigit():
                        a = None
                    if node.getNumChildren() > 0:
                        text = node.getChild(0).getCharacters()
                    self.add_column(create_column(COLUMN_TYPE_EMPTY, None if a is None else int(a), text))
                else:
                    if DEBUG:
                        print("Unknown type is given in the column in line %i." % node.getLine())
                    self.add_column(create_column(COLUMN_TYPE_EMPTY, None, t))
            else:
                if DEBUG:
                    print("The xmlNode name of format enzymeml tag '%s' is not given." % node.getName())


# This describes the CSV file format
class EnzymeMLListOfFormats:
    def __init__(self):
        self.formats = dict()
        self._id = 0

    def add_format(self, sid=None, form=None):
        if form is None:
            form = EnzymeMLFormat()
        if sid is None:
            sid = "format%i" % self._id
            self._id += 1
        form.sid = sid
        self.formats[sid] = form
        return form

    def is_empty(self):
        return len(self.formats) == 0

    def to_element(self):
        el = ET.Element("{%s}listOfFormats" % namespace())

        for f in self.formats:
            el.append(self.formats[f].to_element(f))

        return el

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return self

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "format":
                sid = node.getAttrValue("id")
                if sid == "":
                    sid = None
                form = self.add_format(sid)
                form.from_xmlnode(node)
            else:
                if DEBUG:
                    print("The xmlNode name of format enzymeml tag '%s' is not given." % node.getName())


# This lists all files with their specific formats
class EnzymeMLListOfFiles:
    def __init__(self):
        self.files = dict()
        self._id = 0

    def add_file(self, location, form, sid=None):
        if sid is None:
            sid = "file%i" % self._id
            self._id += 1

        f = EnzymeMLCSV(form, loc=location)
        f.location = location

        self.files[sid] = f
        f.sid = sid
        return f

    def get_files(self):
        return self.files.values()

    def get_file(self, sid):
        return self.files[sid]

    def get_file_by_location(self, loc):
        for sid in self.files:
            file = self.files[sid]
            if file.location == loc:
                return file
        return None

    def list_ids(self):
        return self.files.keys()

    def is_empty(self):
        return len(self.files) == 0

    def to_element(self):
        el = ET.Element("{%s}listOfFiles" % namespace())

        for f in self.files:
            sub = ET.SubElement(el, "{%s}file" % namespace())
            sub.set("id", _get_id(f))
            sub.set("file", str(self.files[f].location))
            sub.set("format", str(_get_id(self.files[f].format)))

        return el

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "file":
                sid = node.getAttrValue("id")
                if sid == "":
                    sid = None
                self.add_file(node.getAttrValue("file"), node.getAttrValue("format"), sid)
            else:
                if DEBUG:
                    print("The xmlNode name of format enzymeml tag '%s' is not given." % node.getName())


# This lists all made measurements with the files and the data positions
class EnzymeMLListOfMeasurements:
    class Measurement:
        def __init__(self, name, file, start, stop):
            self.name = name
            self.file = file
            self.start = start
            self.stop = stop
            self.sid = None

    def __init__(self):
        self.measurements = dict()
        self._id = 0

    def add_measurement(self, name, file, start, stop, sid=None):
        if sid is None:
            sid = "M%i" % self._id
            self._id += 1

        m = EnzymeMLListOfMeasurements.Measurement(name, file, start, stop)
        self.measurements[sid] = m
        m.sid = sid
        return m

    def get_measurements(self):
        return self.measurements.values()

    def get_measurement(self, sid):
        return self.measurements[sid]

    def list_ids(self):
        return self.measurements.keys()

    def is_empty(self):
        return len(self.measurements) == 0

    def to_element(self):
        el = ET.Element("{%s}listOfMeasurements" % namespace())

        for m in self.measurements:
            sub = ET.SubElement(el, "{%s}measurement" % namespace())
            sub.set("id", str(_get_id(m)))
            sub.set("name", str(self.measurements[m].name))
            sub.set("file", str(_get_id(self.measurements[m].file)))
            sub.set("start", str(self.measurements[m].start))
            sub.set("stop", str(self.measurements[m].stop))

        return el

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "measurement":
                sid = node.getAttrValue("id")
                if sid == "":
                    sid = None
                self.add_measurement(node.getAttrValue("name"), node.getAttrValue("file"),
                                     int(node.getAttrValue("start")), int(node.getAttrValue("stop")), sid)
            else:
                if DEBUG:
                    print("The xmlNode name of format enzymeml tag '%s' is not given." % node.getName())


# Used data container of the modelling file
class EnzymeMLUsedData:
    def __init__(self):
        self.replicas = dict()

    def add_replica(self, reaction, replica):
        if reaction is None:
            reaction = ""

        if _get_id(reaction) not in self.replicas:
            self.replicas[_get_id(reaction)] = list()

        if replica is not None:
            self.replicas[_get_id(reaction)].append(_get_id(replica))

    def to_element(self):
        el = _create_base_element("modelReaction")
        sub_d = _add_sub_element(el, "usedData")

        for reac in self.replicas:
            sub = _add_sub_element(sub_d, "usedReaction")

            if reac is not "":
                sub.set("reactionRef", str(_get_id(reac)))

            for repl in self.replicas[reac]:
                sub_r = _add_sub_element(sub, "usedReplica")
                sub_r.set("replicaRef", str(_get_id(repl)))

        return el

    def to_xml_string(self):
        el = self.to_element()
        return ET.tostring(el, "utf-8").decode("utf-8")

    def from_xmlnode(self, xmlnode):
        if xmlnode is None:
            return
        length = xmlnode.getNumChildren()
        if length == 0:
            return

        for i in range(0, length):
            node = xmlnode.getChild(i)
            if node.getName() == "usedReaction":
                reac = node.getAttrValue("reactionRef")
                self.add_replica(reac, None)  # If only the reaction is mentioned

                for j in range(0, node.getNumChildren()):
                    nodechild = node.getChild(j)
                    if nodechild.getName() == "usedReplica":
                        self.add_replica(reac, nodechild.getAttrValue("replicaRef"))


# inconsistent namespaces in XMlNodes.
def _get_namespace(xmlnode):
    ns = xmlnode.getNamespaceURI()
    if ns is not None and ns is not "":
        return ns

    pre = xmlnode.getPrefix()
    if pre is not None and pre is not "":
        return xmlnode.getNamespaceURI(pre)
    return None


# returns the XMLNode with the EnzymeML annotation or None if there is None
def _read_annotation(element):
    if not element.isSetAnnotation():
        return None
    ann = element.getAnnotation()
    for i in range(0, ann.getNumChildren()):
        check = ann.getChild(i)
        if _get_namespace(check) == namespace():
            return check
    return None


def _annotation_write(el, tag, xml_str):
    el.removeTopLevelAnnotationElement(tag)
    el.appendAnnotation(xml_str)


"""
This file uses the EnzymeML Keys to add or read the fields of the EnzymeML notation.

TODO:
id management is missing in add_to_model()
"""
# TODO


__model_ids = 0


def _create_model_id(model):
    global __model_ids
    i = __model_ids
    __model_ids += 1

    model.getSBMLDocument().setLocationURI(str(i))
    return str(i)


#def _get_model(ident):
#    return __model_dict[ident]


def _get_model_ident(model):
    return model.getSBMLDocument().getLocationURI()


####################################################################################################
# The main EnzymeML file. This class is used to create, load and modify EnzymeML Combine Archives. #
# This class allows the management of the different included files.                                #
####################################################################################################
class EnzymeML:
    def __init__(self, name):
        self.name = name
        self.master = _create_experiment_sbml_document()
        self.models = list()
        self.id = _create_model_id(self.master)
        self.csvs = list()
        self.reaction_condition = dict()
        self.reaction_data = None
        self.creator = list()

    def create_model(self, name):
        exd = _create_experiment_sbml_document()
        ident = _create_model_id(exd)
        enzmod = EnzymeMLModel(exd, self, ident)
        enzmod.name = name
        _create_model_sbml_document(self.master, exd, ident)
        self.models.append(enzmod)

        return enzmod

    def add(self, ekey, obj, ident=None):
        return add_to_model(self, ekey, obj, ident)

    def add_csv(self, csv):
        if type(csv) is not EnzymeMLCSV:
            raise ValueError("The argument (%s) is not type of EnzymeMLCSV." % type(csv))
        if csv.location is None:
            csv.location = "./data/%s.csv" % csv.name
        self.csvs.append(csv)

    def add_creator(self, family, given, email, org):
        vcard = combine.VCard()
        vcard.setFamilyName(family)
        vcard.setGivenName(given)
        if org is not None:
            vcard.setOrganization(org)
        if email is not None:
            vcard.setEmail(email)
        self.creator.append(vcard)

    def create_reaction_cond(self, sid):
        self.reaction_condition[sid] = EnzymeMLReaction(self.get_model())
        return self.reaction_condition[sid]

    def get_reaction_cond(self, sid):
        return self.reaction_condition[sid] if sid in self.reaction_condition else None

    def create_reaction_data(self):
        self.reaction_data = EnzymeMLData()
        return self.reaction_data

    def get_reaction_data(self):
        return self.reaction_data

    # Used to create all files in a folder without the archive, returns the archive object
    def create_files(self):
        try:
            os.mkdir("./%s" % self.name)
            print("Created directory %s\\%s." % (os.getcwd(), self.name))
        except FileExistsError:
            pass

        if len(self.models) > 0:
            try:
                os.mkdir("./%s/models" % self.name)
                print("Created directory %s\\%s." % (os.getcwd(), self.name))
            except FileExistsError:
                pass

        if len(self.csvs) > 0:
            try:
                os.mkdir("./%s/data" % self.name)
                print("Created directory %s\\%s." % (os.getcwd(), self.name))
            except FileExistsError:
                pass

        archive = combine.CombineArchive()
        descr = combine.OmexDescription()
        descr.setAbout(".")
        descr.setDescription("EnzymeML Archive - %s" % self.name)
        descr.setCreated(combine.OmexDescription.getCurrentDateAndTime())

        for creator in self.creator:
            descr.addCreator(creator)

        archive.addMetadata(".", descr)

        self.write_sbml_file("%s/experiment.xml" % self.name)
        archive.addFile("%s/experiment.xml" % self.name, "./experiment.xml",
                        combine.KnownFormats.lookupFormat("sbml"), True)

        for model in self.models:
            model.write_sbml_file("%s/models/%s.xml" % (self.name, model.name))
            archive.addFile("%s/models/%s.xml" % (self.name, model.name), "./models/%s.xml" % model.name,
                            combine.KnownFormats.lookupFormat("sbml"), False)

        for csv in self.csvs:
            csv.write("%s/data/%s.csv" % (self.name, csv.name))
            archive.addFile("%s/data/%s.csv" % (self.name, csv.name), csv.location,
                            combine.KnownFormats.lookupFormat("csv"))

        return archive

    # Creates all files and saves them as Zip archive. The deletes the folder.
    def create_archive(self, delete=False):
        archive = self.create_files()
        file = "%s.omex" % self.name
        if os.path.isfile(file):
            os.remove(file)
        archive.writeToFile(file)

        if DEBUG:
            print("Written file '%s'." % file)

        if delete:
            shutil.rmtree("./%s" % self.name)

    def write_sbml_file(self, location):
        model = self.get_model()
        for reac in model.getListOfReactions():
            reac.removeTopLevelAnnotationElement("reaction")
        model.getListOfReactions().removeTopLevelAnnotationElement("data")

        for rc in self.reaction_condition:
            el = model.getElementBySId(rc)
            el.appendAnnotation(self.get_reaction_cond(rc).to_xml_string())

        data = self.reaction_data
        if data is not None:
            lor = model.getListOfReactions()
            lor.appendAnnotation(self.get_reaction_data().to_xml_string())

        sbml.writeSBMLToFile(self.master, location)

    # The following functions are used by the functions
    def get_doc(self):
        return self.master

    def get_model(self):
        return self.master.getModel()

    # Following functions are used to load an EnzymeML from the archieve file
    def load_from_file(self, location):
        omx = combine.CombineArchive()

        if omx.initializeFromArchive(location) is None:
            raise RuntimeError("Could not find a valid omex archive at '%s'." % location)

        # load the master experiment file:
        master = omx.getMasterFile().getLocation()
        me = omx.getEntryByLocation(master)
        if me.getFormat() != combine.KnownFormats.lookupFormat("sbml"):
            raise RuntimeError("Master file ('%s') is not a sbml file." % master)

        self.master = sbml.readSBMLFromString(omx.extractEntryToString(master))
        _load_experiment_sbml_document(self.master)
        model = self.master.getModel()

        # load annotations of experiment file
        lor_ann = _read_annotation(model.getListOfReactions())
        if lor_ann is not None:
            self.reaction_data = EnzymeMLData()
            self.reaction_data.from_xmlnode(lor_ann)

        for reacel in model.getListOfReactions():
            re_ann = _read_annotation(reacel)
            if re_ann is not None:
                recon = self.create_reaction_cond(reacel.getId())
                recon.from_xmlnode(re_ann)

        models = list()  # This solution for reading the archive because of a bug
        csvs = list()

        # load other files
        for i in range(omx.getNumEntries()):
            entry = omx.getEntry(i)

            if entry.isSetMaster() and entry.getMaster():
                continue

            if entry.getFormat() == combine.KnownFormats.lookupFormat("sbml"):
                models.append(entry)
            elif entry.getFormat() == combine.KnownFormats.lookupFormat("csv"):
                csvs.append(entry)

        # load models
        for model in models:
            modeldoc = sbml.readSBMLFromString(omx.extractEntryToString(model.getLocation()))
            _load_model_sbml_document(modeldoc)
            ident = _create_model_id(modeldoc)
            enzmod = EnzymeMLModel(modeldoc, self, ident)
            enzmod.name = os.path.splitext(model.getLocation())[0]
            enzmod.load_from_document(modeldoc)

        # load csv files
        for csv in csvs:
            csvstr = omx.extractEntryToString(csv.getLocation())
            csvenz = self.reaction_data.listOfFiles.get_file_by_location(csv.getLocation())
            if csvenz is not None:
                csvenz.read(csvstr)
                self.csvs.append(csvenz)
            else:
                print("[Warning] The CSV file '%s' is not mentioned in the experiment file." % csv.getLocation())
                # TODO logging?


#############################################################
# This class describes a model file of an EnzymeML Archive. #
# doc: The SBMLDocument of the Model                        #
# parent: The EnzymeML file                                 #
#############################################################
class EnzymeMLModel:
    def __init__(self, doc, parent, ident):
        self.sbmldoc = doc
        self.parent = parent
        self.id = ident
        self.name = "unidentified"
        self.used_data = dict()

    def add(self, ekey, obj, ident=None):
        return add_to_model(self, ekey, obj, ident)

    def create_used_data(self, sid):  # TODO write to file
        self.used_data[sid] = EnzymeMLUsedData()
        return self.used_data[sid]

    def get_used_data(self, sid):
        return self.used_data[sid] if sid in self.used_data else None

    # The following functions are used by the functions
    def write_sbml_file(self, location):
        model = self.get_model()
        for reac in model.getListOfReactions():
            reac.removeTopLevelAnnotationElement("modelReaction")

        for sid in self.used_data:
            el = model.getElementBySId(sid)
            el.appendAnnotation(self.get_used_data(sid).to_xml_string())

        sbml.writeSBMLToFile(self.sbmldoc, location)

    def get_doc(self):
        return self.sbmldoc

    def get_model(self):
        return self.sbmldoc.getModel()

    def load_from_document(self, doc):
        _load_model_sbml_document(doc)


################################################################
# This class describes a CSV file and is used to save the data #
################################################################
class EnzymeMLCSV:
    def __init__(self, form, name=None, loc=None):
        self.columns = list()
        self.format = form
        self.name = name
        self.location = loc
        self.sid = None

        if name is None and loc is None:
            raise ValueError("The parameters name and location are None.")

        if name is None:
            self.name = os.path.splitext(self.location)[0]

    def add_column(self, col):
        self.columns.append(col)

    def nrows(self):
        rs = 0

        for col in self.columns:
            l = len(col)
            if l > rs:
                rs = l

        return rs

    def get_rows(self):
        rows = list()

        for i in range(0, self.nrows()):
            row = list()

            for col in self.columns:
                if i < len(col):
                    row.append(col[i])
                else:
                    row.append(None)

            rows.append(row)

        return rows

    def write(self, name):
        f = open(name, "w+")

        rows = self.get_rows()
        for rn in range(0, len(rows)):
            row = rows[rn]
            line = ""

            for cn in range(0, len(row) - 1):
                if row[cn] is not None:
                    line += str(row[cn])
                line += ","

            if len(row) > 0:
                if row[len(row) - 1] is not None:
                    line += str(row[len(row) - 1])
                line += "\n"

            f.write(line)

        f.close()

    def read(self, csv_str):
        columns = list()

        lines = csv_str.splitlines()
        for line in lines:
            cols = line.split(",")
            for i in range(len(cols)):
                if len(columns) <= i:
                    columns.append(list())

                el = cols[i]
                if el == "":
                    columns[i].append(None)
                else:
                    try:
                        columns[i].append(decimal.Decimal(el))
                    except decimal.InvalidOperation:
                        columns[i].append(str(el))

        for col in columns:
            self.columns.append(col)

    def validate(self):  # TODO validate with the format for consistency
        return self.loc is not None


# This function should be used to create the experiment sbml file
def _create_experiment_sbml_document():
    sbmlns = sbml.SBMLNamespaces(3, 2, "distrib", 1)
    doc = sbml.SBMLDocument(sbmlns)
    doc.setPackageRequired("distrib", True)
    model = doc.createModel()
    model.setMetaId("META_MODEL")
    # doc.add_enzymeml = types.MethodType(_add_enzymeml, model)
    # doc.enzymeml_type = "experiment"
    return doc


def _load_experiment_sbml_document(exdoc):
    if not exdoc.getPackageRequired("distrib"):
        exdoc.enablePackage(sbml.DistribExtension.getXmlnsL3V1V1(), "distrib", True)

    if not exdoc.isSetModel():
        exdoc.createModel()

    model = exdoc.getModel()
    if not model.isSetMetaId():
        model.setMetaId("META_MODEL")

    return exdoc


# This method should be used to create the model sbml file
def _create_model_sbml_document(exp_doc, doc, ident):
    # doc.enzymeml_type = "model"
    # doc.experiment = exp_doc

    m_exp = exp_doc.getModel()
    model = doc.getModel()

    # TODO get the exp_doc bqmodel is

    # Handle Compartments
    loc = m_exp.getListOfCompartments()
    for c in loc:
        pass  # FIXME is this even needed?

    # Load species
    los = m_exp.getListOfSpecies()
    spec = dict()
    for s in los:
        # TODO identifiers need to be compared?
        name = s.getName()
        if name in spec:
            spec[name].append((s.getId(), s.getSBOTermID()))
        else:
            spec[name] = [(s.getId(), s.getSBOTermID())]

    __init_species(model)
    global __species_ids
    __species_ids[ident] = 0

    for sname in spec:
        sbos = list()
        for el in spec[sname]:
            sbo = el[1]
            if sbo not in sbos:
                sbos.append(sbo)

        for sbo in sbos:
            s = model.createSpecies()
            s.setName(sname)
            s.setId("S%i" % __species_ids[ident])
            __species_ids[ident] += 1
            s.setSBOTerm(sbo)

    return doc


def _load_model_sbml_document(doc):
    _load_experiment_sbml_document(doc)


# model - The SBMl model object
# ekey - The enzymemlkey code
# ident - The identification tuple of the modifying object
# obj - The object (mostly dictionary or string) to be added to the file
# TODO reform everything
def add_to_model(enzymeml, ekey, obj, ident=None):
    func = _key_func_dict[ekey]

    if func is None:
        raise UnknownEnzymeMLKeyException(ekey)

    # Convert every decimal to libsbml compatible floats
    if type(obj) == dict:
        for k in obj:
            if type(obj[k]) == decimal.Decimal:
                obj[k] = float(obj[k])

    return func(enzymeml, ident, obj)


def get_species_annotation(species):
    ann = _read_annotation(species)
    if ann is None:
        return None

    if ann.getName() == "species":
        return EnzymeMLSpecies().from_xmlnode(ann)
    elif ann.getName() == "protein":
        return EnzymeMLProtein().from_xmlnode(ann)
    else:
        return None


def get_bqb_identifier(element, quali):
    out = list()

    for cvt in element.getCVTerms():
        if cvt.getQualifierType() == sbml.BIOLOGICAL_QUALIFIER and cvt.getBiologicalQualifierType() == quali:
            for i in range(cvt.getNumResources()):
                out.append(cvt.getResourceURI(i))

    return out


def get_bqm_identifier(element, quali):
    out = list()

    for cvt in element.getCVTerms():
        if cvt.getQualifierType() == sbml.MODEL_QUALIFIER and cvt.getBiologicalQualifierType() == quali:
            pass

    return out


# TODO used to validate the elements and check for set annotations for ontology manager
def validate_element(element):
    return True


# TODO validate of logic and completeness must be implemented
def validate(doc):
    model = doc.getModel()
    __validate_model(model)

    for unit in model.getListOfUnitDefinitions():
        __validate_unit(unit)

    for species in model.getListOfSpecies():
        __validate_species(species)

    for comp in model.getListOfCompartments():
        __validate_compartment(comp)

    for reac in model.getListOfReactions():
        __validate_reaction(reac)


######################
# Validator Handling #
######################
def __validate_model(element):
    pass


def __validate_unit(element):
    pass


def __validate_species(element):
    pass


def __validate_compartment(element):
    pass


def __validate_reaction(element):
    pass


######################
# MAIN File Handling #
######################
def __unspecific_note(enzymeml, ident, obj):
    part = get_element(enzymeml.get_model(), _get_id(ident))

    if part is None:
        print("Element with id '%s' could not be found. Ignoring note step." % _get_id(ident))
        return

    if not issubclass(type(part), sbml.SBase):
        raise RuntimeError("The requested element %s to note is not noteable." % _get_id(ident))

    if obj is None:
        return ident

    if type(obj) is dict:
        part.setNotes("<body xmlns='http://www.w3.org/1999/xhtml'><h1>%s</h1><p>%s</p></body>"
                      % (obj["heading"], obj["text"]))
    else:
        part.setNotes(obj, True)

    return ident


def __main_meta_expname(enzymeml, ident, obj):
    model = enzymeml.get_model()
    model.setName(obj)
    return ident


def __main_meta_name(enzymeml, ident, obj):
    model = enzymeml.get_model()

    if model.isSetModelHistory():
        his = model.getModelHistory()
    else:
        his = sbml.ModelHistory()
        t = time.now()
        date = sbml.Date(t.year, t.month, t.day, t.hour, t.minute, t.second)
        his.setCreatedDate(date)
        his.setModifiedDate(date)

    c = sbml.ModelCreator()

    c.setFamilyName(obj["family"])
    c.setGivenName(obj["given"])

    if "email" in obj:
        c.setEmail(obj["email"])
    if "orcid" in obj:
        if DEBUG:
            print(NotImplementedError("OrcID not implemented yet"))
            print(traceback.format_exc())
    if "org" in obj:
        c.setOrganization(obj["org"])

    his.addCreator(c)
    model.setModelHistory(his)

    return model.getId(), model.getMetaId()


def __main_meta_date_create(enzymeml, ident, obj):
    model = enzymeml.get_model()

    t = time.now()
    date = sbml.Date(t.year, t.month, t.day, t.hour, t.minute, t.second)
    if model.isSetModelHistory():
        his = model.getModelHistory()
    else:
        raise RuntimeError("The model creator(s) must be named before the date can be added.")

    if obj is not None:
        his.setCreatedDate(obj)
    else:
        his.setCreatedDate(date)

    if not his.isSetModifiedDate():
        his.setModifiedDate(his.getCreatedDate())

    r = model.setModelHistory(his)
    if r != 0:
        raise ValueError("libsbml returned the error code %i." % r)

    return model.getId(), model.getMetaId()


def __main_meta_date_modify(enzymeml, ident, obj):
    model = enzymeml.get_model()

    t = time.now()
    date = sbml.Date(t.year, t.month, t.day, t.hour, t.minute, t.second)

    if model.isSetModelHistory():
        his = model.getModelHistory()
    else:
        raise RuntimeError("The model creator(s) must be named before the date can be added.")

    if obj is not None:
        his.setModifiedDate(obj)
    else:
        his.setModifiedDate(date)

    if not his.isSetCreatedDate():
        his.setCreatedDate(his.getModifiedDate())

    r = model.setModelHistory(his)
    if r != 0:
        raise ValueError("libsbml returned the error code %i." % r)

    return model.getId(), model.getMetaId()


__unit_ids = dict()


def __init_unit(model):
    global __unit_ids
    mid = _get_model_ident(model)
    if mid not in __unit_ids:
        __unit_ids[mid] = 0


def __main_unit(enzymeml, ident, obj):
    model = enzymeml.get_model()

    __init_unit(model)
    global __unit_ids

    unit_def = model.createUnitDefinition()
    unit_def.setName(obj["name"])

    mid = _get_model_ident(model)
    ident = ("u%s" % __unit_ids[mid],
             "META_UNIT_%s" % __unit_ids[mid])

    unit_def.setId(ident[0])
    unit_def.setMetaId(ident[1])

    units = obj["units"]

    for unit in units:
        u = unit_def.createUnit()
        u.setKind(unit["kind"])

        if "exponent" in unit:
            u.setExponent(unit["exponent"])
        else:
            u.setExponent(1)

        if "scale" in unit:
            u.setScale(unit["scale"])
        else:
            u.setScale(1)

        if "multiplier" in unit:
            u.setMultiplier(unit["multiplier"])
        else:
            u.setMultiplier(1)

    __unit_ids[mid] += 1

    return ident


def __main_unit_is(enzymeml, ident, obj):
    doc = enzymeml.get_doc()
    element = doc.getElementByMetaId(_get_id(ident, True))

    cvt = _create_bqbiol_cvt(sbml.BQB_IS)
    _add_to_cvt(cvt, obj)

    element.addCVTerm(cvt)

    return ident


__compartment_ids = dict()


def __init_compartment(model):
    global __compartment_ids
    mid = _get_model_ident(model)
    if mid not in __compartment_ids:
        __compartment_ids[mid] = 0


def __main_compartment(enzymeml, ident, obj):
    model = enzymeml.get_model()

    __init_compartment(model)
    global __compartment_ids

    comp_def = model.createCompartment()

    if "name" in obj:
        comp_def.setName(obj["name"])
    else:
        comp_def.setName("unidentified")

    mid = _get_model_ident(model)
    ident = ("c%s" % __compartment_ids[mid],
             "META_COMPARTMENT_%s" % __compartment_ids[mid])

    comp_def.setId(ident[0])
    comp_def.setMetaId(ident[1])

    if "dimensions" in obj:
        comp_def.setSpatialDimensions(obj["dimensions"])
    else:
        comp_def.setSpatialDimensions(3)

    if "constant" in obj:
        comp_def.setConstant(obj["constant"])
    else:
        comp_def.setConstant(True)

    if "size" in obj:
        comp_def.setSize(obj["size"])

    if "units" in obj:
        comp_def.setUnits(_get_id(obj["units"]))

    __compartment_ids[mid] += 1

    return ident


def __main_compartment_is(enzymeml, ident, obj):
    doc = enzymeml.get_doc()
    element = doc.getElementByMetaId(_get_id(ident, True))

    cvt = _create_bqbiol_cvt(sbml.BQB_IS)
    _add_to_cvt(cvt, obj)

    element.addCVTerm(cvt)

    return ident


__species_ids = dict()


def __init_species(model):
    global __species_ids
    mid = _get_model_ident(model)
    if mid not in __species_ids:
        __species_ids[mid] = 0


def __main_species(enzymeml, ident, obj):
    model = enzymeml.get_model()

    __init_species(model)
    global __species_ids

    sp_def = model.createSpecies()
    sp_def.setName(obj["name"])

    mid = _get_model_ident(model)
    ident = ("s%i" % __species_ids[mid],
             "META_SPECIES_%s" % __species_ids[mid])

    sp_def.setId(ident[0])
    sp_def.setMetaId(ident[1])

    if "type" in obj:
        sp_def.setSBOTerm(obj["type"])
    else:
        sp_def.setSBOTerm(ontology.SBO_INTERACTOR)

    if "init_conc" in obj and "init_amount" in obj:
        raise ValueError("'init_conc' and 'init_amount' cannot be assigned at the same time.")
    elif "init_conc" in obj:
        sp_def.setInitialConcentration(obj["init_conc"])
        sp_def.setHasOnlySubstanceUnits(False)
    elif "init_amount" in obj:
        sp_def.setInitialConcentration(obj["init_amount"])
        sp_def.setHasOnlySubstanceUnits(True)

    if "compartment" in obj:
        sp_def.setCompartment(_get_id(obj["compartment"]))
    else:
        raise ValueError("'compartment' argument is missing to create a species")

    if "units" in obj:
        sp_def.setUnits(_get_id(obj["units"]))

    if "constant" in obj:
        sp_def.setConstant(obj["constant"])
    else:
        sp_def.setConstant(False)

    if "boundary_conditions" in obj:
        sp_def.setBoundaryCondition(obj["boundary_conditions"])
    else:
        sp_def.setBoundaryCondition(False)

    if "stdev" in obj and obj["stdev"] is not None:
        distrib = sp_def.getPlugin("distrib")
        unc = distrib.createUncertainty()
        unc_para = unc.createUncertParameter()
        unc_para.setType("standardDeviation")

        if type(obj["stdev"]) is tuple:
            unc_para.setValue(obj["stdev"][0])
            unc_para.setUnits(_get_id(obj["stdev"][1]))
        else:
            unc_para.setValue(obj["stdev"])

    __species_ids[mid] += 1
    return ident


def __main_species_simple(enzymeml, ident, obj):
    doc = enzymeml.get_doc()
    element = doc.getElementByMetaId(_get_id(ident, True))

    species = EnzymeMLSpecies()
    # FIXME no loading of the preexistent data

    if "inchi" in obj:
        species.set_inchi(obj["inchi"])
    if "iupac" in obj:
        species.set_iupac(obj["iupac"])
    if "smiles" in obj:
        species.set_smiles(obj["smiles"])

    if species.has_elements():
        xml = species.to_xml_string()
        element.appendAnnotation(xml)

    if "is" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_IS)
        _add_to_cvt(cvt, obj["is"])
        element.addCVTerm(cvt)

    return ident


def __main_species_protein(enzymeml, ident, obj):
    doc = enzymeml.get_doc()
    element = doc.getElementByMetaId(_get_id(ident, True))

    # FIXME no load function performed. As long as only 1 tag is included, it works
    protein = EnzymeMLProtein()

    protein.set_sequence(obj["sequence"])
    element.appendAnnotation(protein.to_xml_string())

    if "is" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_IS)
        _add_to_cvt(cvt, obj["is"])
        element.addCVTerm(cvt)
    if "hasPart" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_HAS_PART)
        _add_to_cvt(cvt, obj["hasPart"])
        element.addCVTerm(cvt)
    if "hasTaxon" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_HAS_TAXON)
        _add_to_cvt(cvt, obj["hasTaxon"])
        element.addCVTerm(cvt)
    if "encodedBy" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_IS_ENCODED_BY)
        _add_to_cvt(cvt, obj["encodedBy"])
        element.addCVTerm(cvt)
    if "occursIn" in obj:
        cvt = _create_bqbiol_cvt(sbml.BQB_OCCURS_IN)
        _add_to_cvt(cvt, obj["occursIn"])

    return ident


__reactions_ids = dict()


def __init_reactions(model):
    global __reactions_ids
    mid = _get_model_ident(model)
    if mid not in __reactions_ids:
        __reactions_ids[mid] = 0


def __main_reaction(enzymeml, ident, obj):
    model = enzymeml.get_model()

    __init_reactions(model)
    global __reactions_ids

    reac = model.createReaction()
    reac.setName(obj["name"])

    mid = _get_model_ident(model)
    ident = ("r%i" % __reactions_ids[mid],
             "META_REACTION_%s" % __reactions_ids[mid])

    reac.setId(ident[0])
    reac.setMetaId(ident[1])

    if "reversible" in obj:
        reac.setReversible(obj["reversible"])
    else:
        reac.setReversible(False)

    if "reactants" in obj:
        __main_reaction_reactioncomponent_add(reac.createReactant, obj["reactants"])

    if "modifier" in obj:
        __main_reaction_reactioncomponent_add(reac.createModifier, obj["modifier"])

    if "products" in obj:
        __main_reaction_reactioncomponent_add(reac.createProduct, obj["products"])

    __reactions_ids[mid] += 1
    return ident


def __main_reaction_reactant(enzymeml, ident, obj):
    model = enzymeml.get_model()
    reac = model.getElementBySId(_get_id(ident))
    if type(reac) is not sbml.Reaction:
        raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))
    __main_reaction_reactioncomponent_add(reac.createReactant, obj)
    return ident


def __main_reaction_modifier(enzymeml, ident, obj):
    model = enzymeml.get_model()
    reac = model.getElementBySId(_get_id(ident))
    if type(reac) is not sbml.Reaction:
        raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))
    __main_reaction_reactioncomponent_add(reac.createModifier, obj)
    return ident


def __main_reaction_product(enzymeml, ident, obj):
    model = enzymeml.get_model()
    reac = model.getElementBySId(_get_id(ident))
    if type(reac) is not sbml.Reaction:
        raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))
    __main_reaction_reactioncomponent_add(reac.createProduct, obj)
    return ident


def __main_reaction_reactioncomponent_add(func_create, obj):
    def write(oj):
        clazz = func_create()
        clazz.setSpecies(_get_id(oj["id"]))

        if type(clazz) is not sbml.ModifierSpeciesReference:
            if "constant" in oj:
                clazz.setConstant(oj["constant"])
            else:
                clazz.setConstant(True)

            if "stochiometry" in oj:
                clazz.setStoichiometry(oj["stochiometry"])

    if type(obj) is list:
        for o in obj:
            write(o)
    else:
        write(obj)


def __main_reaction_ec_code(enzymeml, ident, obj):
    model = enzymeml.get_model()
    element = model.getElementByMetaId(_get_id(ident, True))

    # TODO is version of vs is
    cvt = _create_bqbiol_cvt(sbml.BQB_IS_VERSION_OF)
    _add_to_cvt(cvt, obj)

    element.addCVTerm(cvt)

    return ident


def __main_reaction_conditions(enzymeml, ident, obj):
    model = enzymeml.get_model()
    # element = model.getElementBySId(_get_id(ident))
    # xmlnode = _read_annotation(element)

    reac = enzymeml.get_reaction_cond(_get_id(ident))
    if reac is None:
        reac = enzymeml.create_reaction_cond(_get_id(ident))

    # if xmlnode is not None:
    #     reac.from_xmlnode(xmlnode)

    if "ph" in obj:
        reac.set_ph(obj["ph"])
    if "temperature" in obj:
        reac.set_temperature(obj["temperature"][0], obj["temperature"][1])
    if "pressure" in obj:
        reac.set_pressure(obj["pressure"][0], obj["pressure"][1])
    if "shaking" in obj:
        reac.set_shaking_frequency(obj["shaking"][0], obj["shaking"][1])

    # __annotation_write(element, "reaction", reac.to_xml_string())

    return ident


def __main_reaction_replica(enzymeml, ident, obj):
    # model = enzymeml.get_model()
    # element = model.getElementBySId(_get_id(ident))
    # xmlnode = _read_annotation(element)

    reac = enzymeml.get_reaction_cond(_get_id(ident))
    if reac is None:
        reac = enzymeml.create_reaction_cond(_get_id(ident))

    # if xmlnode is not None:
    #     reac.from_xmlnode(xmlnode)

    if type(obj) is list:
        for r in obj:
            reac.add_replica(r)
    else:
        reac.add_replica(obj)

    # __annotation_write(element, "reaction", reac.to_xml_string())

    return ident


"""
def __main_reaction_data(model):
    lor = model.getListOfReactions()
    xmlnode = _read_annotation(lor)

    data = EnzymeMLData()
    if xmlnode is not None:
        data.from_xmlnode(xmlnode)


    return lor, data"""


def __main_reaction_data_format(enzymeml, ident, obj):
    # lor, data = __main_reaction_data(enzymeml.get_model())

    data = enzymeml.get_reaction_data()
    if data is None:
        data = enzymeml.create_reaction_data()

    f = data.listOfFormats.add_format(None, obj)

    ret = f.sid

    # __annotation_write(lor, "data", data.to_xml_string())
    return ret


def __main_reaction_data_file(enzymeml, ident, obj):
    # lor, data = __main_reaction_data(enzymeml.get_model())

    data = enzymeml.get_reaction_data()
    if data is None:
        data = enzymeml.create_reaction_data()

    f = data.listOfFiles.add_file(obj["file"], obj["format"])

    ret = f.sid

    # __annotation_write(lor, "data", data.to_xml_string())
    return ret


def __main_reaction_data_measure(enzymeml, ident, obj):
    # lor, data = __main_reaction_data(enzymeml.get_model())

    data = enzymeml.get_reaction_data()
    if data is None:
        data = enzymeml.create_reaction_data()

    m = data.listOfMeasurements.add_measurement(obj["name"], obj["file"], obj["start"], obj["stop"])

    ret = m.sid

    # __annotation_write(lor, "data", data.to_xml_string())
    return ret


#######################
# Model File Handling #
#######################
def __model_species(enzymeml, ident, obj):
    model = enzymeml.get_model()
    __init_species(model)
    global __species_ids

    sp_def = model.createSpecies()
    sp_def.setName(obj["name"])

    # ident = ("s%i" % __species_ids[model.enzymemlid], "META_SPECIES_%s" % __species_ids[model.enzymemlid])

    mid = _get_model_ident(model)
    ident = "s%i" % __species_ids[mid]

    sp_def.setId(ident)
    # sp_def.setMetaId(ident[1])

    if "type" in obj:
        sp_def.setSBOTerm(obj["type"])
    else:
        sp_def.setSBOTerm(ontology.SBO_INTERACTOR)

    if "constant" in obj:
        sp_def.setConstant(obj["constant"])

    __species_ids[mid] += 1
    return ident


def __model_reaction(enzymeml, ident, obj):
    model = enzymeml.get_model()
    __init_reactions(model)
    global __reactions_ids

    reac = model.createReaction()
    reac.setName(obj["name"])

    mid = _get_model_ident(model)
    ident = ("r%i" % __reactions_ids[mid],
             "META_REACTION_%s" % __reactions_ids[mid])

    reac.setId(ident[0])
    reac.setMetaId(ident[1])

    if "reversible" in obj:
        reac.setReversible(obj["reversible"])

    if "reactants" in obj:
        __main_reaction_reactioncomponent_add(reac.createReactant, obj["reactants"])

    if "modifier" in obj:
        __main_reaction_reactioncomponent_add(reac.createModifier, obj["modifier"])

    if "products" in obj:
        __main_reaction_reactioncomponent_add(reac.createProduct, obj["products"])

    if "kineticlaw" in obj:
        __model_reaction_kinetic_law(enzymeml, ident, obj["kineticlaw"])

    if "parameters" in obj:
        for param in obj["parameters"]:
            __model_reaction_parameters(enzymeml, ident, param)

    __reactions_ids[mid] += 1
    return ident


def __model_reaction_kinetic_law(enzymeml, ident, obj):
    model = enzymeml.get_model()
    reac = model.getElementBySId(_get_id(ident))
    if type(reac) is not sbml.Reaction:
        raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))

    if not reac.isSetKineticLaw():
        reac.createKineticLaw()

    kl = reac.getKineticLaw()

    formula = sbml.parseL3Formula(obj)
    kl.setMath(formula)

    return ident


def __model_reaction_parameters(enzymeml, ident, obj):
    model = enzymeml.get_model()
    reac = model.getElementBySId(_get_id(ident))
    if type(reac) is not sbml.Reaction:
        raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))

    if not reac.isSetKineticLaw():
        reac.createKineticLaw()

    kl = reac.getKineticLaw()

    lp = kl.createLocalParameter()
    lp.setName(obj["name"])
    lp.setValue(obj["value"])
    lp.setUnits(_get_id(obj["units"]))

    if "stdev" in obj:
        stdev = obj["stdev"]

        value = None
        unit = None
        if type(stdev) == tuple:
            if len(stdev) == 2:
                value = stdev[0]
                unit = _get_id(stdev[1])
            else:
                value = stdev[0]
        else:
            value = stdev

        distrib = lp.getPlugin("distrib")
        unc = distrib.createUncertainty()
        unc_para = unc.createUncertParameter()
        unc_para.setType("standardDeviation")
        unc_para.setValue(value)

        if unit is not None:
            unc_para.setUnits(unit)

    return ident


def __model_reaction_data(enzymeml, ident, obj):
    # model = enzymeml.get_model()
    # reac = model.getElementBySId(_get_id(ident))
    # if type(reac) is not sbml.Reaction:
    #     raise RuntimeError("No reaction element with SID '%s' was found." % _get_id(ident))

    # xmlnode = _read_annotation(reac)

    ud = enzymeml.get_used_data(_get_id(ident))
    if ud is None:
        ud = enzymeml.create_used_data(_get_id(ident))
    # if xmlnode is not None:
    #     ud.from_xmlnode(xmlnode)

    for reacsid in obj:
        if len(obj[reacsid]) == 0:
            ud.add_replica("#%s" % _get_id(reacsid), None)  # TODO hashtag is symbol for other file; needed?
        else:
            for replsid in obj[reacsid]:
                if type(replsid) is EnzymeMLReplica:
                    replsid = replsid.id
                ud.add_replica("#%s" % _get_id(reacsid), "#%s" % _get_id(replsid))

    # __annotation_write(reac, "modelReaction", ud.to_xml_string())

    return ident


"""
This is used to handle all MODEL_ keys
"""


def __model_add(enzymeml, ekey, ident, obj):
    return 3


_key_func_dict = {
    key.UNSPECIFIC_NOTE: __unspecific_note,

    key.MAIN_META_EXPERIMENT_NAME: __main_meta_expname,
    key.MAIN_META_CREATOR: __main_meta_name,
    key.MAIN_META_DATES_CREATE: __main_meta_date_create,
    key.MAIN_META_DATES_MODIFY: __main_meta_date_modify,
    key.MAIN_META_MODEL_IS: None,
    key.MAIN_META_MODEL_DESCRIBED: None,
    key.MAIN_META_BIOL_DESCRIBED: None,
    key.MAIN_UNIT: __main_unit,
    key.MAIN_UNIT_IS: __main_unit_is,
    key.MAIN_COMPARTMENT: __main_compartment,
    key.MAIN_COMPARTMENT_IS: __main_compartment_is,
    key.MAIN_SPECIES: __main_species,
    key.MAIN_SPECIES_PROTEIN: __main_species_protein,
    key.MAIN_SPECIES_SPECIES: __main_species_simple,
    key.MAIN_REACTION: __main_reaction,
    key.MAIN_REACTION_REACTANTS: __main_reaction_reactant,
    key.MAIN_REACTION_MODIFIERS: __main_reaction_modifier,
    key.MAIN_REACTION_PRODUCTS: __main_reaction_product,
    key.MAIN_REACTION_EC_CODE: __main_reaction_ec_code,
    key.MAIN_REACTION_CONDITION: __main_reaction_conditions,
    key.MAIN_REACTION_REPLICAS: __main_reaction_replica,
    key.MAIN_DATA_FORMAT: __main_reaction_data_format,
    key.MAIN_DATA_FILE: __main_reaction_data_file,
    key.MAIN_DATA_MEASUREMENTS: __main_reaction_data_measure,

    key.MODEL_META_EXPERIMENT_NAME: __main_meta_expname,
    key.MODEL_META_CREATOR: __main_meta_name,
    key.MODEL_META_DATES_CREATE: __main_meta_date_create,
    key.MODEL_META_DATES_MODIFY: __main_meta_date_modify,
    key.MODEL_META_MODEL_IS: None,
    key.MODEL_META_MODEL_DESCRIBED: None,
    key.MODEL_SPECIES: __model_species,
    key.MODEL_REACTION: __model_reaction,
    key.MODEL_REACTION_MODIFIERS: __main_reaction_modifier,
    key.MODEL_REACTION_REACTANTS: __main_reaction_reactant,
    key.MODEL_REACTION_PRODUCTS: __main_reaction_product,
    key.MODEL_REACTION_KINETIC_LAW: __model_reaction_kinetic_law,
    key.MODEL_REACTION_PARAMETERS: __model_reaction_parameters,
    key.MODEL_REACTION_DATA: __model_reaction_data
}
