import enzymeml.enzymeml as enzml
import libsbml as sbml
import pandas as pd 
import unit_manager as unit_manager
from datetime import date
import os


class EnzymeMLwriter:
    def __init__(self, parameters, name, filename):
        self.parameters = parameters
        self.name = name 
        self.filename = filename
        #print(self.parameters)

    def write(self):
        p = self.parameters # Shortcut!
        print(p)
        print("jetzt kommen dir Parameter")
        print(self.parameters)
        print(p["last_name"])
        today = date.today().strftime("%Y %m %d %H,%M,%S")
        print(today)
        
        
        experiment = enzml.EnzymeML(today + p['Reaction_name']+"_" + p['last_name']) # Erstellt eine Neue XML Datei
        
        experiment.add_creator( 
            p["last_name"],
            p["given_name"],
            p["email-address"],
            p["Instituion"]
        )

        experiment.add(
            enzml.key.MAIN_META_CREATOR,
            {
            "family":p['last_name'],
            "given":p['given_name'],
            "email":p['email-address']
            })

        compartment = experiment.add(
            enzml.key.MAIN_COMPARTMENT,
            {
            "size": float(p['Volume']),
            "units":unit_manager.get_unit(experiment, p['volume_unit']),
            "constant": True,
            "name": p['Reaction_vessel']
            })

        Enzyme = experiment.add(
            enzml.key.MAIN_SPECIES,
            {
                "name":p['Enzyme_Name'],
                "compartment":compartment,
                "type":enzml.ontology.SBO_ENZYME,
                "constant":True,
                "init_conc":float(p['Enzyme_concentration']),
                "units":unit_manager.get_unit(experiment, "%") # TODO load from dict
            })

        experiment.add(enzml.key.MAIN_SPECIES_PROTEIN,
            {
                "sequence": p['AA_sequence']}, 
                Enzyme 
             )

        substrates = []
        products = []
        cofactors = []
        species = dict()

        for i, j, k, l in zip(p['Reactant_name'], p['concentration_value'], p['unit'], p['reactant_kind']):
            
            obj = {"name":i,
                "compartment": compartment,
                "constant":False,
                "init_conc": float(j),
                "units":k}

            li = []
            if l == "Product":
                obj["type"]= enzml.ontology.SBO_PRODUCT
                li = products
            elif l == "Substrate":
                obj["type"]= enzml.ontology.SBO_SUBSTRATE
                li = substrates
            elif l == "Cofactor":
                li = cofactors
                obj["type"]= enzml.ontology.SBO_INTERACTOR
            elif l == "Additive":
                li = cofactors
                obj["type"]= enzml.ontology.SBO_INTERACTOR
            else:
                print("%s ist unbekannt" % l)
            
            sid = experiment.add(
                enzml.key.MAIN_SPECIES,
                obj)
            species[i] = sid

            li += [
                { "id":sid, 
                "stochiometry":1,
                "constant": l == "cofactor"}
                ]
        cofactors += [
                { "id":Enzyme, 
                "stochiometry":1,
                "constant": True }
                ]

        reac = experiment.add(
            enzml.key.MAIN_REACTION,
            {
                "name":p['Reaction_name'],
                "reversible":True,
                "reactants": substrates,
                "products": products,
                "modifier": cofactors
            }
            )

        experiment.add(
            enzml.key.MAIN_REACTION_CONDITION,
            {
                "ph":float(p["pH"]), 
                "temperature":(float(p['Temperatur']), "kelvin"),          
                }, reac
            )

        data = pd.read_excel(self.filename)
        print(data)

        form = enzml.EnzymeMLFormat()
       
        experiment.add(enzml.key.MAIN_DATA_FORMAT, form)

        csv = enzml.EnzymeMLCSV( form, name='Data' )
        experiment.add_csv( csv )
        csv_sid = experiment.add(enzml.key.MAIN_DATA_FILE, {"file": csv.location, "format": form.sid})

        # adding time column
        form.add_column(enzml.create_column(enzml.COLUMN_TYPE_TIME, "seconds")) # TODO load from file

        csv.add_column( data["x_parameter"].values.tolist() ) # TODO add time column

        # adding concentration columns
        #sp_sid = species["pyruvate"] # TODO load from file
        sp_sid = "pyruvate"


        measure = experiment.add(enzml.key.MAIN_DATA_MEASUREMENTS,
                {
                    "file": csv_sid, "start": 0, "stop": -1, "name": "pyruvate measurement"
                }
            )

        for i in range(1, data.shape[1]):
            data_col = data["rep_%i" % (i)].values.tolist() # load
            col = enzml.create_column(
                enzml.COLUMN_TYPE_CONCENTRATION, sp_sid, unit_manager.get_unit(experiment, "mol/l") # TODO load from file
            )
            form.add_column(col)
            csv.add_column(data_col)

            repl_enzml = enzml.EnzymeMLReplica(measure, col.replica)
            experiment.add(enzml.key.MAIN_REACTION_REPLICAS, repl_enzml, reac)

        experiment.create_archive()
        filename = today + p['Reaction_name']+"_" + p['last_name']+".omex"
        os.rename(filename, "C:/enzymeML/"+filename)

    





