import enzymeml.enzymeml as enzml
import libsbml as sbml
import pandas as pd

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


class EnzymeMLwriter:
    def __init__(self, parameters, name):
        self.parameters = parameters
        self.name = name
    
    def write (self):

        p = self.parameters

        xp = enzml.EnzymeML(self.name)
        xp.add_creator(
            p["last_name"],
            p["given_name"], 
            p["Email_address"],
            p["Instituion"])

        xp.add(
            enzml.key.MAIN_META_CREATOR, 
            {"family":p["last_name"], 
             "given":p["given_name"],
             "email":p["Email_address"]}
             )
        
        comp = xp.add(
            enzml.key.MAIN_COMPARTMENT,
            {"size": float(p["volume"]),
            "units":get_unit(xp, p["volume_unit"]),
            "constant": True,
            "name": p["Reaction_vessel"]}
            )

        spenz = xp.add(
            enzml.key.MAIN_SPECIES,
            {"name": p["Enzyme_Name"],
            "compartment":comp,
            "type":enzml.ontology.SBO_ENZYME,
            "constant":True,
            "init_conc":float(p["Enzyme_concentration"]),
            "units":get_unit(xp, "mol/l")}
        )
        xp.add(enzml.key.MAIN_SPECIES_PROTEIN,
            {"sequence": p["AA_sequence"]}, spenz)

        substrates = []
        products = []
        cofactors = []

        species = dict()

        for i, j, k, l in zip(p["Substance_"], p["Concentration_Substrate_"], p["substance_unit_"], p["select_substrate_"]):
            
            obj = {"name":i,
                "compartment": comp,
                "constant":False,
                "init_conc": float(j),
                "units":k}

            li = None
            if l == "Product":
                obj["type"]= enzml.ontology.SBO_PRODUCT
                li = products
            elif l == "Substrate":
                obj["type"]= enzml.ontology.SBO_SUBSTRATE
                li = substrates
            elif l == "Cofactor":
                li = cofactors
                obj["type"]= enzml.ontology.SBO_INTERACTOR
            else:
                print("%s ist unbekannt" % l)
            
            sid = xp.add(
                enzml.key.MAIN_SPECIES,
                obj)
            species[i] = sid

            li += [
                { "id":sid, 
                "stochiometry":1,
                "constant": l == "Cofactor"}
                ]
        cofactors += [
                { "id":spenz, 
                "stochiometry":1,
                "constant": True }
                ]

        reac = xp.add(
            enzml.key.MAIN_REACTION,
            {
                "name":p["Reaction_name"],
                "reversible":True,
                "reactants": substrates,
                "products": products,
                "modifier": cofactors
            }
            )

        xp.add(
            enzml.key.MAIN_REACTION_CONDITION,
            {
                "ph":float(p["pH"]), 
                "temperature":(float(p["temperatur"]), "kelvin"),          
                }, reac
            )
        


        data = pd.read_excel(r"C:\Users\Malzacher\Desktop\Beispiel.xlsx")
        print(data)

        form = enzml.EnzymeMLFormat()
       
        xp.add(enzml.key.MAIN_DATA_FORMAT, form)

        csv = enzml.EnzymeMLCSV( form, name='Data' )
        xp.add_csv( csv )
        csv_sid = xp.add(enzml.key.MAIN_DATA_FILE, {"file": csv.location, "format": form.sid})

        # adding time column
        form.add_column(enzml.create_column(enzml.COLUMN_TYPE_TIME, "seconds")) # TODO load from file

        csv.add_column( data["x_parameter"].values.tolist() ) # TODO add time column

        # adding concentration columns
        #sp_sid = species["pyruvate"] # TODO load from file
        sp_sid = "pyruvate"


        measure = xp.add(enzml.key.MAIN_DATA_MEASUREMENTS,
                {
                    "file": csv_sid, "start": 0, "stop": -1, "name": "pyruvate measurement"
                }
            )

        for i in range(1, data.shape[1]):
            data_col = data["rep_%i" % (i)].values.tolist() # load
            col = enzml.create_column(
                enzml.COLUMN_TYPE_CONCENTRATION, sp_sid, get_unit(xp, "mol/l") # TODO load from file
            )
            form.add_column(col)
            csv.add_column(data_col)

            repl_enzml = enzml.EnzymeMLReplica(measure, col.replica)
            xp.add(enzml.key.MAIN_REACTION_REPLICAS, repl_enzml, reac)

        xp.create_archive()


        

        

            
        




            
