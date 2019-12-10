import enzymeml.enzymeml as enzml
import libsbml as sbml



_unit_manager = dict()
def get_unit(enz, name):
    global _unit_manager

    if enz.id not in _unit_manager:
        _unit_manager[enz.id] = dict()

    units = _unit_manager[enz.id]

    if name not in units:
        if name == "%":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "percent",
                                               "units": [{"kind": sbml.UNIT_KIND_DIMENSIONLESS, "scale": -2}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000187", un)
            

            units["%"] = un
        elif name == "ms":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "millisecond",
                                               "units": [{"kind": sbml.UNIT_KIND_SECOND, "scale": -3}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000028", un)
           

            units["ms"] = un
        elif name == "s":
            units["s"] = sbml.UNIT_KIND_SECOND
        elif name == "min":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "minute",
                                               "units": [{"kind": sbml.UNIT_KIND_SECOND, "multiplier": 60}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000031", un)
            

            units["min"] = un
        elif name == "h":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "hour",
                                               "units": [{"kind": sbml.UNIT_KIND_SECOND, "multiplier": 3600}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000032", un)
            

            units["h"] = un
        elif name == "nmol/l":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "nmol/l",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -9},
                                                         {"kind": sbml.UNIT_KIND_LITRE, "exponent": -1}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000062", un)
           

            units["nmol/l"] = un
        elif name == "umol/l":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "umol/l",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -6},
                                                         {"kind": sbml.UNIT_KIND_LITRE, "exponent": -1}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000064", un)
            

            units["umol/l"] = un
        elif name == "mmol/l":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "mmol/l",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -3},
                                                         {"kind": sbml.UNIT_KIND_LITRE, "exponent": -1}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000065", un)
           

            units["mmol/l"] = un
        elif name == "mol/l":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "mol/l",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE},
                                                         {"kind": sbml.UNIT_KIND_LITRE, "exponent": -1}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000062", un)
           

            units["mol/l"] = un
        elif name == "nmol":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "nmol",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -9}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000041", un)
           

            units["nmol"] = un
        elif name == "umol":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "umol",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -6}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000039", un)
           

            units["umol"] = un
        elif name == "mmol":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "mmol",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE, "scale": -3}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000040", un)
        

            units["mmol"] = un
        elif name == "mol":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "mol",
                                               "units": [{"kind": sbml.UNIT_KIND_MOLE}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/UO:0000013", un)
           

            units["mol"] = un
        elif name == "rpm":
            un = enz.add(enzml.key.MAIN_UNIT, {"name": "revolution/min",
                                               "units": [{"kind": sbml.UNIT_KIND_DIMENSIONLESS},
                                                         {"kind": sbml.UNIT_KIND_SECOND, "exponent": -1,
                                                          "multiplier:": 60}]
                                               })
            enz.add(enzml.key.MAIN_UNIT_IS, "https://identifiers.org/NCIT:C70469", un)

            units["rpm"] = un
        else:
            print("Unknown unit %s found. Illegal id is used." % name)
            units[name] = name

    return units[name]
